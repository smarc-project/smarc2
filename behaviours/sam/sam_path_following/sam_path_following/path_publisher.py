#!/usr/bin/env python3
import csv
from pathlib import Path as FilePath

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class CsvPathPublisher(Node):
    def __init__(self):
        super().__init__('csv_path_publisher')

        #file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam/sam_diving_controller/sam_diving_controller/trajectories/simple_path_complexity_1.csv"
        file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam/sam_diving_controller/sam_diving_controller/trajectories/straight_trajectory_1.csv"
        self.declare_parameter('csv_file', file_path)
        self.declare_parameter('frame_id', 'mocap')
        csv_file = self.get_parameter('csv_file').get_parameter_value().string_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        self.publisher_ = self.create_publisher(Path, 'csv_path', 10)
        self.path_msg = self.load_csv(FilePath(csv_file))

        # publish at 1 Hz
        self.timer = self.create_timer(1.0, self.timer_callback)

    def load_csv(self, csv_path) -> Path:
        path_msg = Path()
        path_msg.header.frame_id = self.frame_id

        if not csv_path.exists():
            self.get_logger().error(f'CSV file not found: {csv_path}')
            return path_msg

        with csv_path.open() as f:
            reader = csv.DictReader(f)
            #for row in csvreader:
            for row in reader:
                pose = PoseStamped()
                pose.header.frame_id = self.frame_id
                pose.pose.position.x = float(row['x'])
                pose.pose.position.y = float(row['y'])
                pose.pose.position.z = float(row['z'])
                # orientation left as default (0,0,0,1)
                path_msg.poses.append(pose)

        self.get_logger().info(f'Loaded {len(path_msg.poses)} poses from {csv_path}')
        return path_msg

    def timer_callback(self):
        self.path_msg.header.stamp = self.get_clock().now().to_msg()
        for p in self.path_msg.poses:
            p.header.stamp = self.path_msg.header.stamp
        self.publisher_.publish(self.path_msg)


def main(args=None):
    rclpy.init(args=args)
    node = CsvPathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
