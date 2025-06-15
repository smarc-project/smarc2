import rclpy, math


from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration

from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion, quaternion_from_euler


from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_utilities.georef_utils import convert_latlon_to_utm

from smarc_msgs.msg import Topics as SmarcTopics

from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped, PoseStamped

class SearchAndTrackAuvAction():
    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        self.log = node.get_logger().info
        
        self.ODOM_FRAME = "Quadrotor/odom"
        self.BASE_FRAME = "Quadrotor/base_link"
        self.SETPOINT_TOPIC = "move_to_setpoint"
        self.POINT_REACHED_DISTANCE = 0.3
        self.SPIRAL_ARM_DISTANCE = 0.5  # Distance between spiral arms in meters

        self._as = GentlerActionServer(
            node,
            action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=10.0
        )

        self._search_center_odom : PointStamped|None = None
        self._search_radius : float = 0.0
        self._keep_following : bool = False
        self._spiral_position : float|None = None


        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        self._feedback_str = "No feedback yet"

        self._setpoint_pub = self._node.create_publisher(
            PoseStamped,
            self.SETPOINT_TOPIC,
            10)
        
        self._auv_detection_sub = self._node.create_subscription(
            PointStamped,
            "alars_detection/auv",
            self._auv_detection_callback,
            10)
        
    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    

    def _auv_detection_callback(self, msg: PointStamped):
        #TODO
        pass


    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received goal request: {goal_request}")
        gp = goal_request['search_center']
        alt : float = gp['altitude']
        radius : float = gp['tolerance']

        try:
            if alt < 2.0:
                self._node.get_logger().error("Search center altitude must be > 2.0 meters")
                return False
            if alt > 10.0:
                self._node.get_logger().error("Search center altitude must be < 10.0 meters")
                return False
            if radius > 100.0:
                self._node.get_logger().error("Search tolerance must be < 100.0 meters")
                return False
            if radius < 0.0:
                self._node.get_logger().error("Search tolerance must be >= 0.0 meters")
                return False
        except:
            self._node.get_logger().error("Invalid goal request format!")
            return False
        
        center_gp = GeoPoint()
        center_gp.latitude = float(gp['latitude'])
        center_gp.longitude = float(gp['longitude'])
        center_gp.altitude = alt
        center_utm : PointStamped = convert_latlon_to_utm(center_gp)
        
        try:
            tf = self._tf_buffer.lookup_transform(
                self.ODOM_FRAME, 
                center_utm.header.frame_id, 
                Time(seconds=0),
                timeout=Duration(seconds=1)
            )
            ps = PoseStamped()
            ps.header = center_utm.header
            ps.pose.position = center_utm.point
            ps.pose.orientation.w = 1.0  # Set orientation to identity

            pnt = do_transform_pose_stamped(ps, tf)
            self._search_center_odom = PointStamped()
            self._search_center_odom.header = pnt.header
            self._search_center_odom.point = pnt.pose.position

        except Exception as e:
            self.log(f"Failed to transform search center from {center_utm.header.frame_id} to {self.ODOM_FRAME}: {e}")
            return False
        
        self._search_radius = radius
        self._keep_following = bool(goal_request['keep_following'])
        self._spiral_position = None

        self.log(f"Search center set to: {format_point_stamped(self._search_center_odom)}")
        self.log(f"Search radius set to: {self._search_radius} meters")
        return True

        
    

    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        return True
    

    def _prepare_loop(self) -> None:
        if self._search_center_odom is None:
            self._node.get_logger().error("Search center not set, cannot start action")
            return
        self._current_setpoint_odom: PoseStamped = PoseStamped()
        self._current_setpoint_odom.pose.position.x = self._search_center_odom.point.x
        self._current_setpoint_odom.pose.position.y = self._search_center_odom.point.y
        self._current_setpoint_odom.pose.position.z = self._search_center_odom.point.z
        self._current_setpoint_odom.header = self._search_center_odom.header
        

    def _update_current_setpoint_on_spiral(self):
        if self._spiral_position is None:
            self._spiral_position = 0

        if self._search_center_odom is None:
            self.log("Search center not set, cannot update spiral position")
            return
        
        spiral_x, spiral_y = point_on_spiral(self._spiral_position, base_radius=self.POINT_REACHED_DISTANCE, arm_distance=self.SPIRAL_ARM_DISTANCE)
        self._current_setpoint_odom.pose.position.x = spiral_x + self._search_center_odom.point.x
        self._current_setpoint_odom.pose.position.y = spiral_y + self._search_center_odom.point.y


    def _loop_inner(self) -> bool | None:
        if self._search_center_odom is None:
            self.log("Search center not set, cannot continue action")
            return False
        
        tf = self._tf_buffer.lookup_transform(
            self.BASE_FRAME, 
            self._current_setpoint_odom.header.frame_id, 
            Time(seconds=0),
            timeout=Duration(seconds=1)
        )
        current_setpoint_in_base = do_transform_pose_stamped(self._current_setpoint_odom, tf)
        # Calculate the magnitude (distance from origin) of the setpoint in the base frame
        pos = current_setpoint_in_base.pose.position
        dist_to_current_setpoint = math.sqrt(pos.x ** 2 + pos.y ** 2 + pos.z ** 2)
        if dist_to_current_setpoint < self.POINT_REACHED_DISTANCE:
            if self._spiral_position is not None:
                self._spiral_position += math.pi / 16
                self._update_current_setpoint_on_spiral()
            else:
                self.log("Reached search center, starting search")
                self._spiral_position = 0
                self._update_current_setpoint_on_spiral()

        # Check distance between current_setpoint_odom and search_center
        dx = self._current_setpoint_odom.pose.position.x - self._search_center_odom.point.x
        dy = self._current_setpoint_odom.pose.position.y - self._search_center_odom.point.y
        dz = self._current_setpoint_odom.pose.position.z - self._search_center_odom.point.z
        dist_from_center = math.sqrt(dx**2 + dy**2 + dz**2)
        if dist_from_center > self._search_radius:
            self.log(f"Current setpoint is outside search radius of {self._search_radius}m, search failed.")
            return False
        
        self._current_setpoint_odom.header.stamp = self.now_stamp
        self._setpoint_pub.publish(self._current_setpoint_odom)
        self._feedback_str = f"Remaining: {dist_to_current_setpoint:.2f}m"
        return None
    


    def _give_feedback(self) -> str:
        return self._feedback_str


def point_on_spiral(T_rad:float, base_radius:float=0, arm_distance:float=1) -> tuple[float, float]:
    r = base_radius + arm_distance * T_rad
    x = r * math.cos(T_rad)
    y = r * math.sin(T_rad)
    return x, y


def main():
    rclpy.init()
    node = Node("search_auv_action_node")
    
    SearchAndTrackAuvAction(node, "alars_search_and_follow")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Search AUV Action server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


def format_point_stamped(point: PointStamped|None) -> str:
        if( point is None):
            return "None"
        return f"(x={point.point.x:.3f}, y={point.point.y:.3f}, z={point.point.z:.3f}, frame_id={point.header.frame_id})"

def format_pose_stamped(pose: PoseStamped|None) -> str:
        if( pose is None):
            return "None"
        rpy = euler_from_quaternion([
            pose.pose.orientation.x,
            pose.pose.orientation.y,
            pose.pose.orientation.z,
            pose.pose.orientation.w
        ])
        return f"(x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}, z={pose.pose.position.z:.3f}, " \
               f"roll={math.degrees(rpy[0]):.3f}, pitch={math.degrees(rpy[1]):.3f}, yaw={math.degrees(rpy[2]):.3f}, " \
               f"frame_id={pose.header.frame_id})"
