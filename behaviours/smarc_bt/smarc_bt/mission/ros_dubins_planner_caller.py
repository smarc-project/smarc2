#!/usr/bin/python3

import numpy as np
from rclpy.node import Node

from rosidl_runtime_py.set_message import set_message_fields
from rosidl_runtime_py.convert import message_to_ordereddict

from smarc_mission_msgs.msg import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_mission_msgs.srv import DubinsPlan
from geometry_msgs.msg import Pose2D

from .ros_waypoint import SMaRCWP
from .ros_mission_plan import ROSMissionPlan


# Because the dubins planner uses X=right, Y=up, CCW angles
# while mission plans have X=North, Y=East, CCW angles for heading
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


class ROSDubinsPlannerCaller:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._dubins_planner = self._node.create_client(DubinsPlan,
                                                        MissionTopics.DUBINS_SERVICE)
        self.reset()

    def _log(self, s:str):
        self._node.get_logger().info(s)

    

    def call(self, mplan: ROSMissionPlan, turning_rad: float, step: float) -> None:
        if not type(mplan._waypoints[0]) == SMaRCWP:
            self._log("Dubins planning requires a mission with SMaRCWP waypoints!")
            return
        
        self._converted = False        
        self._mission_plan = mplan

        request = DubinsPlan.Request()
        request.step = float(step)
        request.turning_radius = float(turning_rad)
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

        self._log("Calling dubins planner service")
        self._future = self._dubins_planner.call_async(request)
        self._future.add_done_callback(self._done_cb)

    def _done_cb(self, future) -> None:
        result = future.result()
        # the interpolated waypoints
        # these include the original wps
        dubins_wps = result.waypoints
        # which of the waypoints are "original"
        # we can do index-mapping from these
        # to the original mission plan object
        # to recover all the details of the originals
        # that the dubins planner didnt want
        og_indices = result.original_wp_indices

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
                og_wp = self._mission_plan._waypoints.pop()._goto_wp
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
            new_wp = SMaRCWP(new_goto_wp)
            wp_list.append(new_wp)

        # since we went backwards when filling this...
        wp_list.reverse()
        new_plan = ROSMissionPlan(self._mission_plan._node,
                                  self._mission_plan._plan_id,
                                  wp_list)
        self._mission_plan = new_plan

        self._converted = True


    def reset(self):
        self._mission_plan = None
        self._future = None
        self._converted = False


    @property
    def done(self) -> bool:
        return self._converted
    

    def get_result(self) -> ROSMissionPlan:
        if self.done:
            return self._mission_plan
        
        return None
    


def test_dubins_planner_caller():
    import matplotlib.pyplot as plt
    import rclpy, sys

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("dubins_planner_caller_tester")

    caller = ROSDubinsPlannerCaller(node)

    step = 0.5
    turning_rad = 5.0
    # x,y,heading
    # heading is compass heading, so 0=north, 90=east
    points = [
        (0.0,  0.0, 0.0 ),
        (10.0, 0.0, 0.0 ),
        (20.0, 0.0, 90.0)
    ]

    def plot_path(ax, points, marker='bo', arrow_color='k'):
        # Plot each point and draw an arrow according to the angle
        for x, y, angle in points:
            ax.plot(x, y, marker)  # 'bo' creates a blue circle marker
            # Calculate the arrow's dx and dy using the angle
            dx = np.cos(np.deg2rad(_heading_to_yaw(angle)))
            dy = np.sin(np.deg2rad(_heading_to_yaw(angle)))
            ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc=arrow_color, ec=arrow_color)

    # Create the plot
    fig, ax = plt.subplots()
    plot_path(ax, points, marker='rx', arrow_color='r')

    wp1 = GotoWaypoint()
    wp1.name = "one"
    wp1.pose.pose.position.x = points[0][0]
    wp1.pose.pose.position.y = points[0][1]
    wp1.arrival_heading = points[0][2]
    wp1.use_heading = True

    wp2 = GotoWaypoint()
    wp2.name = "two"
    wp2.pose.pose.position.x = points[1][0]
    wp2.pose.pose.position.y = points[1][1]
    wp2.arrival_heading = points[1][2]
    wp2.use_heading = True

    wp3 = GotoWaypoint()
    wp3.name = "three"
    wp3.pose.pose.position.x = points[2][0]
    wp3.pose.pose.position.y = points[2][1]
    wp3.arrival_heading = points[2][2]
    wp3.use_heading = True


    wps = [
        SMaRCWP(wp1),
        SMaRCWP(wp2),
        SMaRCWP(wp3)
    ]
    mplan = ROSMissionPlan(node, "test_mission", wps)

    caller.call(mplan, turning_rad, step)

    new_plan = None
    def wait():
        nonlocal caller, new_plan, ax
        if not caller.done: return

        new_plan = caller.get_result()
        if new_plan is not None:
            caller.reset()
            plot_path(ax, [(p[0], p[1], p[2]) for p in  new_plan.planar_wps])



    node.create_timer(1, wait)
    for i in range(5):
        print(i)
        rclpy.spin_once(node)

    plt.show()
