#!/usr/bin/python
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import  PointStamped, PoseStamped
from smarc_utilities.georef_utils import convert_latlon_to_utm
from alars_auv_search_planner.search_planner_controller import SearchPlannerController
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from smarc_action_base.gentler_action_server import GentlerActionServer
import traceback

class SearchPlannerAction():
    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node
        self.spcontroller = SearchPlannerController()
        self.point_publisher = self._node.create_publisher(
            msg_type = PoseStamped,
            topic = self.spcontroller.model_params['topics.move_drone'], 
            qos_profile= 10)

        # Initialize the action server with the node and action name
        # Give it all the necessary callbacks
        self._as = GentlerActionServer(
            node,
            "alars_search",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 1/self.spcontroller.model_params['grid_map.update.rate'] # loop frequency defined by grid map update frequency
        )

        # Subscribe from detection topic to know when to stop search
        try:
            self._node.create_subscription(PointStamped, 
                                        self.spcontroller.model_params["topics.sam_detection"],
                                        self._sam_detection_callback,
                                        10)
        except:
            self._node.get_logger().error("Sam detection topic wasn't updated on search_planner_controller.py (check TODO). Waiting for dji_msgs.Topics.msg to be updated.")

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself
        self.MAP_SEEN_MAX = 80
        self._radius = 0
        self._gps = None
        self._reset_search()

    def _reset_search(self):
        self.sam_position = None
        self.map_seen = 0
        self.spcontroller.init_done = False

    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        Here you would typically validate the goal request
        Return True to accept the goal, False to reject it
        """ 
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        self._gps = GeoPoint()
        self._radius = 0

        try:
            p = goal_request['search_position']
            self._gps.latitude = p['latitude']
            self._gps.longitude = p['longitude']
            self._gps.altitude = float(p['altitude'])
            self._radius = float(p['tolerance'])
            if self._radius <= 0:
                self._node.get_logger().error('Action goal had invalid radius(tolerance) value!')
                return False
            if self._gps.altitude <= 0:
                self._node.get_logger().error('Action goal had negative altitude value!')
                return False

        except:
            self._node.get_logger().error('Action goal could not be parsed?') 
            return False

        self._node.get_logger().info(f"Accepted goal request with search position: {self._gps} and radius: {self._radius} m")
        return True

    
    
    def _on_cancel_received(self) -> bool:
        """
        Here you would typically handle the cancel request
        Return True to accept the cancel, False to reject it
        """
        self._node.get_logger().warn("Received cancel request, cancelling search")
        self._reset_search()
        return True

    
    def _prepare_loop(self) -> None:
        """
        Here you would typically set up any necessary state or resources
        This is run once before the loop starts, after you accept the goal
        """
        self._node.get_logger().info("Preparing loop for search action execution")
        if self._gps is None:
            self._node.get_logger().error("Search position (self._gps) was None at _prepare_loop!")
            return

        self._reset_search()

        # if activated by client, quadrotor doesn't perform initial movement (assigning purposes only)
        self.spcontroller.drone_init_pos = PointStamped()
        self.spcontroller.drone_init_pos.header.frame_id = self.spcontroller.model_params['frames.id.quadrotor_odom']      

        # get search radius (range) and altitude 
        self.spcontroller.grid_map.w = self.spcontroller.grid_map.h = 2*self._radius
        self.spcontroller.planner.flight_height = self.spcontroller.planner.grid_map.flight_height = self._gps.altitude
        GPS_ping_utm = convert_latlon_to_utm(self._gps)
        self.spcontroller.GPS_ping = self.spcontroller.planner.transform_point(GPS_ping_utm, self.spcontroller.model_params['frames.id.map'])

        # (re)initialize planner (including grid map)
        self.spcontroller.grid_map.GPS_ping = self.spcontroller.GPS_ping
        self.spcontroller.reinitialize_search()

    def _loop_inner(self) -> bool | None:
        """ 
        Here you would typically perform the main logic of the action
        Return True to indicate success, False for failure, or None to continue
        This is run after _prepare_loop call at "loop_frequency" Hz
        """

        if round(self.map_seen*100,2) >= self.MAP_SEEN_MAX :
            self._node.get_logger().warn(f"{self.MAP_SEEN_MAX} % of the map was seen without finding auv, failing search!")
            self._reset_search()
            return False
        elif self.sam_position is not None:
            self._node.get_logger().warn("SAM was detected, search success!")
            self._reset_search()
            return True
        
        # Update planner and grid map ()
        try:
            self.map_seen = self.spcontroller.update_grid_map()
        except Exception as e:
            self._node.get_logger().warn("### update_grid_map failed, failing action")
            self._node.get_logger().warn(str(e))
            self._node.get_logger().warn(traceback.format_exc())
            self._reset_search()
            return False
        
        try:
            pose2pub = self.spcontroller.update_path()
        except Exception as e:
            self._node.get_logger().warn("### update_path failed, failing action")
            self._node.get_logger().warn(str(e))
            self._node.get_logger().warn(traceback.format_exc())
            self._reset_search()
            return False
        
        try:
            if pose2pub is not None: 
                if pose2pub.header.stamp.sec == 0 and pose2pub.header.stamp.nanosec == 0:
                    pose2pub.header.stamp = self._node.get_clock().now().to_msg()
                self.point_publisher.publish(pose2pub)
        except Exception as e:
            self._node.get_logger().warn("### point_publisher failed, failing action")
            self._node.get_logger().warn(str(e))
            self._node.get_logger().warn(traceback.format_exc())
            self._reset_search()
            return False

        # everything went well, continue search
        return None
        
    
    def _give_feedback(self) -> str:
        feedback = f"{round(self.map_seen*100,2)} % of the map was seen"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback
    
    def _sam_detection_callback(self, msg):
        self._node.get_logger().info(f"SAM detected: {msg.point}")
        self.sam_position = msg




def main():
    rclpy.init()
    node = Node("search_auv_action_node")
    
    action = SearchPlannerAction(node, "alars_search")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.add_node(action.spcontroller)
    executor.add_node(action.spcontroller.planner)
    executor.add_node(action.spcontroller.planner.grid_map)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Search AUV Action server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()