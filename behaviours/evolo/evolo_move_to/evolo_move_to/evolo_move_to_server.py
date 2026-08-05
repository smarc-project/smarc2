import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped

from transforms3d.euler import euler2quat

from rclpy.time import Duration, Time
from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist
from geometry_msgs.msg import PoseStamped, PointStamped
from std_msgs.msg import Float32, Empty
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as controlTopics
from tf2_ros import Buffer, TransformException, TransformListener
import math
from evolo_controllers.control import PID

import numpy as np
import math


class EvoloMoveTo():


    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        # Initialize the action server with the node and action name
        # Give it all the necessary callbacks
        self._as = GentlerActionServer(
            node,
            action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=2
        )

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself

        # Tf listener
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )

        # State variables. gets updated from topic callbacks
        self.robot_position = PoseStamped() #robot positon [geometry_msgs/msg/Pose]
        self.robot_speed = 0 #Speed in m/s
        self.robot_position_time = None #robot position time to be compared with current time
        self.target_position = PoseStamped() #target positon [geometry_msgs/msg/Pose]
        self.distance_to_target = None
        self.start_location = PoseStamped()

        #Target frame
        #self.frame_id = 'map_gt'
        self.frame_id = 'evolo/odom'

        #Settings etc
        self.target_tol = 10 #Waypoint tolerance
        self._node.declare_parameter('target_radius', 10)
        self.target_tol = float(self._node.get_parameter('target_radius').value)

        self._node.declare_parameter('timeout', 1800)
        self.timeout = float(self._node.get_parameter('timeout').value)

        self._node.declare_parameter('use_xte', True)
        self.use_xte_compensation = self._node.get_parameter('use_xte').get_parameter_value().bool_value

        self._node.declare_parameter('aim_ahead_dist_max', 40)
        self.aim_ahead_dist_m = float(self._node.get_parameter('aim_ahead_dist_max').value)
        self.aim_ahead_dist_m = max(0,min(40,self.aim_ahead_dist_m))

        #PID parameters
        #Closed loop gains
        self._node.declare_parameter("xte_pid_p", 0.2)
        self._node.declare_parameter("xte_pid_i", 0.1)
        self._node.declare_parameter("xte_pid_d", 1.0)
        self._node.declare_parameter("xte_pid_max_integral", 5.0)
        self._node.declare_parameter("xte_pid_max_output", 10.0) 
        
        self.xte_pid_p = float(self._node.get_parameter("xte_pid_p").value)
        self.xte_pid_i = float(self._node.get_parameter("xte_pid_i").value)
        self.xte_pid_d = float(self._node.get_parameter("xte_pid_d").value)
        self.xte_pid_max_integral = float(self._node.get_parameter("xte_pid_max_integral").value)
        self.xte_pid_max_output = float(self._node.get_parameter("xte_pid_max_output").value)

        self.PID = PID(self.xte_pid_p,
                       self.xte_pid_i,
                       self.xte_pid_d,
                       self.xte_pid_max_output,
                       self.xte_pid_max_integral)

        self.max_speed = 8.0        
        
        #Time of action start to check for timeout
        self.action_started_time = None
        
        #Callback groups
        self.publisher_callback_group = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()

        # Publishers
        self.evolo_pub = self._node.create_publisher(Odometry, evoloTopics.EVOLO_CONTROL_PLANNED, 10, callback_group=self.publisher_callback_group)
        self.target_pub = self._node.create_publisher(PointStamped, evoloTopics.EVOLO_CURRENT_WP, 10, callback_group=self.publisher_callback_group)
        # Subscribers
        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback,10, callback_group=self.subscriber_callback_group)
        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it
        #params = json.loads(goal_request['json-params'])

        speed = goal_request['speed']
        waypoint = goal_request['waypoint']

        try:
            speed = float(speed)
        except Exception as e:
            self._node.get_logger().info(f"Tried to parse speed as float. Did not work: {speed}, {e}")
            if(speed == "slow"): speed = 2.0
            elif(speed == "standard"): speed = 4.9
            elif(speed == "fast"): speed = 6
            else: speed = 0.0

        assert type(speed) == float

        self._node.get_logger().info(f"speed: {speed}, waypoint: {waypoint}")

        #if 'timeout' in params.keys() : self.timeout = min(3600, max(1, params['timeout']))
        #self.timeout = 600
        #self._node.get_logger().info('timeout: ' + str(self.timeout))

        #Compute target position from lat lon
        lat = float(waypoint['latitude'])
        lon = float(waypoint['longitude'])
        #self._node.get_logger().info(f"lat lon sent to function: {lat}, {lon}")
        self.target_position = self.latlon_to_local_frame([lat,lon])
        self.target_speed = speed
        return True
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it
        #TODO send speed=stop
        return True
    
    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal
        self.action_started_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        #self.PID.reset()

        #Save start location so it can be used in XTE calculation
        self.start_location = self.robot_position
        return None

    def _loop_inner(self) -> bool | None:
        # Here you would typically perform the main logic of the action
        # Return True to indicate success, False for failure, or None to continue
        # This is run after _prepare_loop call at "loop_frequency" Hz

        #Check for timeout
        time_now = self._node.get_clock().now().nanoseconds * 1e-9
        runtime = (time_now - self.action_started_time)
        if(runtime > self.timeout):
            return False # Failure

        if(self.robot_position is None or (time_now - self.robot_position_time) > 10):
            self._node.get_logger().error("ERROR no robot position")
            return False

        #Calculate distance to our target and return true (success) if we are close to it
        self.distance_to_target = self.calculate_distance(self.robot_position, self.target_position)
        if(self.distance_to_target < self.target_tol):
            #TODO send speed = Stop
            return True

        if(self.use_xte_compensation and self.robot_speed > 0.514444444*7): #Only use XTE when foiling
            # XTE math. (Coordinate system is in meters)
            #(1) create local coordinate system start_pos = origin
            goalX = self.target_position.pose.position.x - self.start_location.pose.position.x
            goalY = self.target_position.pose.position.y - self.start_location.pose.position.y
            currentX = self.robot_position.pose.position.x - self.start_location.pose.position.x
            currentY = self.robot_position.pose.position.y - self.start_location.pose.position.y

            #(2) project current position on the line between start and goal

            #normalized vector from start to goal n=[nx,ny]
            dist_total = math.sqrt(goalX*goalX + goalY*goalY)
            nx = goalX / dist_total
            ny = goalY / dist_total

            # current pos projected on line p=[px,py]
            dist_from_start = nx*currentX + ny*currentY; #dot product
            px = nx*dist_from_start
            py = ny*dist_from_start

            #Check if the point p is actually between start and goal
            f = nx*px + ny*py
            case = 0 # 0 = between start and goal, 1 = before the start point, 2 = after the end point
            if(f < 0): case = 1
            if(f > dist_total): case = 2

            if(case == 0): #Closest point is on the line between start and goal
                self._node.get_logger().info("Steering using XTE")

                #Calcualte XTE error
                dx_xte = px -currentX
                dy_xte = py -currentY
                xte_m = math.sqrt(dx_xte*dx_xte + dy_xte*dy_xte)
                
                #Calcuale sign of XTE error using cross product
                cross = (goalX - 0.0) * (currentY - 0.0) - (goalY - 0.0) * (currentX - 0.0)
                sign = 1.0 if cross < 0 else -1.0 #positive if current pos is to the right of the line
                xte_m*=sign

                xte_pid_output_deg = self.PID.update_error(xte_m, time_now)
                xte_pid_outpud_rad = math.radians(xte_pid_output_deg)               
                self._node.get_logger().info(f"XTE PID output {xte_pid_output_deg}")

                #move projected point on the line
                dist_to_goal = dist_total - dist_from_start; # m left to goal
                dist_to_move = self.aim_ahead_dist_m * (self.robot_speed / (0.514444444*15)) #15kn = move target aim_ahead_distance
                dist_to_move = min(dist_to_goal, dist_to_move) # Don't move the target past goal

                px += nx*dist_to_move
                py += ny*dist_to_move
                self._node.get_logger().info(f"Moving target along rumbline: {dist_to_move} meters")
            elif(case == 1): #target = start point
                self._node.get_logger().info("Steering towards start point")
                px = 0
                py = 0
                xte_pid_outpud_rad = 0
                self.PID.reset()
            else : #target = goal point
                self._node.get_logger().info("Steering towards goal point")
                px = goalX
                py = goalY
                xte_pid_outpud_rad = 0
                self.PID.reset()

            #Calcualte yaw to the target position
            # targetpos = origin + proected target position
            target_pos_x = self.start_location.pose.position.x + px
            target_pos_y = self.start_location.pose.position.y + py
            self._node.get_logger().info(f"target location: x={target_pos_x}, y={target_pos_y}")

            dx = target_pos_x - self.robot_position.pose.position.x
            dy = target_pos_y - self.robot_position.pose.position.y
            targetYaw = math.atan2(dy,dx) # yaw in ENU

            #Add PID output
            targetYaw += xte_pid_outpud_rad
            #Unwrap
            if(targetYaw > 2*math.pi): targetYaw -= 2*math.pi
            if(targetYaw < 0): targetYaw += 2*math.pi
            

        else: #no XTE compensation
            self._node.get_logger().info("No XTE compensation")
            dx = self.target_position.pose.position.x - self.robot_position.pose.position.x
            dy = self.target_position.pose.position.y - self.robot_position.pose.position.y
            targetYaw = math.atan2(dy,dx) # yaw in ENU
        

        target_quaternion = euler2quat(0,0,targetYaw, axes='sxyz')
        control_msg = Odometry()
        control_msg.header.stamp    = self._node.get_clock().now().to_msg()
        control_msg.header.frame_id = self.frame_id
        control_msg.child_frame_id = "evolo/base_link"
        control_msg.pose.pose.orientation.x = target_quaternion[1]
        control_msg.pose.pose.orientation.y = target_quaternion[2]
        control_msg.pose.pose.orientation.z = target_quaternion[3]
        control_msg.pose.pose.orientation.w = target_quaternion[0]
        control_msg.twist.twist.linear.x  = self.target_speed
        self.evolo_pub.publish(control_msg)

        #Publish current waypoint
        target_point = PointStamped()
        target_point.header = self.target_position.header
        target_point.point = self.target_position.pose.position 
        self.target_pub.publish(target_point)

        return None
    
    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = time_now - self.action_started_time

        feedback = f"Action runtime: {runtime}. DTT: {self.distance_to_target}"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback
   
    def calculate_distance(self, pose1:PoseStamped, pose2:PoseStamped) -> float:
        dx = pose1.pose.position.x - pose2.pose.position.x
        dy = pose1.pose.position.y - pose2.pose.position.y
        return math.sqrt(dx*dx + dy*dy)

    
    def latlon_to_local_frame(self, point_list: list) -> PoseStamped:

        geopoint = GeoPoint()
        geopoint.latitude = point_list[0]
        geopoint.longitude = point_list[1]
        geopoint.altitude = 0.0
        yaw = math.radians(point_list[2]) if len(point_list) > 2 else 0.0


        point: utm.UTMPoint = utm.fromMsg(geopoint)
        pose_stamp = PoseStamped()
        pose_stamp.pose.position = point.toPoint()
        zone, band = point.gridZone()
        pose_stamp.header.frame_id = f"utm_{zone}_{band}"

        self._node.get_logger().info(f"Utmpoint: {point}")

        #Add yaw
        quaternion_values = euler2quat(0,0,yaw, axes='sxyz')
        pose_stamp.pose.orientation.x = quaternion_values[1]
        pose_stamp.pose.orientation.y = quaternion_values[2]
        pose_stamp.pose.orientation.z = quaternion_values[3]
        pose_stamp.pose.orientation.w = quaternion_values[0]

        t = self._tf_buffer.lookup_transform(
                target_frame=self.frame_id,
                source_frame=pose_stamp.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1),
            )
        return do_transform_pose_stamped(pose_stamp, t)

    #Subscriber callback functions
    def robot_odom_callback(self,msg : Odometry):
        #self._node.get_logger().info("robot position updated.")
        self.robot_position = PoseStamped()
        self.robot_position.header = msg.header
        self.robot_position.pose = msg.pose.pose
        self.robot_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        self.robot_speed = msg.twist.twist.linear.x
        #self._node.get_logger().info("" + str(msg.header.frame_id))

    def testcase(self):
        pass


def main():
    rclpy.init()
    node = Node("evolo_move_to_action_server")
    
    action_client = EvoloMoveTo(node, "move_to")
    
    #action_client.testcase()
    

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down evolo move to acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
