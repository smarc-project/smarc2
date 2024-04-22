#!/usr/bin/python3

import os, json

from rosidl_runtime_py.set_message import set_message_fields
from rosidl_runtime_py.convert import message_to_ordereddict

from rclpy.node import Node
from py_trees.blackboard import Blackboard

from smarc_mission_msgs.msg import BTCommand, GotoWaypoint, MissionControl
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_mission_msgs.srv import UTMLatLon
from geographic_msgs.msg import GeoPoint


from .i_bb_mission_updater import IBBMissionUpdater
from .ros_mission_plan import ROSMissionPlan
from .ros_waypoint import SMaRCWP
from ..bt.bb_keys import BBKeys


class LatLonUTMConverter:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._ll_utm_converter = self._node.create_client(UTMLatLon,
                                                          MissionTopics.UTM_LATLON_CONVERSION_SERVICE)
        
        self.reset()

    def _log(self, s:str):
        self._node.get_logger().info(s)
        
    def call(self, msg: MissionControl) -> None:
        self._converted = False
        self._mission_control_msg = msg

        converter_msg = UTMLatLon.Request()
        converter_msg.lat_lon_points = []
        for wp in msg.waypoints:
            gp = GeoPoint()
            gp.latitude = wp.lat
            gp.longitude = wp.lon
            converter_msg.lat_lon_points.append(gp)

        self._log("Calling service")
        self._future = self._ll_utm_converter.call_async(converter_msg)
        self._future.add_done_callback(self._done_cb)

    def _done_cb(self, future) -> None:
        self._log("Done cb")
        result = future.result()
        self._log("Got result")

        for wp, utm_point in zip(self._mission_control_msg.waypoints, result.utm_points):
            wp.pose.pose.position.x = utm_point.point.x
            wp.pose.pose.position.y = utm_point.point.y

        self._converted = True


    def reset(self):
        self._mission_control_msg = None
        self._future = None
        self._converted = False


    @property
    def done(self) -> bool:
        return self._converted
    

    def get_result(self) -> MissionControl:
        if self.done:
            return self._mission_control_msg
        
        return None



