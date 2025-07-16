import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer

from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
import numpy as np
import time
import math

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
        
        # State variables. gets updated from topic callbacks
        self.robot_position = PoseStamped() #robot positon [geometry_msgs/msg/Pose]
        self.robot_altitude = None #altitude over seafloor in meters [Float32]
        self.target_position = PoseStamped() #target position [geometry_msgs/msg/Pose]
        self.target_position_time = None #node time to be compared with current time
        self.current_loiter_point_index=0 #Index of current loiter point    

        #Settings etc
        self.target_tol = 5 #tolerance when loitering
        self.timeout = 600
        self.fast_rpm = 700
        self.slow_rpm = 500
        self.loiter_points = None
        self.loiter_depth = 5
        self.long_distance_depth = 4
        self.short_distance_depth = 2
        self.prox_ops_depth = 2
        self.min_altitude = 3
        self.map = None #Occupancygrid

        #Initialize in the "Do nothing phase"
        self.current_action_phase = self.ACTION_PHASE.STANDBY
        
        #Time of action start to check for timeout
        self.action_started_time = None

        #Service clients
        self.srv_callback_group = ReentrantCallbackGroup()
        self.set_map_cli = self._node.create_client(SetMap, 'set_map', callback_group=self.srv_callback_group)
        self.get_plan_cli = self._node.create_client(GetPlan, 'plan_path', callback_group=self.srv_callback_group)

        while not self.get_plan_cli.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().info('Waiting for set map service...')

        while not self.set_map_cli.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().info('Waiting for set map service...')

        # Publishers
        self.map_pub = self._node.create_publisher(OccupancyGrid, 'proxops/map',10)
        self.path_pub = self._node.create_publisher(Path, 'proxops/path',10)
        #self.rpm_pub
        #self.yaw_pub
        #self.depth_pub
        #self.roll_pub

        # Subscribers
        #altitude_sub
        self.target_sub = self._node.create_subscription(PoseStamped, 'proxops/target', self.target_callback,10)
        #'done'_sub

        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it

        #TODO parse input JSON
        #Check that the goal request contains all important parameters

        
        #Create occupancy grid for path planner
        self.map = self.create_map(frame_id = 'map', geofence = None)
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

        #Check if Lolo is outside the geofenced area
        #if(outside(self.geofence))
        #    return False # Failure

        #Do different things depending on action phase
        if(self.current_action_phase == self.ACTION_PHASE.STANDBY):
            self._node.get_logger().info("Something went wrong.")
            return False # Failure
        if(self.current_action_phase == self.ACTION_PHASE.DONE):
            self._node.get_logger().info("Action success.")
            return True # Success

        #TODO check if we the position of the docking station is known
        #if docking station location is unknown current_action_pahse -> LOITER
        #if distance to docking station==far away current_action_pahse -> LONG_DISTANCE
        #if distance to docking station==close away current_action_pahse -> SHORT_DISTANCE

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
            self.robot_position = self.loiter_points[self.current_loiter_point_index]
            self.current_loiter_point_index = (self.current_loiter_point_index+1) % len(self.loiter_points)

            #Plan a path to the next loiter point
            result = self.plan_path('map', self.robot_position, self.loiter_points[self.current_loiter_point_index])
            
            if(result is not None ): 
                self._node.get_logger().info("Plan path successful")
                #Publish map for logging
                self.path_pub.publish(result)

                yaw_setpoint = self.get_yaw_from_path(self.robot_position, result)
                roll_setpoint = 0
                depth_setpoint = self.get_depth_setpoint(self.loiter_depth)
                rpm_setpoint = self.slow_rpm
                self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))

                #TODO publish setpoints

            else: 
                self._node.get_logger().error("Failed to plan path")
                return False #FAIL


        if(self.current_action_phase == self.ACTION_PHASE.LONG_DISTANCE):
            # Plan a path that goes to a point 10m ahead of the docking station
            # Send yaw = 10s into the future in the path
            # Set RPM = Fast

            #Plan a path to the next loiter point
            path = self.plan_path('map', self.robot_position, self.target_position)
            if(path is not None ): 
                self._node.get_logger().info("Plan path successful")
                #Publish map for logging
                self.path_pub.publish(path)

                yaw_setpoint = self.get_yaw_from_path(self.robot_position, path)
                roll_setpoint = 0
                depth_setpoint = self.get_depth_setpoint(self.long_distance_depth)
                rpm_setpoint = self.fast_rpm
                self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))

                #TODO publish setpoints
            else: 
                self._node.get_logger().error("Failed to plan path")
                return False #FAIL
            pass

        if(self.current_action_phase == self.ACTION_PHASE.SHORT_DISTANCE):
            # Set target yaw = docking station + 10m ahead
            # Set RPM = SLOW if distance to target < 2m
            # Set RPM = FAST if distance to target < 4m
            yaw_setpoint = self.get_angle_between_points(self.robot_position, self.target_position)
            roll_setpoint = 0
            depth_setpoint = self.get_depth_setpoint(self.loiter_depth)
            rpm_setpoint = self.slow_rpm
            self._node.get_logger().info("Yaw setpoint: " +str(yaw_setpoint))
            pass

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
        # Step through the path 10s into the future (or until end) and calculate the yaw value need to reach that point
        #start_time = path.poses[0].header.stamp.sec
        index = 0
        #self._node.get_logger().info("path length " + str(len(path.poses)))
        #while index < len(path.poses)-1:
        #    #dt = path.poses[index].header.stamp.sec - start_time
        #    #self._node.get_logger().info("dt: " + str(dt))
        #    index +=1
        #    if(index > 30): 
        #        break
        index = min(len(path.poses)-1, 30) 
        return self.get_angle_between_points(start_pose, path.poses[index])

    def get_angle_between_points(self, p1:PoseStamped, p2:PoseStamped):
        dx = p2.pose.position.x - p1.pose.position.x
        dy = p2.pose.position.y - p1.pose.position.y
        return math.atan2(dy,dx)

    def integrate_pose(p:PoseStamped, t):
        #Integrate p with constant speed for t seconds
        return None

    def get_depth_setpoint(self, target_depth) -> float:
        #return a good depth setpoint based on target depth and minimum altitude
        return min(target_depth, (-self.robot_position.pose.position.z + self.robot_altitude) - self.min_altitude)

    def plan_path(self,frame_id, _start, _goal):
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
        TODO: Use lat lon as geofence input
        """
        gridmap = OccupancyGrid()
        gridmap.header.frame_id = frame_id
        gridmap.info.height = 100
        gridmap.info.width = 100
        gridmap.info.resolution = 1.0
        gridmap.info.origin.position.x = 0.0
        gridmap.info.origin.position.y = 0.0
        gridmap.info.origin.position.z = 0.0

        gridmap.data = [-1]*(gridmap.info.width*gridmap.info.height)
        #gridmap.data[row + col*gridmap.info.height] = 100
        for i in range(0,100):
            gridmap.data[0 + i*gridmap.info.height] = 100
            gridmap.data[1 + i*gridmap.info.height] = 100
            gridmap.data[98 + i*gridmap.info.height] = 100
            gridmap.data[99 + i*gridmap.info.height] = 100
            gridmap.data[i + 0*gridmap.info.height] = 100
            gridmap.data[i + 1*gridmap.info.height] = 100
            gridmap.data[i + 98*gridmap.info.height] = 100
            gridmap.data[i + 99*gridmap.info.height] = 100
        return gridmap

    #Subscriber callback functions
    def target_callback(self,msg):
        self._node.get_logger().info("target position received.")
        self.target_position = msg
        self.target_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)

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
