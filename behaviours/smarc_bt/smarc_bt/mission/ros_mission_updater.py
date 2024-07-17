#!/usr/bin/python3

import os, json
import numpy as np

from rclpy.node import Node
from rosidl_runtime_py.set_message import set_message_fields
from rosidl_runtime_py.convert import message_to_ordereddict

from py_trees.blackboard import Blackboard

from geometry_msgs.msg import Pose2D, PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from std_msgs.msg import Empty

from smarc_mission_msgs.msg import GotoWaypoint, MissionControl
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_mission_msgs.srv import DubinsPlan, UTMLatLon

from smarc_msgs.msg import Topics as SmarcTopics


from dubins_planner.dubins_planner_node import DubinsPlannerService
from utm_latlon_converter.converter_service_node import GeoConverterService

from .i_bb_mission_updater import IBBMissionUpdater
from .ros_mission_plan import ROSMissionPlan
from .ros_waypoint import ROSWP
from ..bt.bb_keys import BBKeys


# Because the dubins planner uses X=right, Y=up, CCW angles
# while mission plans have X=East, Y=North, and compass heading where 0=north 90=east
def _heading_to_yaw(a):
    return (90-a)%360
def _yaw_to_heading(b):
    return (-(b-90))%360
def _directed_angle(v1,v2):
    """
    returns angle in a directed fashion, from v1 to v2, v1+angle = v2
    negative value means v2 is closer if v1 rotates cw
    """
    x1,x2 = v1[0],v2[0]
    y1,y2 = v1[1],v2[1]

    dot = x1*x2 + y1*y2      # dot product
    det = x1*y2 - y1*x2      # determinant
    angle_diff = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)

    return angle_diff


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

        self._abort_pub = node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)
        self._latest_mission_control_msg = None
        self._mission_control_sub = node.create_subscription(MissionControl,
                                                            MissionTopics.MISSION_CONTROL_TOPIC,
                                                            self._mission_control_cb,
                                                            10)
 
        

    def _mission_control_cb(self, msg:MissionControl):
        self._latest_mission_control_msg = msg

    def __get_mission_plan(self) -> ROSMissionPlan:
        mission_plan = self._bb.get(BBKeys.MISSION_PLAN)
        if mission_plan is None:
            self._log("No mission plan to modify!")
            self._latest_mission_control_msg = None
            return None

        return mission_plan

    def __save_mission(self, msg):
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

    def __load_mission(self, msg):
        folder = self._bb.get(BBKeys.MISSION_PLAN_STORAGE)
        path = os.path.expanduser(folder)
        filename = os.path.join(path, f"{msg.name}.json")
        with open(filename, 'r') as f:
            j = f.read()
            mc = MissionControl()
            set_message_fields(mc, j)

        self._log("Loaded mission {msg.name} from file!")
        return mc


    def tick(self):
        """
        Handle the mission control message synchronously with a BT so that the input to the BT
        can not change _during_ its tick.
        """
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
                self._log("SET PLAN failed due to save/load function.")
            else:
                self._set_plan(msg)

        elif msg.command == MissionControl.CMD_REQUEST_FEEDBACK:
            self._log("REQUEST FEEDBACK not implemented")
            self._latest_mission_control_msg = None
            return

        else:
            # following commands all rely on there being a mission plan
            mission_plan = self.__get_mission_plan()
            
            if msg.command == MissionControl.CMD_EMERGENCY:
                if mission_plan is not None: mission_plan.emergency()
                self._abort_pub.publish(Empty())
                self._log("Mission Updater: ABORTED")

            if mission_plan is None:
                self._latest_mission_control_msg = None
                return

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
                loaded_msg = self.__load_mission(msg)
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
        self.__save_mission(msg)
        return msg

    def _set_plan(self, mc: MissionControl):
        request = UTMLatLon.Request()
        request.lat_lon_points = []
        for wp in mc.waypoints:
            gp = GeoPoint()
            gp.latitude = wp.lat
            gp.longitude = wp.lon
            request.lat_lon_points.append(gp)

        response = GeoConverterService.convert(request, UTMLatLon.Response())

        for wp, utm_point in zip(mc.waypoints, response.utm_points):
            wp.pose.pose.position.x = utm_point.point.x
            wp.pose.pose.position.y = utm_point.point.y
            wp.pose.header.frame_id = utm_point.header.frame_id

        wps = [ROSWP(wp) for wp in mc.waypoints]
        new_plan = ROSMissionPlan(self._node, mc.name, mc.hash, mc.timeout, wps)
        self._bb.set(BBKeys.MISSION_PLAN, new_plan)
        self._log(f"New mission {new_plan._plan_id}({new_plan._hash}) set!")

    def plan_dubins(self, turning_radius:float = None, step_size:float = None):
        mplan = self.__get_mission_plan()
        if mplan is None: return

        if turning_radius is None:
            turning_radius = self._bb.get(BBKeys.DUBINS_TURNING_RADIUS)

        if step_size is None:
            step_size = self._bb.get(BBKeys.DUBINS_STEP_SIZE)

        request = DubinsPlan.Request()
        request.step = float(step_size)
        request.turning_radius = float(turning_radius)
        request.waypoints = []

        planar_wps = mplan.planar_wps
        for i,wp in enumerate(planar_wps):
            # planar wps is [x,y,heading]
            # we want [x,y,yaw]
            p2d = Pose2D()
            p2d.x = wp[0]
            p2d.y = wp[1]
            # The WP might not have a heading defined
            # in this case we want the heading to be towards
            # the next WP in the plan for it.
            # for a plan: A B C. if none of them have a specificed
            # arrival heading, A should head towards B, B to C and C from B
            if wp[2] is not None:
                p2d.theta = _heading_to_yaw(wp[2])
            else:
                # if this is the last WP, heading should be
                # "from the previous WP"
                if i == len(planar_wps)-1:
                    prev_wp = planar_wps[i-1]
                    a = _directed_angle((1,0), (wp[0]-prev_wp[0], wp[1]-prev_wp[1]))
                    p2d.theta = np.rad2deg(a)
                else:
                    next_wp = planar_wps[i+1]
                    a = _directed_angle((1,0), (next_wp[0]-wp[0], next_wp[1]-wp[1]))
                    p2d.theta = np.rad2deg(a)
            request.waypoints.append(p2d)

        response = DubinsPlannerService.dubins_cb(request, DubinsPlan.Response())

        # the interpolated waypoints
        # these include the original wps
        dubins_wps = response.waypoints
        # which of the waypoints are "original"
        # we can do index-mapping from these
        # to the original mission plan object
        # to recover all the details of the originals
        # that the dubins planner didnt want
        og_indices = response.original_wp_indices

        # we want to create SMaRCWPs using
        # GotoWaypoint objects.
        # The interpolated WPs need depth/alti etc. fields
        # as well. So we copy them from the original wps of the mission.
        # Each interpolated WP should have the properties of the
        # original WP that it is going TOWARDS.
        # if A 1 2 3 B 4 5 6 C and ABC are original WPs and 123.. are interpolated
        # then 1,2,3 should have B's properties, 4,5,6 should have C's.
        # we have a list for ABC in the original mplan
        # and we have a list for A123B456C in the dubins plan
        # and we have a list for [0, 4, 8] to identify ABC' in A123B456C
        # this is all easier going backwards, then we simply pop from the 
        # OG wps as we see their index in the index list and assign wps its values
        # until we see the next og index
        og_wp_dict = None
        wp_list = []
        for i in reversed(range(len(dubins_wps))):
            if i == og_indices[-1]:
                og_indices.pop()
                og_wp = mplan._waypoints.pop().goto_wp
                og_wp_dict = message_to_ordereddict(og_wp)

            # first, create a clone of the original wp
            # planning only changes the x,y,heading fields
            # so we can over-write those afterwards
            new_goto_wp = GotoWaypoint()
            set_message_fields(new_goto_wp, og_wp_dict)
            # now we can over-write the x,y,heading of this
            # new interpolated wp from its own
            new_goto_wp.use_heading = True
            new_goto_wp.pose.pose.position.x = dubins_wps[i].x
            new_goto_wp.pose.pose.position.y = dubins_wps[i].y
            new_goto_wp.arrival_heading = _yaw_to_heading(dubins_wps[i].theta)
            new_goto_wp.name = f"({i})_{new_goto_wp.name}"
            wp_list.append(new_goto_wp)

        # since we went backwards when filling this...
        wp_list.reverse()

        # and now, for the final act, we want latlon in each and every WP in the plan!
        request = UTMLatLon.Request()
        request.utm_points = []
        for goto_wp in wp_list:
            ps = PointStamped()
            ps.point.x = goto_wp.pose.pose.position.x
            ps.point.y = goto_wp.pose.pose.position.y
            ps.header.frame_id = goto_wp.pose.header.frame_id
            request.utm_points.append(ps)

        response = GeoConverterService.convert(request, UTMLatLon.Response())
        for goto_wp, latlon_point in zip(wp_list, response.lat_lon_points):
            goto_wp.lat = latlon_point.latitude
            goto_wp.lon = latlon_point.longitude

        # and FINALLY, we can make a  mission out of these
        wp_list = [ROSWP(wp) for wp in wp_list]
        new_plan = ROSMissionPlan(self._node,
                                  mplan._plan_id,
                                  mplan._hash,
                                  mplan._timeout,
                                  wp_list)

        self._bb.set(BBKeys.MISSION_PLAN, new_plan)
        self._log(f"Mission {new_plan._plan_id}({new_plan._hash}) dubinsified!")




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
        mc.timeout = 99999999

        choice = input("Choose: new, start, pause, stop, emergency:\n")
        if choice == "new":
            mc.command = MissionControl.CMD_SET_PLAN

            wp1 = GotoWaypoint()
            wp1.name = "wp1"
            wp1.lat = 58.821496
            wp1.lon = 17.619285

            waypoint = PoseStamped()
            waypoint.header.frame_id = 'odom'
            waypoint.pose.position.x = 5.0
            waypoint.pose.position.y = 0.0
            waypoint.pose.position.z = 0.0
            waypoint.pose.orientation.x = 0.0
            waypoint.pose.orientation.y = 0.0
            waypoint.pose.orientation.z = 0.0
            waypoint.pose.orientation.w = 1.0

            wp1.pose = waypoint


#            wp2 = GotoWaypoint()
#            wp1.name = "wp2"
#            wp1.lat = 58.820936
#            wp1.lon = 17.618728
#
            mc.waypoints = [wp1]

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