class ROSMissionUpdater(IBBMissionUpdater):
    def __init__(self,
                 node: Node) -> None:
        """
        Creates/deletes/updates a mission plan in the blackboard
        with info from ros topics/services.
        """
        super().__init__()

        self._node = node
        self._bb = Blackboard()

        self._latest_mission_control_msg = None
        self._mission_control_sub = node.create_subscription(MissionControl,
                                                            MissionTopics.MISSION_CONTROL_TOPIC,
                                                            self._mission_control_cb,
                                                            10)
        
        self._mission_control_pub = node.create_publisher(MissionControl,
                                                          MissionTopics.MISSION_CONTROL_TOPIC,
                                                          10)
        
        self._mission_storage_folder = self._node.declare_parameter("mission_storage_folder", "~/MissionPlans/").value
        
        self._ll_converter = LatLonUTMConverter(node)
        

    def _mission_control_cb(self, msg:MissionControl):
        self._latest_mission_control_msg = msg


    def tick(self):
        """
        # TODO https://github.com/smarc-project/smarc_missions/blob/b1bf53cea3855c28f9a2c004ef2d250f02885afe/smarc_bt/src/nodered_handler.py#L251
        Handle the mission control message synchronously with a BT so that the input the the BT
        can not change _during_ its tick.
        """
        # see if there is a plan to set from before
        self._try_set_plan()

        # Process the last mission control msg we got
        # and then set it to None
        msg = self._latest_mission_control_msg
        if msg is None: return

        if msg.command == MissionControl.CMD_IS_FEEDBACK: return

        if msg.command == MissionControl.CMD_SET_PLAN:
            self._log("SET PLAN")
            msg = self._save_load_plan(msg)
            if msg is None:
                self._log("SET PLAN failed")
            else:
                self._ll_converter.call(msg)
            

        if msg.command == MissionControl.CMD_REQUEST_FEEDBACK:
            self._log("REQUEST FEEDBACK not implemented")
        

        # following commands all rely on there being a mission plan
        mission_plan = self._bb.get(BBKeys.MISSION_PLAN)
        if mission_plan is None:
            self._log("No mission plan to change the state of.")
            self._latest_mission_control_msg = None
            return
        

        if msg.command == MissionControl.CMD_EMERGENCY:
            mission_plan.emergency()

        if msg.command == MissionControl.CMD_START:
            mission_plan.start()

        if msg.command == MissionControl.CMD_PAUSE:
            mission_plan.pause()

        if msg.command == MissionControl.CMD_STOP:
            mission_plan.stop()
        
        self._latest_mission_control_msg = None



    def _log(self, s:str):
        self._node.get_logger().info(s)

    def _save_mission(self, msg):
        if "TEST--" in msg.name:
            self._log("Test mission, not saving")
            return

        path = os.path.expanduser(self._mission_storage_folder)
        if not os.path.exists(path):
            os.makedirs(path)

        filename = os.path.join(path, f"{msg.name}.json")
        with open(filename, 'w') as f:
            oredered_dict = message_to_ordereddict(msg)
            j = json.dumps(oredered_dict)
            f.write(j)
            self._log(f"Wrote mission {filename}")

    def _load_mission(self, msg):
        path = os.path.expanduser(self._mission_storage_folder)
        filename = os.path.join(path, f"{msg.name}.json")
        with open(filename, 'r') as f:
            j = f.read()
            mc = MissionControl()
            set_message_fields(mc, j)

        self._log("Loaded mission {msg.name} from file!")
        return mc

    def _save_load_plan(self, msg: MissionControl) -> MissionControl:
        """
        The message might contain a proper complete plan
        or just the hash of a plan.
        If its a proper mission:
            - Check if a saved mission with the same name exists
                - over-write it if it exists
                    - Save the msg object directly since its already serialized and such, with msg.name as its filename
            - If no same-name saved mission exists, save this one with its hash
        If it is NOT a proper mission = no waypoints then we need to check if we have a saved
        mission with the same hash. If so, we load it, if not, do nothing.
            - Check the msg.hash and msg.name fields, everything else can be empty for this
            - Purpose: Super-low-bandwidth mission selection
        """
        if(msg.name != "" and msg.hash != "" and len(msg.waypoints) == 0):
            # try to load a mission from file
            try:
                loaded_msg = self._load_mission(msg)
            except:
                self._log(f"Could not load mission with name: {msg.name}")
                return None

            # okay, got a mission message, but does it have the same hash
            # as the request?
            if loaded_msg.hash == msg.hash:
                msg = loaded_msg
            else:
                self._log(f"A plan with this name exists, but has a different hash: {msg.name}")
                return None

        # we either got a proper full mission message
        # or the loaded mission message is good to use
        self._save_mission(msg)

        return msg
    
    def _try_set_plan(self):
        if not self._ll_converter.done: 
            return

        msg = self._ll_converter.get_result()
        if msg is not None:
            self._ll_converter.reset()
            waypoints = [SMaRCWP(wp) for wp in msg.waypoints]
            new_plan = ROSMissionPlan(self._node, msg.name, waypoints)

            self._bb.set(BBKeys.MISSION_PLAN, new_plan)
            self._log(f"New mission {msg.name} set!")


def send_test_mission_control():
    import rclpy, sys, time

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("send_test_mission")

    
    pub = node.create_publisher(MissionControl,
                                MissionTopics.MISSION_CONTROL_TOPIC,
                                10)

    def interact():    
        nonlocal pub
        mc = MissionControl()
        mc.hash = "testhash"
        mc.name = "testplan"

        choice = input("Choose: new, start, pause, stop, emergency:\n")
        if choice == "new":
            mc.command = MissionControl.CMD_SET_PLAN
            
            wp1 = GotoWaypoint()
            wp1.name = "wp1"
            wp1.lat = 58.821496
            wp1.lon = 17.619285

            wp2 = GotoWaypoint()
            wp1.name = "wp2"
            wp1.lat = 58.820936
            wp1.lon = 17.618728

            mc.waypoints = [wp1, wp2]
        
        if choice == "start":
            mc.command = MissionControl.CMD_START
        if choice == "pause":
            mc.command = MissionControl.CMD_PAUSE
        if choice == "stop":
            mc.command = MissionControl.CMD_STOP
        if choice == "emergency":
            mc.command = MissionControl.CMD_EMERGENCY
                   

        pub.publish(mc)
        print(f"Published plan\n{mc}")

    node.create_timer(1, interact)
    rclpy.spin(node)
