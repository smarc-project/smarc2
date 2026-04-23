#!/usr/bin/python

import enum
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped, PoseWithCovarianceStamped, Quaternion
from geometry_msgs.msg import PointStamped

from smarc_action_base.gentler_action_server import GentlerActionServer
from dji_msgs.msg import Topics as DJITopics
from alars.alars_common import DroneState


class RecoveryPhases(enum.Enum):
    IDLE = 0
    MOVING_TO_DIPPING_POSITION = 1
    DIPPING = 2
    FORWARD = 3
    RAISING_LOW = 4
    RAISING_MED = 5
    RAISING_HIGH = 6

class RecoverAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value

        self._drone_state = DroneState(node, self._robot_name)

        self._node.declare_parameter('max_rope_length', 3.0)
        self.MAX_ROPE_LENGTH = self._node.get_parameter('max_rope_length').get_parameter_value().double_value

        self._node.declare_parameter('setpoint_tolerance', 0.5)
        self.SETPOINT_TOLERANCE : float = self._node.get_parameter('setpoint_tolerance').get_parameter_value().double_value

        self._node.declare_parameter('max_auv_age', 10.0)
        self.MAX_AUV_AGE = self._node.get_parameter('max_auv_age').get_parameter_value().double_value

        self._node.declare_parameter('max_buoy_age', 20.0)
        self.MAX_BUOY_AGE = self._node.get_parameter('max_buoy_age').get_parameter_value().double_value

        self._reset()

        self._auv_in_map : PoseStamped = PoseStamped()
        self._buoy_in_map : PoseStamped = PoseStamped()
        
        self._setpoint_pub = self._node.create_publisher(
            msg_type = PoseStamped,
            topic = DJITopics.MOVE_TO_SETPOINT_TOPIC,
            qos_profile= 10)
        
        self._node.create_subscription(PoseWithCovarianceStamped,
                                       DJITopics.PROJECTED_AUV_POSE_WITH_COV_TOPIC,
                                       self._auv_projection_cb,
                                       10)
        
        self._node.create_subscription(PoseWithCovarianceStamped,
                                       DJITopics.PROJECTED_BUOY_POSE_WITH_COV_TOPIC,
                                       self._buoy_projection_cb,
                                       10)
        
        self._as = GentlerActionServer(
            node,
            "alars_recover",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 10
        )


            
    def _reset(self):
        self._phase : RecoveryPhases = RecoveryPhases.IDLE
        self._points : dict[RecoveryPhases, PoseStamped] = {}


    def _auv_projection_cb(self, msg: PoseWithCovarianceStamped):
        self._auv_in_map.pose.position.x = msg.pose.pose.position.x
        self._auv_in_map.pose.position.y = msg.pose.pose.position.y
        self._auv_in_map.pose.position.z = msg.pose.pose.position.z
        self._auv_in_map.header = msg.header
        if self._auv_in_map.header.frame_id != self._drone_state.MAP_FRAME:
            try:
                self._auv_in_map = self._drone_state.pose_stamped_in_map(self._auv_in_map)
            except Exception as e:
                self._loginfo(f"Could not transform object position into MAP frame: {e}")
                traceback.print_exc()

    def _buoy_projection_cb(self, msg: PoseWithCovarianceStamped):
        self._buoy_in_map.pose.position.x = msg.pose.pose.position.x
        self._buoy_in_map.pose.position.y = msg.pose.pose.position.y
        self._buoy_in_map.pose.position.z = msg.pose.pose.position.z
        self._buoy_in_map.header = msg.header
        if self._buoy_in_map.header.frame_id != self._drone_state.MAP_FRAME:
            try:
                self._buoy_in_map = self._drone_state.pose_stamped_in_map(self._buoy_in_map)
            except Exception as e:
                self._loginfo(f"Could not transform buoy position into MAP frame: {e}")
                traceback.print_exc()


    def compute_distance(self, pose1 : PoseStamped, pose2 : PoseStamped) -> float:
        if pose1.header.frame_id != pose2.header.frame_id:
            raise ValueError("Poses must be in the same frame to compute distance")
        p1 = np.array([pose1.pose.position.x, pose1.pose.position.y, pose1.pose.position.z])
        p2 = np.array([pose2.pose.position.x, pose2.pose.position.y, pose2.pose.position.z])
        return np.linalg.norm(p1 - p2)


    def _loginfo(self, msg: str):
        self._node.get_logger().info(msg)


    def _on_goal_received(self, goal_request: dict) -> bool:
        # goal: {
        #   "forward_distance": float,
        #   "forward_altitude": float,
        #   "dipping_altitude" : float,
        #   "raising_altitude" : float
        # }
        #            D
        # A          |
        # |          |
        # |          |
        # B----O-----C 
        # A-B = dipping altitude
        # B-C = forward distance, at forward altitude
        # C-D = raising altitude
        # O = where the object and buoy are, perpendicular to screen
        
        try:
            self.forward_distance = float(goal_request['forward_distance'])
            self.forward_altitude = float(goal_request['forward_altitude'])
            self.dipping_altitude = float(goal_request['dipping_altitude'])
            self.raising_altitude = float(goal_request['raising_altitude'])
        except KeyError:
            self._loginfo(f"Goal request is missing a required field, received:\n {goal_request}")
            return False
        
        if self._auv_in_map is None:
            self._loginfo("Rejecting. No AUV position received yet.")
            return False
        
        if self._drone_state.msg_is_older_than(self._auv_in_map, self.MAX_AUV_AGE):
            self._loginfo(f"Rejecting. AUV position is too old.")
            return False
        
        if self._buoy_in_map is None:
            self._loginfo("Rejecting. No buoy position received yet.")
            return False

        if self._drone_state.msg_is_older_than(self._buoy_in_map, self.MAX_BUOY_AGE):
            self._loginfo(f"Rejecting. Buoy position is too old.")
            return False

        try:
            obj_buoy_dist = self.compute_distance(self._auv_in_map, self._buoy_in_map)
        except Exception as e:
            self._loginfo(f"Rejecting. Error occurred while computing distance between auv and buoy: {e}")
            return False
    

        if obj_buoy_dist > self.MAX_ROPE_LENGTH:
            self._loginfo(f"Rejecting. Criteria: obj-buoy dist=={obj_buoy_dist:.1f} <= {self.MAX_ROPE_LENGTH:.1f}")
            return False
        
        self._loginfo(f"Accepted recover action goal. Obj-Buoy dist={obj_buoy_dist:.2f}m")
        return True
    

    def _on_cancel_received(self) -> bool:
        self._loginfo("Cancelled.")
        self._reset()
        return True


    def _prepare_loop(self) -> None:
        # pre-compute all the points
        # see diagram in _on_goal_received
        # everything in odom frame
        obj_pos = np.array([self._auv_in_map.pose.position.x, self._auv_in_map.pose.position.y])
        buoy_pos = np.array([self._buoy_in_map.pose.position.x, self._buoy_in_map.pose.position.y])
        middle_pos = (obj_pos + buoy_pos) / 2.0
        # line perpendicular to obj-buoy line
        rope_direction = buoy_pos - obj_pos
        motion_direction = np.array([-rope_direction[1], rope_direction[0]])
        motion_direction = motion_direction / np.linalg.norm(motion_direction)
        dipping_pos = middle_pos - motion_direction * self.forward_distance/2
        raising_pos = dipping_pos + motion_direction * self.forward_distance 

        # A
        self._dipping_high = PoseStamped()
        self._dipping_high.header.frame_id = self._drone_state.MAP_FRAME
        self._dipping_high.pose.position.x = dipping_pos[0]
        self._dipping_high.pose.position.y = dipping_pos[1]
        self._dipping_high.pose.position.z = self.dipping_altitude
        self._dipping_high.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.MOVING_TO_DIPPING_POSITION] = self._dipping_high

        # B
        self._dipping_low = PoseStamped()
        self._dipping_low.header.frame_id = self._drone_state.MAP_FRAME
        self._dipping_low.pose.position.x = dipping_pos[0]
        self._dipping_low.pose.position.y = dipping_pos[1]
        self._dipping_low.pose.position.z = self.forward_altitude
        self._dipping_low.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.DIPPING] = self._dipping_low

        # C
        self._raising_low = PoseStamped()
        self._raising_low.header.frame_id = self._drone_state.MAP_FRAME
        self._raising_low.pose.position.x = raising_pos[0]
        self._raising_low.pose.position.y = raising_pos[1]
        self._raising_low.pose.position.z = self.forward_altitude
        self._raising_low.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.FORWARD] = self._raising_low

        # D1
        self._raising_high_low = PoseStamped()
        self._raising_high_low.header.frame_id = self._drone_state.MAP_FRAME
        self._raising_high_low.pose.position.x = raising_pos[0]
        self._raising_high_low.pose.position.y = raising_pos[1]
        self._raising_high_low.pose.position.z = self.raising_altitude/4.0
        self._raising_high_low.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.RAISING_LOW] = self._raising_high_low

        # D2
        self._raising_high_med = PoseStamped()
        self._raising_high_med.header.frame_id = self._drone_state.MAP_FRAME
        self._raising_high_med.pose.position.x = raising_pos[0]
        self._raising_high_med.pose.position.y = raising_pos[1]
        self._raising_high_med.pose.position.z = self.raising_altitude/2.0
        self._raising_high_med.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.RAISING_MED] = self._raising_high_med

        # D3
        self._raising_high_high = PoseStamped()
        self._raising_high_high.header.frame_id = self._drone_state.MAP_FRAME
        self._raising_high_high.pose.position.x = raising_pos[0]
        self._raising_high_high.pose.position.y = raising_pos[1]
        self._raising_high_high.pose.position.z = self.raising_altitude
        self._raising_high_high.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self._points[RecoveryPhases.RAISING_HIGH] = self._raising_high_high

        
    def _loop_inner(self) -> bool|None:
        """
        Return True to indicate success, False for failure, or None to continue
        """
        if self._drone_state.drone_in_map is None:
            self._loginfo("No odom received yet, cannot perform recovery...")
            return False
        
        if self._phase == RecoveryPhases.IDLE:
            self._phase = RecoveryPhases.MOVING_TO_DIPPING_POSITION
            self._loginfo(f"Starting recovery, moving to dipping position at {str_posestamp(self._points[self._phase])}")
        
        target_point = self._points[self._phase]
        distance_to_target = self.compute_distance(self._drone_state.drone_in_map, target_point)
        
        if distance_to_target <= self.SETPOINT_TOLERANCE:
            # reached current phase target, move to next phase
            if self._phase == RecoveryPhases.MOVING_TO_DIPPING_POSITION:
                self._phase = RecoveryPhases.DIPPING
                self._loginfo(f"MOVING_TO_DIPPING_POSITION -> DIPPING")
                return None
            elif self._phase == RecoveryPhases.DIPPING:
                self._phase = RecoveryPhases.FORWARD
                self._loginfo(f"DIPPING -> FORWARD")
                return None
            elif self._phase == RecoveryPhases.FORWARD:
                self._phase = RecoveryPhases.RAISING_LOW
                self._loginfo(f"FORWARD -> RAISING_LOW")
                return None
            elif self._phase == RecoveryPhases.RAISING_LOW:
                self._phase = RecoveryPhases.RAISING_MED
                self._loginfo(f"RAISING_LOW -> RAISING_MED")
                return None
            elif self._phase == RecoveryPhases.RAISING_MED:
                self._phase = RecoveryPhases.RAISING_HIGH
                self._loginfo(f"RAISING_MED -> RAISING_HIGH")
                return None
            elif self._phase == RecoveryPhases.RAISING_HIGH:
                self._loginfo("Recovery completed successfully.")
                self._reset()
                return True
            
        # still en route to current phase target, publish setpoint
        target_point.header.stamp = self._node.get_clock().now().to_msg()
        self._setpoint_pub.publish(target_point)
        return None

        
    def _give_feedback(self) -> str:
        return f"Phase: {self._phase.name}"


def point_to_pose(ps_in: PointStamped) -> PoseStamped:
    ps = PoseStamped()
    ps.header = ps_in.header
    ps.pose.position = ps_in.point
    ps.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    return ps

def str_posestamp(pose: PoseStamped):
    """Helper function to print PoseStamped Messages nicely."""
    pos = pose.pose.position
    return (f"Pos:[{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}] in {pose.header.frame_id}")
        

def main(args=None):
    rclpy.init(args=args)

    node = Node("alars_recover_action_server")

    recover_action = RecoverAction(node)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()