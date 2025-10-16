#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PointStamped
import math
import time
from sensor_msgs.msg import CameraInfo

class PosePublisher(Node):
    def __init__(self):
        super().__init__('pose_publisher')

        # Publisher
        self.publisher_ = self.create_publisher(PoseStamped, '/M350/move_to_setpoint', 10)

        # Subscriber to middle point
        self.middle_sub = self.create_subscription(
            PointStamped,
            '/M350/alars_detection/middle',
            self.middle_callback,
            10)

        # Subscribe once to camera info to get FOV
        self.cam_info_sub = self.create_subscription(
            CameraInfo,
            '/M350/gimbal_camera/cam_info',
            self.cam_info_callback,
            1)
        self.cam_info_received = False

        # FSM states
        self.state = "go_initial"
        self.middle_point = None
        self.reached_time = None

        # Timer loop at 10Hz
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('PosePublisher initialized.')

        # Camera and UAV parameters
        self.altitude = 8.0  # meters above target
        self.fov_x = None
        self.fov_y = None
        self.current_x = 0.0  # UAV map frame initial position
        self.current_y = -15.0

    def euler_to_quaternion(self, roll, pitch, yaw):
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        return qx, qy, qz, qw

    def cam_info_callback(self, msg: CameraInfo):
        # Only subscribe once
        if not self.cam_info_received:
            fx = msg.k[0]
            fy = msg.k[4]
            width = msg.width
            height = msg.height

            # Compute horizontal and vertical FOV
            self.fov_x = 2 * math.atan(width / (2 * fx))
            self.fov_y = 2 * math.atan(height / (2 * fy))
            self.get_logger().info(f"Camera FOV received: FOV_x={math.degrees(self.fov_x):.1f}°, FOV_y={math.degrees(self.fov_y):.1f}°")
            self.cam_info_received = True

            # Unsubscribe after receiving
            self.destroy_subscription(self.cam_info_sub)

    def middle_callback(self, msg: PointStamped):
        self.middle_point = (msg.point.x, msg.point.y)

    def publish_pose(self, x, y, z, yaw_deg=0.0):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "M350/map"

        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z

        roll, pitch, yaw = 0.0, 0.0, math.radians(yaw_deg)
        qx, qy, qz, qw = self.euler_to_quaternion(roll, pitch, yaw)
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw

        self.publisher_.publish(msg)

    def timer_callback(self):
        if not self.cam_info_received:
            # Wait until FOV is received
            return

        goal_tolerance = 0.2

        if self.state == "go_initial":
            # Record start time when first entering this state
            if not hasattr(self, 'go_initial_start_time'):
                self.go_initial_start_time = time.time()
                self.get_logger().info("Flying to initial point (0.0, -15.0, 4.0)")

            # Keep publishing the pose to hold UAV at initial point
            self.publish_pose(self.current_x, self.current_y, 10.0)

            # Calculate elapsed and remaining time
            elapsed = time.time() - self.go_initial_start_time
            remaining = max(0, 20.0 - elapsed)

            # Print how many seconds left (rounded to 1 decimal place)
            self.get_logger().info(f"Remaining time at initial point: {remaining:.1f} sec")


            # Transition after 15 seconds
            if elapsed >= 20.0:
                self.state = "wait_middle"
                self.wait_middle_start_time = time.time()  # start timer for wait_middle
                self.get_logger().info("Completed initial positioning, switching to wait_middle")

        elif self.state == "wait_middle" and self.middle_point is not None:

            # Record start time when first entering this state
            if not hasattr(self, 'wait_middle_start_time'):
                self.wait_middle_start_time = time.time()

            # Calculate elapsed and remaining time (example: 10 sec hold at middle)
            elapsed = time.time() - self.wait_middle_start_time
            remaining = max(0, 10.0 - elapsed)
            self.get_logger().info(f"Remaining time at middle point: {remaining:.1f} sec")

            norm_x, norm_y = self.middle_point

            # Convert normalized coordinates to real-world offsets
            offset_x = norm_x * self.altitude * math.tan(self.fov_x / 2)   # left right
            offset_y = norm_y * self.altitude * math.tan(self.fov_y / 2)   # forward and back 

            # Corrective waypoint
            target_x = self.current_x - offset_y   # forward and back 
            target_y = self.current_y - offset_x   # left right

            self.publish_pose(target_x, target_y, 10.0)
            self.get_logger().info(f"Tracking middle: norm=({norm_x:.2f},{norm_y:.2f}) -> offset=({offset_x:.2f},{offset_y:.2f}) -> waypoint=({target_x:.2f},{target_y:.2f})")

            # Check tolerance
            if abs(offset_x) < goal_tolerance and abs(offset_y) < goal_tolerance:
                self.get_logger().info("Middle point centered!")
                self.reached_time = time.time()
                self.state = "descend"
            elif elapsed >= 10.0:
                self.get_logger().info("Wait time exceeded! Switching to descend")
                self.reached_time = time.time()
                self.state = "descend"

        elif self.state == "descend":
            # Calculate elapsed and remaining rest time
            elapsed = time.time() - self.reached_time
            remaining = max(0, 5.0 - elapsed)
            self.get_logger().info(f"Descend Remaining rest time: {remaining:.1f} sec")
            # Publish pose with descending altitude
            self.publish_pose(self.current_x, self.current_y, 3.0)

            if elapsed >= 5.0:
                self.get_logger().info("Rest complete. Moving forward + altitude.")
                self.state = "move_forward"



        elif self.state == "move_forward":
            # Record start time for rise motion
            if not hasattr(self, 'move_forward_start_time'):
                self.move_forward_start_time = time.time()
                self.start_altitude = 4.0 # store current altitude at entry
                self.target_altitude = 3.0           # desired final altitude
                self.rise_duration = 8.0              # seconds to complete rise
                self.rise_rate = (self.target_altitude - self.start_altitude) / self.rise_duration

            # Calculate elapsed and clamp to rise duration
            elapsed = time.time() - self.move_forward_start_time
            elapsed = min(elapsed, self.rise_duration)

            # Compute new altitude
            new_altitude = self.start_altitude + self.rise_rate * elapsed

            # Move forward while rising
            target_x = self.current_x + 5.0
            target_y = self.current_y
            self.publish_pose(target_x, target_y, new_altitude)

            remaining = max(0, self.rise_duration - elapsed)
            self.get_logger().info(
                f"Moving forward +5m | Rising to {self.target_altitude:.1f}m | "
                f"Remaining rise time: {remaining:.1f} sec | Altitude: {new_altitude:.2f}"
            )

            # Transition after rise is done
            if elapsed >= self.rise_duration:
                self.get_logger().info("Forward + rise motion complete.")
                self.state = "ascend_and_hover"   # <-- replace with your actual next state
                self.reached_time = time.time()
                
  
        elif self.state == "ascend_and_hover":
            # Calculate elapsed and remaining rest time
            elapsed = time.time() - self.reached_time
            remaining = max(0, 10.0 - elapsed)
            self.get_logger().info(f"Ascend and Hover Remaining rest time: {remaining:.1f} sec")

            self.publish_pose(self.current_x + 5.0, self.current_y, 10.0)

            if elapsed >= 10.0:
                self.get_logger().info("Hover complete. Moving back home.")
                self.state = "Home"
                self.reached_time = time.time()

        elif self.state == "Home":
            # Calculate elapsed and remaining rest time
            elapsed = time.time() - self.reached_time
            remaining = max(0, 15.0 - elapsed)
            self.get_logger().info(f"Go Home Remaining rest time: {remaining:.1f} sec")

            # Publish pose with descending altitude
            self.publish_pose(0.0, 0.0, 10.0)

            if elapsed >= 15.0:
                self.get_logger().info("Arrive home. Start to land")
                self.state = "Land"
                self.reached_time = time.time()


        elif self.state == "Land":

            # Publish pose with descending altitude
            self.publish_pose(0.0, 0.0, 1.0)
            self.get_logger().info("Landing...")



        #    pass

def main(args=None):
    rclpy.init(args=args)
    node = PosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
