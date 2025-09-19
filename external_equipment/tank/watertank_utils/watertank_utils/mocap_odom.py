import rclpy
from rclpy.node import Node

import tf2_ros
import tf_transformations

from geometry_msgs.msg import TransformStamped, Pose, Twist
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion, quaternion_from_euler

import numpy as np

class MocapOdomBridge(Node):

    def __init__(self):
        super().__init__('mocap_odom_sam')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.mocap_to_odom_mat = None
        self.static_broadcaster = tf2_ros.StaticTransformBroadcaster(self)

        self.map_frame = self.declare_parameter("map_frame", "mocap").value
        self.odom_frame = self.declare_parameter("odom_frame", "sam/odom").value
        self.base_link = self.declare_parameter("base_link", "sam/base_link").value
        self.mocap_odom_top = self.declare_parameter("mocap_odom_sam", "/mocap/sam_mocap/odom").value
        self.sam_odom_top = self.declare_parameter("sam_odom_topic", "/sam/dr/odom").value
        
        self.odom_pub = self.create_publisher(Odometry, self.sam_odom_top, qos_profile=1)
        self.mocap_subs = self.create_subscription(Odometry, self.mocap_odom_top, self.mocap_odom_cb, qos_profile=10)

        # self.timer = self.create_timer(0.02, self.timer_cb)  # 50Hz


    def mocap_odom_cb(self, odom_mocap_msg: Odometry):
        try:
            # Get mocap -> base_link transform
            t = self.tf_buffer.lookup_transform(self.map_frame, 'sam_mocap/base_link', rclpy.time.Time())

            if self.mocap_to_odom_mat is None:

                # First message: save as static mocap -> odom
                self.get_logger().info("Captured initial mocap->base_link as mocap->odom")
                static_mocap_to_odom = t

                mocap_to_odom_tf = TransformStamped()
                mocap_to_odom_tf.header.stamp = self.get_clock().now().to_msg()
                mocap_to_odom_tf.header.frame_id = self.map_frame
                mocap_to_odom_tf.child_frame_id = self.odom_frame
                
                # Odom should always be horizontal
                roll, pitch, yaw = euler_from_quaternion(
                        [static_mocap_to_odom.transform.rotation.x, 
                         static_mocap_to_odom.transform.rotation.y,
                         static_mocap_to_odom.transform.rotation.z,
                         static_mocap_to_odom.transform.rotation.w])
                
                self.get_logger().info(f"Euler {roll}, {pitch}, {yaw}")
                
                # euler[1] = 0.
                quat = quaternion_from_euler(0, 0, yaw)
                static_mocap_to_odom.transform.rotation.x = quat[0]
                static_mocap_to_odom.transform.rotation.y = quat[1]
                static_mocap_to_odom.transform.rotation.z = quat[2]
                static_mocap_to_odom.transform.rotation.w = quat[3]

                self.mocap_to_odom_mat = self.transform_to_matrix(static_mocap_to_odom.transform)

                # Flip to ENU
                self.mocap_to_odom_mat = self.mocap_to_odom_mat @ tf_transformations.quaternion_matrix([1, 0, 0, 0.0])
                self.mocap_to_odom_mat
                translation, rotation = self.matrix_to_transform(self.mocap_to_odom_mat)
                mocap_to_odom_tf.transform.translation.x = translation[0]
                mocap_to_odom_tf.transform.translation.y = translation[1]
                mocap_to_odom_tf.transform.translation.z = translation[2]
                mocap_to_odom_tf.transform.rotation.x = rotation[0]
                mocap_to_odom_tf.transform.rotation.y = rotation[1]
                mocap_to_odom_tf.transform.rotation.z = rotation[2]
                mocap_to_odom_tf.transform.rotation.w = rotation[3]
                self.static_broadcaster.sendTransform(mocap_to_odom_tf)

                return

            # Convert transforms to numpy

            # Compute odom -> base_link = inv(mocap -> odom) * (mocap -> base_link)
            # self.mocap_to_odom_mat = self.transform_to_matrix(self.static_mocap_to_odom.transform)
            mocap_to_base_mat = self.transform_to_matrix(t.transform)
            odom_to_base_mat = np.linalg.inv(self.mocap_to_odom_mat) @ mocap_to_base_mat 
            
            # Flip to ENU
            odom_to_base_mat = odom_to_base_mat @ tf_transformations.quaternion_matrix([1, 0, 0, 0.0])

            odom_to_base_tf = TransformStamped()
            odom_to_base_tf.header.stamp = odom_mocap_msg.header.stamp
            odom_to_base_tf.header.frame_id = self.odom_frame
            odom_to_base_tf.child_frame_id = self.base_link

            translation, rotation = self.matrix_to_transform(odom_to_base_mat)
            odom_to_base_tf.transform.translation.x = translation[0]
            odom_to_base_tf.transform.translation.y = translation[1]
            odom_to_base_tf.transform.translation.z = translation[2]
            odom_to_base_tf.transform.rotation.x = rotation[0]
            odom_to_base_tf.transform.rotation.y = rotation[1]
            odom_to_base_tf.transform.rotation.z = rotation[2]
            odom_to_base_tf.transform.rotation.w = rotation[3]

            self.tf_broadcaster.sendTransform(odom_to_base_tf)

            # Publish Odometry
            odom_msg = Odometry()
            odom_msg.header.stamp = odom_mocap_msg.header.stamp
            odom_msg.header.frame_id = self.odom_frame
            odom_msg.child_frame_id = self.base_link

            odom_msg.pose.pose.position.x = translation[0]
            odom_msg.pose.pose.position.y = translation[1]
            odom_msg.pose.pose.position.z = translation[2]
            odom_msg.pose.pose.orientation.x = rotation[0]
            odom_msg.pose.pose.orientation.y = rotation[1]
            odom_msg.pose.pose.orientation.z = rotation[2]
            odom_msg.pose.pose.orientation.w = rotation[3]
            odom_msg.twist.twist = odom_mocap_msg.twist.twist

            self.odom_pub.publish(odom_msg)

        except Exception as e:
            self.get_logger().warn(f'Failed to get transform: {e}')

    def transform_to_matrix(self, transform):
        t = transform.translation
        q = transform.rotation
        trans = tf_transformations.translation_matrix([t.x, t.y, t.z])
        rot = tf_transformations.quaternion_matrix([q.x, q.y, q.z, q.w])
        return trans @ rot

    def matrix_to_transform(self, mat):
        trans = tf_transformations.translation_from_matrix(mat)
        rot = tf_transformations.quaternion_from_matrix(mat)
        return trans, rot

def main(args=None):
    rclpy.init(args=args)
    node = MocapOdomBridge()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
