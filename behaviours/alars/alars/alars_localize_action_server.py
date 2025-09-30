#!/usr/bin/python

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Float32

from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_utilities.georef_utils import convert_latlon_to_utm
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics

class LocalizeAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value

        self.GIMBAL_FRAME : str = self._robot_name + '/' + DJILinks.GIMBAL_CAMERA_LINK
        self._MAX_DETECTION_AGE : float = 2.0  # seconds
        self._TRACKING_TOLERANCE : float = 0.1  # normalized image coordinates
        self._TRACKING_AGGRESSIVENESS : float = 0.5

        self._auv_position : PointStamped = PointStamped()
        self._buoy_position : PointStamped = PointStamped()
        self._auv_altitude : float = 0.0

        self._setpoint : PoseStamped = PoseStamped()
        self._setpoint.header.frame_id = self.GIMBAL_FRAME

        
        self._setpoint_pub = self._node.create_publisher(
            msg_type = PoseStamped,
            topic = DJITopics.MOVE_TO_SETPOINT_TOPIC,
            qos_profile= 10)
        
        self._node.create_subscription(PointStamped, 
                                       DJITopics.ESTIMATED_AUV_TOPIC,
                                       self._auv_detection_cb,
                                       10)
        
        self._node.create_subscription(PointStamped,
                                       DJITopics.ESTIMATED_BUOY_TOPIC,
                                       self._buoy_detection_cb,
                                       10)
        
        self._node.create_subscription(Float32,
                                       SmarcTopics.ALTITUDE_TOPIC,
                                       self._alt_cb,
                                       10)
        
        self._as = GentlerActionServer(
            node,
            "alars_localize",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 10
        )

        self._track_auv : bool = False
        self._track_buoy : bool = False



    def _loginfo(self, msg: str):
        self._node.get_logger().info(f"[LocalizeAction] {msg}")

    def _auv_detection_cb(self, msg: PointStamped):
        self._auv_position = msg

    def _buoy_detection_cb(self, msg: PointStamped):
        self._buoy_position = msg

    def _alt_cb(self, msg: Float32):
        self._auv_altitude = msg.data

    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        This action does not take any input goal parameters, instead it 
        always listens to the detection topics and works from those.
        """
        s = "Received goal"
        got_auv = self._auv_position.header.stamp.sec != 0 and self._auv_position.point.x != 0 and self._auv_position.point.y != 0
        got_buoy = self._buoy_position.header.stamp.sec != 0 and self._buoy_position.point.x != 0 and self._buoy_position.point.y != 0

        self._track_auv = bool(goal_request['localize_auv'])
        self._track_buoy = bool(goal_request['localize_buoy'])

        if self._track_auv and self._track_buoy:
            s += " to localize both AUV and Buoy at the same time, we dont do that here, rejecting."
            self._reset()
            self._loginfo(s)
            return False

        if (self._track_auv and not got_auv) or (self._track_buoy and not got_buoy):
            s += f", but either no AUV(got:{got_auv}, want:{self._track_auv}) or no Buoy(got:{got_buoy}, want:{self._track_buoy}) detection received yet, rejecting."
            self._reset()
            self._loginfo(s)
            return False
        else:
            s += f", accepting (got_auv:{got_auv}, want_auv:{self._track_auv}, got_buoy:{got_buoy}, want_buoy:{self._track_buoy})."
            self._loginfo(s)
            return True
        
    def _reset(self):
        self._track_auv = False
        self._track_buoy = False
        
    def _on_cancel_received(self) -> bool:
        self._loginfo("Cancelled.")
        self._reset()
        return True
    
    def _prepare_loop(self) -> None:
        # nothing to prepare for this, goal check already made sure
        # we have the necessary detections
        return
    
    def _msg_is_older_than(self, msg, age_s: float) -> bool:
        now_stamp = self._node.get_clock().now().to_msg()
        return (now_stamp.sec - msg.header.stamp.sec) + (now_stamp.nanosec - msg.header.stamp.nanosec) * 1e-9 > age_s

    def _loop_inner(self) -> bool|None:
        """
        Return True to indicate success, False for failure, or None to continue
        """

        # we simply move the camera such that the auv is centered in the image
        # since the detection topic is normalized to -1,1, that means we just
        # need to make it 0,0-ish
        # we'll publish the setpoint in the camera frame, the captain should
        # handle the rest
        
        if not self._track_auv and not self._track_buoy:
            self._loginfo("Not tracking anything, finishing with success.")
            self._reset()
            return True

        target_position = self._auv_position if self._track_auv else self._buoy_position

        # check if the detection is recent enough
        if self._msg_is_older_than(target_position, self._MAX_DETECTION_AGE):
            self._loginfo("AUV/Buoy detection message too old, aborting.")
            self._reset()
            return False
        
        
        # are we done tracking?
        if abs(target_position.point.x) <= self._TRACKING_TOLERANCE and abs(target_position.point.y) <= self._TRACKING_TOLERANCE:
            self._loginfo("AUV/Buoy centered, finishing with success.")
            self._reset()
            return True
        
        # not done tracking, do P control i guess
        self._setpoint.header.stamp = self._node.get_clock().now().to_msg()

        if abs(target_position.point.x) > self._TRACKING_TOLERANCE:
            self._setpoint.pose.position.x = -target_position.point.x * self._TRACKING_AGGRESSIVENESS
        else:
            self._setpoint.pose.position.x = 0.0

        if abs(target_position.point.y) > self._TRACKING_TOLERANCE:
            self._setpoint.pose.position.y = -target_position.point.y * self._TRACKING_AGGRESSIVENESS
        else:
            self._setpoint.pose.position.y = 0.0

        self._setpoint_pub.publish(self._setpoint)

        self._loginfo(f"Tracking: {self._give_feedback()}")
        return None

        

    def _give_feedback(self) -> str:
        target_position = self._auv_position if self._track_auv else self._buoy_position
        target = f'{target_position.point.x:.2f},{target_position.point.y:.2f},{target_position.point.z:.2f}'
        setpoint = f'{self._setpoint.pose.position.x:.2f},{self._setpoint.pose.position.y:.2f},{self._setpoint.pose.position.z:.2f}'
        return f"Target:{target}, setpoint:{setpoint}"


def main(args=None):
    rclpy.init(args=args)

    node = Node("alars_localize_action_server")

    localize_action = LocalizeAction(node)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()