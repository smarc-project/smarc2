#!/usr/bin/python

import enum
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped, PoseWithCovarianceStamped, Quaternion
from geometry_msgs.msg import PointStamped

from tf2_ros import Buffer, TransformListener

from smarc_action_base.gentler_action_server import GentlerActionServer
from dji_msgs.msg import Topics as DJITopics
from alars.alars_common import DroneState



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
        self._wp_index = 0
        self._points : list[PoseStamped] = []


    def _auv_projection_cb(self, msg: PoseWithCovarianceStamped):
        self._auv_in_map.pose.position.x = msg.pose.pose.position.x
        self._auv_in_map.pose.position.y = msg.pose.pose.position.y
        self._auv_in_map.pose.position.z = msg.pose.pose.position.z
        self._auv_in_map.header = msg.header
        if self._auv_in_map.header.frame_id != self._drone_state.MAP_FRAME:
            try:
                in_map = self._drone_state.pose_stamped_in_map(self._auv_in_map)
                if in_map is not None:
                    self._auv_in_map = in_map
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
                in_map = self._drone_state.pose_stamped_in_map(self._buoy_in_map)
                if in_map is not None:
                    self._buoy_in_map = in_map
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
        #   "no_buoy": bool 
        #   "no_buoy_radius": float,
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
            self._no_buoy_radius = float(goal_request['no_buoy_radius'])
            self._recover_without_buoy = self._no_buoy_radius > 0
            self._forward_distance = float(goal_request['forward_distance'])
            self._forward_altitude = float(goal_request['forward_altitude'])
            self._dipping_altitude = float(goal_request['dipping_altitude'])
            self._raising_altitude = float(goal_request['raising_altitude'])
        except KeyError:
            self._loginfo(f"Goal request is missing a required field, received:\n {goal_request}")
            return False
        
        if self._auv_in_map is None:
            self._loginfo("Rejecting. No AUV position received yet.")
            return False
        
        if self._drone_state.msg_is_older_than(self._auv_in_map, self.MAX_AUV_AGE, "auv in map goal check"):
            self._loginfo(f"Rejecting. AUV position is too old.")
            return False
        
        if self._recover_without_buoy:
            self._loginfo(f"Accepted recover action goal without buoy.")
            return True
        else:
            self._loginfo(f"Received recover action goal with buoy. Checking criteria...")
            if self._buoy_in_map is None:
                self._loginfo("Rejecting. No buoy position received yet.")
                return False

            if self._drone_state.msg_is_older_than(self._buoy_in_map, self.MAX_BUOY_AGE, "buoy in map goal check"):
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
    
    
    def _points_with_buoy(self):
        # pre-compute all the points
        # see diagram in _on_goal_received
        # everything in odom frame
        sam_pos = np.array([self._auv_in_map.pose.position.x, self._auv_in_map.pose.position.y])
        buoy_pos = np.array([self._buoy_in_map.pose.position.x, self._buoy_in_map.pose.position.y])
        middle_pos = (sam_pos + buoy_pos) / 2.0
        # line perpendicular to obj-buoy line
        rope_direction = buoy_pos - sam_pos
        motion_direction = np.array([-rope_direction[1], rope_direction[0]])
        motion_direction = motion_direction / np.linalg.norm(motion_direction)
        dipping_pos = middle_pos - motion_direction * self._forward_distance/2
        dragged_pos = dipping_pos + motion_direction * self._forward_distance 

        p = [
            (dipping_pos, self._dipping_altitude), #A
            (dipping_pos, self._forward_altitude), #B
            (dragged_pos, self._forward_altitude), #C
            (dragged_pos, self._raising_altitude/5.0), #D1
            (dragged_pos, self._raising_altitude/2.0), #D2
            (dragged_pos, self._raising_altitude) #D3
        ]

        for (pos, alt) in p:
            ps = PoseStamped()
            ps.header.frame_id = self._drone_state.MAP_FRAME
            ps.pose.position.x = pos[0]
            ps.pose.position.y = pos[1]
            ps.pose.position.z = alt
            ps.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
            self._points.append(ps)



    def _points_without_buoy(self):
        sam_pos = np.array([self._auv_in_map.pose.position.x, self._auv_in_map.pose.position.y])
        # since there is no guiding buoy, we make a circle around sam of given radius
        # after doing the same dipping
        # and after the circle, we will do the same raising
        num_points = 8
        circle = []
        for i in range(num_points):
            angle = i * 2 * np.pi / num_points
            offset = np.array([np.cos(angle), np.sin(angle)]) * self._no_buoy_radius
            pos = sam_pos + offset
            ps = PoseStamped()
            ps.header.frame_id = self._drone_state.MAP_FRAME
            ps.pose.position.x = pos[0]
            ps.pose.position.y = pos[1]
            ps.pose.position.z = self._forward_altitude
            ps.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
            circle.append(ps)
        
        dipping = PoseStamped()
        dipping.header.frame_id = self._drone_state.MAP_FRAME
        dipping.pose.position.x = circle[0].pose.position.x
        dipping.pose.position.y = circle[0].pose.position.y
        dipping.pose.position.z = self._dipping_altitude

        d1 = PoseStamped()
        d1.header.frame_id = self._drone_state.MAP_FRAME
        d1.pose.position.x = circle[-1].pose.position.x
        d1.pose.position.y = circle[-1].pose.position.y
        d1.pose.position.z = self._raising_altitude/5.0

        d2 = PoseStamped()
        d2.header.frame_id = self._drone_state.MAP_FRAME
        d2.pose.position.x = circle[-1].pose.position.x
        d2.pose.position.y = circle[-1].pose.position.y
        d2.pose.position.z = self._raising_altitude/2.0

        d3 = PoseStamped()
        d3.header.frame_id = self._drone_state.MAP_FRAME
        d3.pose.position.x = circle[-1].pose.position.x
        d3.pose.position.y = circle[-1].pose.position.y
        d3.pose.position.z = self._raising_altitude

        self._points = [dipping]+circle+circle+[d1, d2 ,d3]
        

    def _prepare_loop(self) -> None:
        self._reset()
        if self._recover_without_buoy:
            self._points_without_buoy()
        else:
            self._points_with_buoy()


    def _loop_inner(self) -> bool|None:
        """
        Return True to indicate success, False for failure, or None to continue
        """
        if self._drone_state.drone_in_map is None:
            self._loginfo("No odom received yet, cannot perform recovery...")
            return False
        
        if self._wp_index == 0:
            self._loginfo(f"Starting recovery, moving to first waypoint of {len(self._points)}. Will use buoy: {not self._recover_without_buoy}")
        
        if self._wp_index >= len(self._points):
            self._loginfo("Recovery complete!")
            return True
        
        target_point = self._points[self._wp_index]
        distance_to_target = self.compute_distance(self._drone_state.drone_in_map, target_point)
        if distance_to_target <= self.SETPOINT_TOLERANCE:
            self._loginfo(f"Reached waypoint {self._wp_index} at {str_posestamp(target_point)}, distance to target was {distance_to_target:.2f}m")
            self._wp_index += 1
            return None
        
        target_point.header.stamp = self._node.get_clock().now().to_msg()
        self._setpoint_pub.publish(target_point)
        self._loginfo(f"Moving to waypoint {self._wp_index} at {str_posestamp(target_point)}, distance to target is {distance_to_target:.2f}m")
        return None

        
    def _give_feedback(self) -> str:
        return f"Phase: {self._wp_index+1}/{len(self._points)}."


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