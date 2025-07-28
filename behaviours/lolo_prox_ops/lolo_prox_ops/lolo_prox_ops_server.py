import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion
from rclpy.time import Duration, Time
from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Empty
from lolo_msgs.msg import Topics as loloTopics
from smarc_msgs.msg import Topics as smarcTopics
from tf2_ros import Buffer, TransformException, TransformListener
import numpy as np
import time
import math
import json

import tf_transformations

from enum import Enum

class LoloProxOpsAction():
    #Enums

    class ACTION_PHASE(Enum):
        STANDBY = 0 # Do nothing
        LOITER = 1 # Loiter underwater and wait for a position fix from the docking station
        LONG_DISTANCE = 2 # Drive towards the docking station
        SHORT_DISTANCE = 3 # Close range including speed control?
        DONE = 4 # We have received a "success" and will stop the action

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
        self.robot_position_time = None #robot position time to be compared with current time
        self.robot_altitude = None #altitude over seafloor in meters [Float32]
        self.target_position = PoseStamped() #target position [geometry_msgs/msg/Pose]
        self.target_position_time = None #node time to be compared with current time
        self.current_loiter_point_index=0 #Index of current loiter point    
        self.loiter_points = []

        #Target frame
        #self.frame_id = 'map_gt'
        self.frame_id = 'lolo/odom'

        #Settings etc
        self.target_tol = 5 #tolerance when loitering
        self.timeout = 1800.0
        self.fast_rpm = 600.0
        self.slow_rpm = 300.0
        self.loiter_points = None
        self.loiter_depth = 0.0
        self.long_distance_depth = 0.0
        self.short_distance_depth = 0.0
        self.min_altitude = 0.0
        self.map = None #Occupancygrid

        #Initialize in the "Do nothing phase"
        self.current_action_phase = self.ACTION_PHASE.STANDBY
        
        #Time of action start to check for timeout
        self.action_started_time = None

        #Service clients
        self.srv_callback_group = ReentrantCallbackGroup()
        self.publisher_callback_group = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()
        self.set_map_cli = self._node.create_client(SetMap, 'set_map', callback_group=self.srv_callback_group)
        self.get_plan_cli = self._node.create_client(GetPlan, 'plan_path', callback_group=self.srv_callback_group)

        while not self.get_plan_cli.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().info('Waiting for set map service...')

        while not self.set_map_cli.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().info('Waiting for set map service...')

        # Publishers
        self.map_pub = self._node.create_publisher(OccupancyGrid, 'proxops/map',10, callback_group=self.publisher_callback_group)
        self.path_pub = self._node.create_publisher(Path, 'proxops/path',10, callback_group=self.publisher_callback_group)
        self.rpm_pub = self._node.create_publisher(Float32, loloTopics.RPM_SETPOINT, 10, callback_group=self.publisher_callback_group)
        self.yaw_pub = self._node.create_publisher(Float32, loloTopics.YAW_SETPOINT, 10, callback_group=self.publisher_callback_group)
        self.depth_pub = self._node.create_publisher(Float32, loloTopics.DEPTH_SETPOINT, 10, callback_group=self.publisher_callback_group)
        self.roll_pub = self._node.create_publisher(Float32, loloTopics.ROLL_SETPOINT, 10, callback_group=self.publisher_callback_group)

        # Subscribers
        self.altitude_sub = self._node.create_subscription(Float32, smarcTopics.ALTITUDE_TOPIC, self.altitude_callback,10, callback_group=self.subscriber_callback_group)
        self.target_sub = self._node.create_subscription(PoseStamped, 'proxops/target', self.target_callback,10, callback_group=self.subscriber_callback_group)
        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback,10, callback_group=self.subscriber_callback_group)
        self.done_sub = self._node.create_subscription(Empty, 'proxops/done', self.done_callback,10, callback_group=self.subscriber_callback_group)

        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it
        params = json.loads(goal_request['json-params'])

        self._node.get_logger().info(f"params: {params}")
        
        #Loiter points
        l1 = params['loiter_1']
        l2 = params['loiter_2']
        #Map boundary
        map_boundary = params['geofence']

        assert l1 is not None
        assert l2 is not None
        assert map_boundary is not None

        #Convert loiter points to local frame
        self.loiter_points = []
        self.loiter_points.append(self.latlon_to_local_frame(l1))
        self.loiter_points.append(self.latlon_to_local_frame(l2))
        #self.latlon_to_local_frame()

        
        #Create occupancy grid for path planner
        self.map = self.create_map(frame_id = self.frame_id, geofence = map_boundary)
        set_map_req = SetMap.Request()
        set_map_req.map = self.map

        #Send occupancy grid to path planner
        self._node.get_logger().info("Sending map to path planner service")

        future = self.set_map_cli.call_async(set_map_req)
        t = 0
        while not (future.done()):
            time.sleep(0.01)
            t += 1
            if(t > 100): #1s timeout
                future.cancel()
                break
        result = future.result()
        
        if(result is not None ): 
            self._node.get_logger().info('Map set successfully')
            
            #Publish map for logging
            self.map_pub.publish(self.map)
            return True
        
        self._node.get_logger().info('Failed to set map. Will not accept goal')
        return False
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it
        self.current_action_phase = self.ACTION_PHASE.STANDBY
        return True
    
    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal
        self.action_started_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        self.current_action_phase = self.ACTION_PHASE.LOITER

    def _loop_inner(self) -> bool | None:
        # Here you would typically perform the main logic of the action
        # Return True to indicate success, False for failure, or None to continue
        # This is run after _prepare_loop call at "loop_frequency" Hz

        #Check for timeout
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = (time_now - self.action_started_time)
        if(runtime > self.timeout):
            return False # Failure

        #Do different things depending on action phase
        if(self.current_action_phase == self.ACTION_PHASE.STANDBY):
            self._node.get_logger().error("Something went wrong.")
            return False # Failure
        if(self.current_action_phase == self.ACTION_PHASE.DONE):
            self._node.get_logger().info("Action success.")
            return True # Success

        #if docking station location is unknown current_action_pahse -> LOITER
        #if distance to docking station==far away current_action_pahse -> LONG_DISTANCE
        #if distance to docking station==close away current_action_pahse -> SHORT_DISTANCE

        if(self.robot_position is None or (time_now - self.robot_position_time) > 10):
            self._node.get_logger().error("ERROR no robot position")
            return None

        if(self.target_position == None or self.target_position_time == None): 
            self.current_action_phase = self.ACTION_PHASE.LOITER
        elif(time_now - self.target_position_time > 10):
            self.current_action_phase = self.ACTION_PHASE.LOITER
        else:
            #TODO integrate target position..
            dist = self.calculate_distance(self.robot_position, self.target_position)
            if(dist > 20): self.current_action_phase = self.ACTION_PHASE.LONG_DISTANCE
            else: self.current_action_phase = self.ACTION_PHASE.SHORT_DISTANCE
            
            

        if(self.current_action_phase == self.ACTION_PHASE.LOITER):
            # We will plan a path every X loops that keeps lolo inside the geofenced area
            # Preferable as far away from the corners as possible to avoid running aground
            # Send a course for lolo to lolo corresponding to a point in the path ~10s in the future
            # Set RPM=Slow

            #Calculate distance to our current loiter target and change target if we are close enough to switch to the next one
            if(self.calculate_distance(self.robot_position, self.loiter_points[self.current_loiter_point_index]) < self.target_tol):
                self.current_loiter_point_index = (self.current_loiter_point_index+1) % len(self.loiter_points)

            #TESTING
            #self.robot_position = self.loiter_points[self.current_loiter_point_index]
            #self.current_loiter_point_index = (self.current_loiter_point_index+1) % len(self.loiter_points)

            #Plan a path to the next loiter point
            result = self.plan_path(self.robot_position, self.loiter_points[self.current_loiter_point_index])
            
            if(result is not None ): 
                self._node.get_logger().info("Plan path successful")
                #Publish path and map for logging
                self.path_pub.publish(result)
                self.map_pub.publish(self.map)

                yaw_setpoint = Float32()
                roll_setpoint = Float32()
                depth_setpoint = Float32()
                rpm_setpoint = Float32()

                yaw_setpoint.data = self.get_yaw_from_path(self.robot_position, result)
                roll_setpoint.data = 0.0
                depth_setpoint.data = self.get_depth_setpoint(self.loiter_depth)
                rpm_setpoint.data = self.slow_rpm
                self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))

                #publish setpoints
                self.rpm_pub.publish(rpm_setpoint)
                self.yaw_pub.publish(yaw_setpoint)
                self.depth_pub.publish(depth_setpoint)
                self.roll_pub.publish(roll_setpoint)

            else: 
                self._node.get_logger().error("Failed to plan path")
                return False #FAIL

        if(self.current_action_phase == self.ACTION_PHASE.LONG_DISTANCE):
            # Plan a path that goes to a point 10m ahead of the docking station
            # Send yaw = 10s into the future in the path
            # Set RPM = Fast

            #Plan a path to the next loiter point
            path = self.plan_path(self.robot_position, self.target_position)
            if(path is not None ): 
                self._node.get_logger().info("Plan path successful")
                #Publish path and map for logging
                self.path_pub.publish(path)
                self.map_pub.publish(self.map)

                yaw_setpoint = Float32()
                roll_setpoint = Float32()
                depth_setpoint = Float32()
                rpm_setpoint = Float32()

                yaw_setpoint.data = self.get_yaw_from_path(self.robot_position, path)
                roll_setpoint.data = 0.0
                depth_setpoint.data = self.get_depth_setpoint(self.long_distance_depth)
                rpm_setpoint.data = self.fast_rpm
                self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))

                #publish setpoints
                self.rpm_pub.publish(rpm_setpoint)
                self.yaw_pub.publish(yaw_setpoint)
                self.depth_pub.publish(depth_setpoint)
                self.roll_pub.publish(roll_setpoint)
            else: 
                self._node.get_logger().error("Failed to plan path")
                return False #FAIL
            pass

        if(self.current_action_phase == self.ACTION_PHASE.SHORT_DISTANCE):
            # Set target yaw = docking station + 10m ahead
            # Set RPM = SLOW if distance to target < 2m
            # Set RPM = FAST if distance to target < 4m

            yaw_setpoint = Float32()
            roll_setpoint = Float32()
            depth_setpoint = Float32()
            rpm_setpoint = Float32()

            projected_target = self.integrate_pose(self.target_position,10)

            yaw_setpoint.data = self.get_angle_between_points(self.robot_position, projected_target)
            roll_setpoint.data = 0.0
            depth_setpoint.data = self.get_depth_setpoint(self.short_distance_depth)
            rpm_setpoint.data = self.slow_rpm if self.calculate_distance(self.robot_position, projected_target) < 3 else self.fast_rpm
            self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))
            
            #publish setpoints
            self.rpm_pub.publish(rpm_setpoint)
            self.yaw_pub.publish(yaw_setpoint)
            self.depth_pub.publish(depth_setpoint)
            self.roll_pub.publish(roll_setpoint)

        return None
    
    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = time_now - self.action_started_time

        feedback = f"Action runtime: {runtime}. Current phase: {self.current_action_phase.name}"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback
   
    def calculate_distance(self, pose1:PoseStamped, pose2:PoseStamped) -> float:
        dx = pose1.pose.position.x - pose2.pose.position.x
        dy = pose1.pose.position.y - pose2.pose.position.y
        return math.sqrt(dx*dx + dy*dy)

    def get_yaw_from_path(self, start_pose:PoseStamped, path : Path) -> float: 

        if(len(path.poses) < 4):
            self._node.get_logger().Error("Path too short: " +str(len(path.poses)))
            return self.get_yaw_from_posestamped(start_pose)
        


        yaw1 = self.get_angle_between_points(path.poses[1], path.poses[2]) #1st  pose
        yaw2 = self.get_angle_between_points(path.poses[2], path.poses[3]) #2nd pose

        d = yaw2-yaw1

        self._node.get_logger().info("current yaw: : " +str(math.degrees(self.get_yaw_from_posestamped(start_pose))))
        self._node.get_logger().info("Yaw1: : " +str(math.degrees(yaw1)))
        self._node.get_logger().info("Yaw2: : " +str(math.degrees(yaw2)))

        if(d < -math.pi): d+=2*math.pi
        if(d > math.pi): d-=2*math.pi

        return yaw2 + d*2
        #turn = 0
        #if(d < math.radians(2.5)): turn = -1
        #if(d > math.radians(2.5)): turn = 1
        #return yaw1 + turn
    
    def get_yaw_from_posestamped(self, ps:PoseStamped) -> float: 
        orientation_q = ps.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
        #self._node.get_logger().error("roll pitch yaw: " +str(math.degrees(roll)) +", "+str(math.degrees(pitch))+", "+str(math.degrees(yaw)))
        return yaw

    def get_angle_between_points(self, p1:PoseStamped, p2:PoseStamped):
        dx = p2.pose.position.x - p1.pose.position.x
        dy = p2.pose.position.y - p1.pose.position.y
        return math.atan2(dy,dx)

    def integrate_pose(self,p:PoseStamped, m:float ) -> PoseStamped:
        yaw = self.get_yaw_from_posestamped(p)
        p.pose.position.x += m*math.cos(yaw)
        p.pose.position.y += m*math.sin(yaw)
        return p

    def get_depth_setpoint(self, target_depth) -> float:
        #return a good depth setpoint based on target depth and minimum altitude
        return min(target_depth, (-self.robot_position.pose.position.z + self.robot_altitude) - self.min_altitude)

    def plan_path(self, _start, _goal):
        """
        Plan a path from start to goal
        """
        #Service requst
        req = GetPlan.Request()
        #Start position
        req.start = _start
        #Goal position
        req.goal = _goal

        future = self.get_plan_cli.call_async(req)
        t = 0
        while not (future.done()):
            time.sleep(0.01)
            t += 1
            if(t > 100):
                future.cancel()
                break
        if(future.result() != None):
            return future.result().plan
        return None

    def create_map(self, frame_id, geofence) -> OccupancyGrid:
        """
        Create an occupancygrid with free and occupied regions based on the geofence given in the goal
        """

        #Convert points
        boundary = [self.latlon_to_local_frame(point) for point in geofence]

        minx = math.inf
        miny = math.inf
        maxx = -math.inf
        maxy = -math.inf
        for i in range(len(boundary)):
            minx = min(minx, boundary[i].pose.position.x)
            miny = min(miny, boundary[i].pose.position.y)
            maxx = max(maxx, boundary[i].pose.position.x)
            maxy = max(maxy, boundary[i].pose.position.y)

        self._node.get_logger().error("coordinates of map: (" + str(minx) + ", " + str(miny) + ") (" + str(maxx) + ", " + str(maxy) + ")")

        gridmap = OccupancyGrid()
        gridmap.header.stamp = self._node.get_clock().now().to_msg()
        gridmap.header.frame_id = frame_id
        gridmap.info.height = int(maxy-miny)+1
        gridmap.info.width = int(maxx-minx)+1
        gridmap.info.resolution = 1.0
        gridmap.info.origin.position.x = minx
        gridmap.info.origin.position.y = miny
        gridmap.info.origin.position.z = 0.0

        gridmap.data = [-1]*(gridmap.info.width*gridmap.info.height)

        for x in range(gridmap.info.width):
            for y in range(gridmap.info.height):
                if(not self.is_inside_boundary(gridmap.info.origin.position.x + x,gridmap.info.origin.position.y + y, boundary)):
                    gridmap.data[x + y*gridmap.info.width] = 100
                else:
                    gridmap.data[x + y*gridmap.info.width] = 0
        return gridmap

    def is_inside_boundary(self, x : float,y : float, boundary: list) -> bool:
        c = False
        l = len(boundary)
        for i in range(l):
            pi = boundary[i].pose.position
            piplus = boundary[(i+1) % l].pose.position
            if( ((piplus.x>x) != (pi.x>x)) and
                (y < (pi.y-piplus.y) * (x-piplus.x) / (pi.x-piplus.x) + piplus.y) ):
                c = not c
        return c

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

        #Add yaw
        quaternion_values = tf_transformations.quaternion_from_euler(0,0,yaw)
        pose_stamp.pose.orientation.x = quaternion_values[0]
        pose_stamp.pose.orientation.y = quaternion_values[1]
        pose_stamp.pose.orientation.z = quaternion_values[2]
        pose_stamp.pose.orientation.w = quaternion_values[3]

        t = self._tf_buffer.lookup_transform(
                target_frame=self.frame_id,
                source_frame=pose_stamp.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1),
            )
        return do_transform_pose_stamped(pose_stamp, t)

    #Subscriber callback functions
    def target_callback(self,msg:PoseStamped):
        #self._node.get_logger().info("target position received.")
        if(msg.header.frame_id != self.frame_id):
            self._node.get_logger().info("Target is not in the coorrect frame")
            return
        self.target_position = msg
        self.target_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)

    def robot_odom_callback(self,msg : Odometry):
        #self._node.get_logger().info("robot position updated.")
        self.robot_position = PoseStamped()
        self.robot_position.header = msg.header
        self.robot_position.pose = msg.pose.pose
        self.robot_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        #self._node.get_logger().info("" + str(msg.header.frame_id))

    def altitude_callback(self,msg):
        self.robot_altitude = msg.data

    def done_callback(self,msg):
        self._node.get_logger().info("Done message received")
        self.current_action_phase = self.ACTION_PHASE.DONE

    def testcase(self):

        self.robot_altitude = 3

        #Set robot position
        robot_yaw_rad = 1
        robot_pitch_rad = 0
        robot_roll_rad = 0
        pose_quaternion_values = tf_transformations.quaternion_from_euler(robot_roll_rad,
                                                                          robot_pitch_rad,
                                                                          robot_yaw_rad)
        self.robot_position.header.frame_id = 'map'
        self.robot_position.header.stamp = self._node.get_clock().now().to_msg()
        self.robot_position.pose.orientation.x = pose_quaternion_values[0]
        self.robot_position.pose.orientation.y = pose_quaternion_values[1]
        self.robot_position.pose.orientation.z = pose_quaternion_values[2]
        self.robot_position.pose.orientation.w = pose_quaternion_values[3]
        self.robot_position.pose.position.x = 50.0
        self.robot_position.pose.position.y = 50.0
        self.robot_position.pose.position.z = 0.0

        #set target position
        target_yaw_rad = -1
        target_pitch_rad = 0
        target_roll_rad = 0
        target_quaternion_values = tf_transformations.quaternion_from_euler(target_roll_rad,
                                                                          target_pitch_rad,
                                                                          target_yaw_rad)
        self.target_position.header.frame_id = 'map'
        self.target_position.pose.orientation.x = target_quaternion_values[0]
        self.target_position.pose.orientation.y = target_quaternion_values[1]
        self.target_position.pose.orientation.z = target_quaternion_values[2]
        self.target_position.pose.orientation.w = target_quaternion_values[3]
        self.target_position.pose.position.x = 50.0
        self.target_position.pose.position.y = 70.0
        self.target_position.pose.position.z = 0.0
        
        #TODO geofence

        #Points to be used for loitering when no target is in sight
        self.loiter_points = []

        l1 = PoseStamped()
        l1.header.frame_id = 'map'
        l1.header.stamp = self._node.get_clock().now().to_msg()
        l1_q = tf_transformations.quaternion_from_euler(0,
                                                        0,
                                                        math.radians(225))
        l1.pose.orientation.x = l1_q[0]
        l1.pose.orientation.y = l1_q[1]
        l1.pose.orientation.z = l1_q[2]
        l1.pose.orientation.w = l1_q[3]
        l1.pose.position.x = 20.0
        l1.pose.position.y = 20.0
        l1.pose.position.z = 0.0
        self.loiter_points.append(l1)

        l2 = PoseStamped()
        l2.header.frame_id = 'map'
        l2.header.stamp = self._node.get_clock().now().to_msg()
        l2_q = tf_transformations.quaternion_from_euler(0,
                                                        0,
                                                        math.radians(45))
        l2.pose.orientation.x = l2_q[0]
        l2.pose.orientation.y = l2_q[1]
        l2.pose.orientation.z = l2_q[2]
        l2.pose.orientation.w = l2_q[3]
        l2.pose.position.x = 80.0
        l2.pose.position.y = 80.0
        l2.pose.position.z = 0.0
        self.loiter_points.append(l2)


def main():
    rclpy.init()
    node = Node("lolo_prox_ops_action")
    
    action_client = LoloProxOpsAction(node, "lolo_prox_ops")
    
    action_client.testcase()
    

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down lolo prox ops acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
