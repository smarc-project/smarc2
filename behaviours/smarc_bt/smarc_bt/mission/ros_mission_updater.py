#!/usr/bin/python3

import os, json

from rosidl_runtime_py.set_message import set_message_fields
from rosidl_runtime_py.convert import message_to_ordereddict

from rclpy.node import Node
from py_trees.blackboard import Blackboard

from smarc_mission_msgs.msg import BTCommand, GotoWaypoint, MissionControl
from smarc_mission_msgs.msg import Topics as MissionTopics


from .ros_utm_lat_lon_converter_caller import ROSUTMLatLonConverterCaller
from .ros_dubins_planner_caller import ROSDubinsPlannerCaller

from .i_bb_mission_updater import IBBMissionUpdater
from .ros_mission_plan import ROSMissionPlan
from .ros_waypoint import SMaRCWP
from ..bt.bb_keys import BBKeys


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
        
                
        self._ll_converter = ROSUTMLatLonConverterCaller(node)
        self._dubins_planner = ROSDubinsPlannerCaller(node)
        

    def _mission_control_cb(self, msg:MissionControl):
        self._latest_mission_control_msg = msg


    def _get_mission_plan(self) -> ROSMissionPlan:
        mission_plan = self._bb.get(BBKeys.MISSION_PLAN)
        if mission_plan is None:
            self._log("No mission plan to modify!")
            self._latest_mission_control_msg = None
            return None

        return mission_plan


    def tick(self):
        """
        Handle the mission control message synchronously with a BT so that the input the the BT
        can not change _during_ its tick.
        """
        # see if there is a plan to set from before
        self._try_set_plan()
        self._try_set_dubins_plan()

        # Process the last mission control msg we got
        # and then set it to None
        msg = self._latest_mission_control_msg
        if msg is None: return

        elif msg.command == MissionControl.CMD_IS_FEEDBACK:
            self._latest_mission_control_msg = None
            return

        elif msg.command == MissionControl.CMD_SET_PLAN:
            self._log("SET PLAN")
            msg = self._save_load_plan(msg)
            if msg is None:
                self._log("SET PLAN failed")
            else:
                self._ll_converter.call(msg)
            
        elif msg.command == MissionControl.CMD_REQUEST_FEEDBACK:
            self._log("REQUEST FEEDBACK not implemented")
            self._latest_mission_control_msg = None
            return

        else:
            # following commands all rely on there being a mission plan
            mission_plan = self._get_mission_plan()
            if mission_plan is None:
                self._latest_mission_control_msg = None
                return

            if msg.command == MissionControl.CMD_EMERGENCY:
                mission_plan.emergency()

            elif msg.command == MissionControl.CMD_START:
                mission_plan.start()

            elif msg.command == MissionControl.CMD_PAUSE:
                mission_plan.pause()

            elif msg.command == MissionControl.CMD_STOP:
                mission_plan.stop() 

            else:
                self._log(f"Unknown mission control command: {msg.command}")
                self._latest_mission_control_msg = None
                return
        
        self._latest_mission_control_msg = None


    def _log(self, s:str):
        self._node.get_logger().info(s)

    def _save_mission(self, msg):
        if "TEST--" in msg.name:
            self._log("Test mission, not saving")
            return

        folder = self._bb.get(BBKeys.MISSION_PLAN_STORAGE)
        path = os.path.expanduser(folder)
        if not os.path.exists(path):
            os.makedirs(path)

        filename = os.path.join(path, f"{msg.name}.json")
        with open(filename, 'w') as f:
            oredered_dict = message_to_ordereddict(msg)
            j = json.dumps(oredered_dict)
            f.write(j)
            self._log(f"Wrote mission {filename}")

    def _load_mission(self, msg):
        folder = self._bb.get(BBKeys.MISSION_PLAN_STORAGE)
        path = os.path.expanduser(folder)
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
        if not self._ll_converter.done: return

        msg = self._ll_converter.get_result()
        if msg is None: return

        self._ll_converter.reset()
        waypoints = [SMaRCWP(wp) for wp in msg.waypoints]
        new_plan = ROSMissionPlan(self._node, msg.name, waypoints)

        self._bb.set(BBKeys.MISSION_PLAN, new_plan)
        self._log(f"New mission {msg.name} set!")


    def _try_set_dubins_plan(self):
        if not self._dubins_planner.done: return
        
        new_plan = self._dubins_planner.get_result()
        if new_plan is None: return

        self._bb.set(BBKeys.MISSION_PLAN, new_plan)
        self._log(f"Mission {new_plan.name} has been dubinifed!")



    def plan_dubins(self):
        mplan = self._get_mission_plan()
        if mplan is None: return

        turning_radius = self._bb.get(BBKeys.DUBINS_TURNING_RADIUS)
        step_size = self._bb.get(BBKeys.DUBINS_STEP_SIZE)
        self._dubins_planner.call(mplan, turning_radius, step_size)




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
