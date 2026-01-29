#!/usr/bin/env python3
import csv
from pathlib import Path as FilePath

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped


class LastPathPointPublisher(Node):
    def __init__(self):
        super().__init__('csv_path_publisher')

        file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam/sam_diving_controller/sam_diving_controller/trajectories/2026-01-19__straight_trajectory_1m.csv"
        self.declare_parameter('csv_file', file_path)
        self.declare_parameter('frame_id', 'mocap')
        csv_file = self.get_parameter('csv_file').get_parameter_value().string_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        self.publisher_ = self.create_publisher(PoseStamped, '/mocap/hula/pose', 10)
        self.pose_msg = self.load_last_pose(FilePath(csv_file))

        # publish at 1 Hz
        self.timer = self.create_timer(1.0, self.timer_callback)

    def load_last_pose(self, csv_path: FilePath) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = self.frame_id

        if not csv_path.exists():
            self.get_logger().error(f'CSV file not found: {csv_path}')
            pose.pose.orientation.w = 1.0
            return pose

        last_row = None
        with csv_path.open() as f:
            reader = csv.DictReader(f)  # <-- tab-separated (your header shows tabs)
            for row in reader:
                last_row = row

        if last_row is None:
            self.get_logger().error(f'CSV file is empty (no data rows): {csv_path}')
            pose.pose.orientation.w = 1.0
            return pose

        try:
            pose.pose.position.x = float(last_row['x'])
            pose.pose.position.y = float(last_row['y'])
            pose.pose.position.z = float(last_row['z'])

            pose.pose.orientation.w = float(last_row['q0'])
            pose.pose.orientation.x = float(last_row['q1'])
            pose.pose.orientation.y = float(last_row['q2'])
            pose.pose.orientation.z = float(last_row['q3'])


        except (KeyError, ValueError) as e:
            self.get_logger().error(f'Failed parsing last row in {csv_path}: {e}')
            pose.pose.orientation.w = 1.0
            return pose

        self.get_logger().info(
            f"Loaded last pose: "
            f"p=({pose.pose.position.x:.3f},{pose.pose.position.y:.3f},{pose.pose.position.z:.3f}) "
            f"q=({pose.pose.orientation.x:.4f},{pose.pose.orientation.y:.4f},"
            f"{pose.pose.orientation.z:.4f},{pose.pose.orientation.w:.4f})"
        )
        return pose

#    def load_csv(self, csv_path) -> Path:
#        path_msg = Path()
#        path_msg.header.frame_id = self.frame_id
#
#        if not csv_path.exists():
#            self.get_logger().error(f'CSV file not found: {csv_path}')
#            return path_msg
#
#        with csv_path.open() as f:
#            reader = csv.DictReader(f)
#            #for row in csvreader:
#            for row in reader:
#                pose = PoseStamped()
#                pose.header.frame_id = self.frame_id
#                pose.pose.position.x = float(row['x'])
#                pose.pose.position.y = float(row['y'])
#                pose.pose.position.z = float(row['z'])
#                # orientation left as default (0,0,0,1)
#                path_msg.poses.append(pose)
#
#        self.get_logger().info(f'Loaded {len(path_msg.poses)} poses from {csv_path}')
#        return path_msg

    def timer_callback(self):
        self.pose_msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher_.publish(self.pose_msg)


def main(args=None):
    rclpy.init(args=args)
    node = LastPathPointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
