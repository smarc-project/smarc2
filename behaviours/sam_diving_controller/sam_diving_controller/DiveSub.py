#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node

import numpy as np
import math

import tf2_geometry_msgs.tf2_geometry_msgs
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped, TransformStamped

from smarc_msgs.msg import PercentStamped, ThrusterRPM
from smarc_control_msgs.msg import Topics as ControlTopics
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

from message_filters import Subscriber, ApproximateTimeSynchronizer

from tf_transformations import euler_from_quaternion

try:
    from .IDivePub import IDivePub, MissionStates
except: 
    from IDivePub import IDivePub, MissionStates

class DiveSub():
    """
    Dive Controller to listen to a waypoint and provide the corresponding setpoints to the
    DivingModel within the MVC framework
    """
    def __init__(self,
                 node: Node,
                 dive_pub: IDivePub):

        self._node = node
        self._dive_pub = dive_pub

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        # We need to declare the parameter we want to read out from the alunch file first.
        self._node.declare_parameter('robot_name', 'sam0')
        self._node.declare_parameter('tf_suffix', '')
        self._node.declare_parameter('acados_dir', '')
        tf_suffix = self._node.get_parameter('tf_suffix').get_parameter_value().string_value
        robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value
        self._robot_base_link = robot_name + '/base_link'+ tf_suffix #'/base_link_gt'
        self.acados_dir = self._node.get_parameter('acados_dir').get_parameter_value().string_value

        self._loginfo(f"robot base link: {self._robot_base_link}")

        self._depth_setpoint = None
        self._pitch_setpoint = None
        self._requested_rpm = None
        self._goal_tolerance = None
        self._waypoint_global = None
        self._waypoint_body = None
        self._received_waypoint = False

        self._mission_state = MissionStates.NONE

        self._tf_base_link = None

        self._states = Odometry()

        self._control_input = {} 
        self._control_input['vbs'] = 0.0
        self._control_input['lcg'] = 0.0
        self._control_input['rpm1'] = 0.0
        self._control_input['rpm2'] = 0.0
        self._control_input['stern'] = 0.0
        self._control_input['rudder'] = 0.0

        self.state_sub = node.create_subscription(msg_type=Odometry, topic=ControlTopics.STATES, callback=self._states_cb, qos_profile=10)
        self.waypoint_sub = node.create_subscription(msg_type=PoseStamped, topic=ControlTopics.WAYPOINT, callback=self._wp_cb, qos_profile=10)

        # Synch subscribers here 
        self.lcg_fb = Subscriber(self._node, PercentStamped, SamTopics.LCG_FB_TOPIC)
        self.vbs_fb = Subscriber(self._node, PercentStamped, SamTopics.VBS_FB_TOPIC)
        self.rpm1_fb = Subscriber(self._node, ThrusterRPM, SamTopics.THRUSTER1_FB_TOPIC)
        self.rpm2_fb = Subscriber(self._node, ThrusterRPM, SamTopics.THRUSTER2_FB_TOPIC)
        self.thrust_vector_fb = Subscriber(self._node, ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC)

        self.ctrl_synch_msg = ApproximateTimeSynchronizer(
            [self.vbs_fb, self.lcg_fb, self.rpm1_fb, self.rpm2_fb, self.thrust_vector_fb],
            queue_size = 100,
            slop = 0.0001
        )
        self.ctrl_synch_msg.registerCallback(self._ctrl_synch_cb)

        self._loginfo("Dive Controller Node started")


    # Internal methods
    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _states_cb(self, msg):
        self._states = msg


    def _wp_cb(self, wp):
        self._waypoint_global = wp

        # TODO: Get the proper RPM from the waypoint
        self._requested_rpm = 500
        self._received_waypoint = True

    def _ctrl_synch_cb(self, vbs_fb_msg: PercentStamped, lcg_fb_msg: PercentStamped,
                       rpm1_fb_msg: ThrusterRPM, rpm2_fb_msg: ThrusterRPM, 
                       thrust_vector_fb_msg: ThrusterAngles):
        self._control_input['vbs'] = vbs_fb_msg.value
        self._control_input['lcg'] = lcg_fb_msg.value
        self._control_input['rpm1'] = rpm1_fb_msg.rpm
        self._control_input['rpm2'] = rpm2_fb_msg.rpm
        self._control_input['stern'] = thrust_vector_fb_msg.thruster_vertical_radians
        self._control_input['rudder'] = thrust_vector_fb_msg.thruster_horizontal_radians


    def _update_tf(self):
        if self._waypoint_global is None:
            return

        try:
            self._tf_base_link = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                                  self._waypoint_global.header.frame_id,
                                                                  rclpy.time.Time(seconds=0))
        except Exception as ex:
            self._loginfo(
                f"Could not transform {self._robot_base_link} to {self._waypoint_global.header.frame_id}: {ex}")
            return


    def _transform_wp(self):
        if self._waypoint_global is None:
            return

        if self._tf_base_link is None:
            return

        self._waypoint_body = tf2_geometry_msgs.do_transform_pose(self._waypoint_global.pose, self._tf_base_link)


    # Get methods
    def get_depth_setpoint(self):
        if self._waypoint_body is not None:
            self._depth_setpoint = self._waypoint_global.pose.position.z

        return self._depth_setpoint


    def get_pitch_setpoint(self):
        if self._waypoint_body is not None:
            rpy = euler_from_quaternion([
                self._waypoint_global.pose.orientation.x,
                self._waypoint_global.pose.orientation.y,
                self._waypoint_global.pose.orientation.z,
                self._waypoint_global.pose.orientation.w])

            self._pitch_setpoint = rpy[1]

        return self._pitch_setpoint

    def get_heading_setpoint(self):
        # NOTE: Sketchy implementation. We want the heading to be zero since we
        # calculate the heading error as the angle between the current heading
        # and where the waypoint is. In case we want to do heading control at
        # one point, we have to change/adjust this.
        return 0.0 

    def get_rpm_setpoint(self):
        return self._requested_rpm

    def get_states(self):
        # TODO: Might be better to split this by what 
        # state you're interested in, then you can get them
        # directly.
        return self._states

    def get_control_input(self):
        return self._control_input
    

    def get_depth(self):
        return self._states.pose.pose.position.z


    def get_pitch(self):

        rpy = euler_from_quaternion([
            self._states.pose.pose.orientation.x,
            self._states.pose.pose.orientation.y,
            self._states.pose.pose.orientation.z,
            self._states.pose.pose.orientation.w])

        return rpy[1]


    def get_heading(self):

        if self._waypoint_body is None:
            return None

        heading = math.atan2(self._waypoint_body.position.y, self._waypoint_body.position.x)

        return heading

    def get_distance(self):
        """
        Euclidean norm as distance from body, i.e. origin to waypoint
        """

        if self._waypoint_body is None:
            return None

        distance = math.sqrt(self._waypoint_body.position.x**2 + self._waypoint_body.position.y**2 + self._waypoint_body.position.z**2)

        return distance

    def get_dive_pitch(self):
        if self._waypoint_body is None:
            return None

        # With the ata2, we automatically get the desired diving pitch angle that corresponds to 
        # a ENU system, i.e. positive pitch for diving down, negative pitch for diving up
        current_depth = self.get_depth()
        depth_error = np.abs(self._waypoint_global.pose.position.z) - np.abs(current_depth)
        distance = self.get_distance()
        dive_pitch = math.atan2(depth_error, distance)

        return dive_pitch

    def get_waypoint(self):
        return self._waypoint_global

    def get_goal_tolerance(self):

        if self._goal_tolerance is None:
            return 0

        return self._goal_tolerance

    def get_mission_state(self):
        """
        This is needed when using an action server. Then it has the proper string.
        Otherwise nothing happens and the condition in the DivingModel is ignored.
        Could be fixed at one point...
        """
        return self._mission_state
    
    # Has methods
    def has_waypoint(self):
        return self._received_waypoint

    def set_mission_state(self, new_state, node_name):
        old_state = self._mission_state
        self._mission_state = new_state

        s=""
        if new_state in MissionStates.TERMINAL_STATES():
            # TODO: Setting the waypoint to None kills the controller, bc it expects
            # a pose.
            #self._waypoint_global = None 
            s = "(Terminal)"

        self._loginfo(f"DiveController state: from {node_name}: {old_state} --> {new_state}{s}")

    def update(self):
        """
        All the things when updating
        """
        self._update_tf()
        self._transform_wp()



def main():
#    # when creating the _object_ rather than the _class_, we use the concrete classes
#    from .SAMDiveView import SAMThrustView
#
    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DiveNode")
    node._logger("not implemented")
#    view = SAMThrustView(node)
#    controller = GoToWaypointActionServerController(node, view)
#
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)


if __name__ == "__main__":
    main()
