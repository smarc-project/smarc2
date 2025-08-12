#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node

import numpy as np
import math

from tf2_geometry_msgs import PoseWithCovarianceStamped
import tf2_geometry_msgs.tf2_geometry_msgs
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped, TransformStamped
from sensor_msgs.msg import Imu

from smarc_msgs.msg import PercentStamped, ThrusterRPM, ThrusterFeedback
from smarc_control_msgs.msg import Topics as ControlTopics
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles, ThrusterRPMs
from dead_reckoning_msgs.msg import Topics as DRTopics
from rclpy.executors import MultiThreadedExecutor

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
                 param):

        self._node = node

        self.param = param

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        # We need to declare the parameter we want to read out from the alunch file first.
        self._node.declare_parameter('robot_name', 'sam0')
        self._node.declare_parameter('tf_suffix', '')
        self._node.declare_parameter('acados_dir', '')
        tf_suffix = self._node.get_parameter('tf_suffix').get_parameter_value().string_value
        self.robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value
        self._robot_base_link = self.robot_name + '/base_link'+ tf_suffix
        self._odom_link = self.robot_name + '/odom'
        self.acados_dir = self._node.get_parameter('acados_dir').get_parameter_value().string_value

        self._loginfo(f"robot base link: {self._robot_base_link}")

        self._depth_setpoint = None
        self._pitch_setpoint = None
        self._requested_rpm = None
        self._goal_tolerance = None
        self._waypoint_global = None
        self._waypoint_body = None
        self._waypoint_odom = None
        self._received_waypoint = False
        self._joy_depth = None
        self._depth = None
        self._pitch = None

        # Trajectory tracking variables.
        self.path = None
        self.path_len = None
        self.current_idx = 0

        self._mission_state = MissionStates.NONE

        self._tf_base_link = None
        self._tf_odom_link = None

        self._states = Odometry()
        self._received_states = False

        self._control_input = {} 
        self._control_input['vbs'] = self.param['vbs_u_neutral']
        self._control_input['lcg'] = self.param['lcg_u_neutral']
        self._control_input['rpm1'] = self.param['rpm_u_neutral']
        self._control_input['rpm2'] = self.param['rpm_u_neutral']
        self._control_input['stern'] = self.param['tv_u_neutral']
        self._control_input['rudder'] = self.param['tv_u_neutral']

        self.state_sub = node.create_subscription(msg_type=Odometry, topic=ControlTopics.STATES, callback=self._states_cb, qos_profile=10)
        self.waypoint_sub = node.create_subscription(msg_type=PoseStamped, topic=ControlTopics.WAYPOINT, callback=self._wp_cb, qos_profile=10)
        self.joy_depth_setpoint_sub = node.create_subscription(msg_type=Float64, topic=ControlTopics.ELEV_SP_TOP, callback=self._joy_depth_setpoint_cb, qos_profile=10)
        self.depth_sub = node.create_subscription(msg_type=PoseWithCovarianceStamped, topic=DRTopics.DR_DEPTH_POSE_TOPIC, callback=self._depth_cb, qos_profile=10)
        self.pitch_sub = node.create_subscription(msg_type=Imu, topic=ControlTopics.PITCH, callback=self._pitch_cb, qos_profile=10)

        # Path subscriber - Added for trajectory tracking
        self.path_sub = node.create_subscription(msg_type=Path, topic='planned_path', callback=self._path_cb, qos_profile=10)

        # Test of subscribers - excluding ctrl_synch_msg
        self.lcg_fb = node.create_subscription(msg_type=PercentStamped, topic=SamTopics.LCG_FB_TOPIC, callback=self._lcg_cb, qos_profile=10)
        self.vbs_fb = node.create_subscription(msg_type=PercentStamped, topic=SamTopics.VBS_FB_TOPIC, callback=self._vbs_cb, qos_profile=10)
        # self.rpm1_fb = node.create_subscription(msg_type=ThrusterRPM, topic=SamTopics.THRUSTER1_CMD_TOPIC, callback=self._lcg_cb, qos_profile=10)
        # self.rpm2_fb = node.create_subscription(msg_type=ThrusterRPM, topic=SamTopics.THRUSTER2_CMD_TOPIC, callback=self._lcg_cb, qos_profile=10)
        self.combined_rpms_fb = node.create_subscription(msg_type=ThrusterRPMs, topic="core/thruster_rpms_cmd", callback=self._rpms_cb, qos_profile=10)
        self.thrust_vector_fb = node.create_subscription(msg_type=ThrusterAngles, topic=SamTopics.THRUST_VECTOR_CMD_TOPIC, callback=self._thrust_vector_cb, qos_profile=10)

        # Synch subscribers here 
        # self.lcg_fb = Subscriber(self._node, PercentStamped, SamTopics.LCG_FB_TOPIC)
        # self.vbs_fb = Subscriber(self._node, PercentStamped, SamTopics.VBS_FB_TOPIC)
        # self.rpm1_fb = Subscriber(self._node, ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC)
        # self.rpm2_fb = Subscriber(self._node, ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC)
        # self.thrust_vector_fb = Subscriber(self._node, ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC)

        #self.ctrl_synch_msg = ApproximateTimeSynchronizer(
        #    [self.vbs_fb, self.lcg_fb, self.rpm1_fb, self.rpm2_fb, self.thrust_vector_fb],
        #    queue_size = 100,
        #    slop = 0.0001
        #)
        #self.ctrl_synch_msg.registerCallback(self._ctrl_synch_cb)

        self._loginfo("Dive Subscriber Node started")


    # Internal methods
    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _states_cb(self, msg):
        self._states = msg
        #self._loginfo(f"R. state:{self._states.pose.pose.position.x:.2f}, {self._states.pose.pose.position.y:.2f}, {self._states.pose.pose.position.z:.2f} ")
        self._received_states = True


    def _wp_cb(self, wp):
        self._waypoint_global = wp

        # NOTE: RPMs are now "fast", "standard", "slow"
        self._requested_rpm = 500
        self._received_waypoint = True

    def _path_cb(self, path):
        self.path = path
    
    def _joy_depth_setpoint_cb(self, msg):
        self._joy_depth = msg.data

    def _depth_cb(self, msg):
        self._depth = msg.pose.pose.position.z

    def _pitch_cb(self, msg):
        quat = np.array([msg.orientation.w, msg.orientation.x, msg.orientation.y, msg.orientation.z])
        rpy = euler_from_quaternion(quat,axes='sxyz')
        self._pitch = rpy[1]

    def _ctrl_synch_cb(self, vbs_fb_msg: PercentStamped, lcg_fb_msg: PercentStamped,
                       combined_rpms_fb: ThrusterRPMs,
                       thrust_vector_fb_msg: ThrusterAngles):
        self._control_input['vbs'] = vbs_fb_msg.value
        self._control_input['lcg'] = lcg_fb_msg.value
        self._control_input['rpm1'] = combined_rpms_fb.thruster_1_rpm
        self._control_input['rpm2'] = combined_rpms_fb.thruster_2_rpm
        self._control_input['stern'] = thrust_vector_fb_msg.thruster_vertical_radians
        self._control_input['rudder'] = thrust_vector_fb_msg.thruster_horizontal_radians

    # Control input callbacks added for testing
    def _vbs_cb(self, vbs_fb_msg: PercentStamped):
        #self._loginfo(f"vbs: {vbs_fb_msg.header.stamp}")
        self._control_input['vbs'] = vbs_fb_msg.value

    def _lcg_cb(self, lcg_fb_msg: PercentStamped):
        #self._loginfo(f"lcg: {lcg_fb_msg.header.stamp}")
        self._control_input['lcg'] = lcg_fb_msg.value

    def _rpms_cb(self, combined_rpms_fb: ThrusterRPMs):
        #self._loginfo(f"rpms: {combined_rpms_fb.header.stamp}")
        self._control_input['rpm1'] = combined_rpms_fb.thruster_1_rpm
        self._control_input['rpm2'] = combined_rpms_fb.thruster_2_rpm 

    def _thrust_vector_cb(self, thrust_vector_fb_msg: ThrusterAngles):
        #self._loginfo(f"Thrust {thrust_vector_fb_msg.header.stamp}")
        self._control_input['stern'] = thrust_vector_fb_msg.thruster_vertical_radians
        self._control_input['rudder'] = thrust_vector_fb_msg.thruster_horizontal_radians
    # ------------------------------------------------------------------------------------

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

        try:
            self._tf_odom_link = self._tf_buffer.lookup_transform(self._odom_link,
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

        self._waypoint_odom = tf2_geometry_msgs.do_transform_pose(self._waypoint_global.pose, self._tf_odom_link)
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
        #return self._states
        if self._received_states:
            return self._states
        else: 
            return None

    def get_control_input(self):
        return self._control_input
    

    def get_depth(self):
        return self._states.pose.pose.position.z

    def get_sensor_depth(self):
        return self._depth

    def get_pitch(self):

        rpy = euler_from_quaternion([
            self._states.pose.pose.orientation.x,
            self._states.pose.pose.orientation.y,
            self._states.pose.pose.orientation.z,
            self._states.pose.pose.orientation.w])

        return rpy[1]

    def get_sensor_pitch(self):
        
        return self._pitch


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
        """
        This is basically a look-ahead controller based on the distance to the waypoint.
        """
        if self._waypoint_body is None:
            return None

        # With the ata2, we automatically get the desired diving pitch angle that corresponds to 
        # a ENU system, i.e. positive pitch for diving down, negative pitch for diving up
        current_depth = self.get_depth()
        depth_setpoint = self.get_depth_setpoint()
        #depth_setpoint *= -1
        #current_depth *= -1
        depth_error = depth_setpoint - current_depth
        look_ahead_distance = 3
        dive_pitch = math.atan2(-depth_error, look_ahead_distance)

        return dive_pitch

    def get_waypoint(self):
        return self._waypoint_global
    

    def get_path(self, path):
        return self.path

    def get_odom_waypoint(self):
        return self._waypoint_odom

    def get_path(self):
        return self.path

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


    def get_joy_depth_setpoint(self):
        return self._joy_depth


    def get_joy_pitch_setpoint(self):

        return 0.0
    
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

    def set_current_idx(self, idx):
        """
        Setting the current index of the trajectory we're following.
        """
        
        self.current_idx = idx

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
