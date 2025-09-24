from gettext import translation

import numpy as np
import tf2_geometry_msgs
from geometry_msgs.msg import PointStamped, TransformStamped, Point, Quaternion
from nav_msgs.msg import Odometry
from tf_transformations import quaternion_matrix, quaternion_multiply, quaternion_inverse


def rotate_vector_to_child(odom_msg: Odometry, vec_in_parent):
    q = odom_msg.pose.pose.orientation
    rotation_child_parent = quaternion_matrix([q.x, q.y, q.z, q.w])[:3, :3]

    rotation_parent_child = rotation_child_parent.T
    return rotation_parent_child.dot(vec_in_parent)


def transform_point_to_child(odom_parent: Odometry, point_in_odom):
    transform_child_to_parent = odometry_to_transform(odom_parent)
    transform_parent_to_child = invert_transform(transform_child_to_parent)

    if isinstance(point_in_odom, PointStamped):
        pass
    if isinstance(point_in_odom, Point):
        new_point = PointStamped()
        new_point.header = odom_parent.header
        new_point.point = point_in_odom
        point_in_odom = new_point

    return tf2_geometry_msgs.do_transform_point(point_in_odom, transform_parent_to_child)


def invert_transform(transform_to_inv: TransformStamped):
    t = np.array([
        transform_to_inv.transform.translation.x,
        transform_to_inv.transform.translation.y,
        transform_to_inv.transform.translation.z,
    ], dtype=float)
    q = [
        transform_to_inv.transform.rotation.x,
        transform_to_inv.transform.rotation.y,
        transform_to_inv.transform.rotation.z,
        transform_to_inv.transform.rotation.w,
    ]

    quaternion_inv = quaternion_inverse(q)
    rotation_inv = quaternion_matrix(quaternion_inv)[:3, :3]
    translation_inv = -rotation_inv @ t

    result = TransformStamped()
    result.header.stamp = transform_to_inv.header.stamp
    result.header.frame_id = transform_to_inv.child_frame_id
    result.child_frame_id = transform_to_inv.header.frame_id

    result.transform.translation.x = float(translation_inv[0])
    result.transform.translation.y = float(translation_inv[1])
    result.transform.translation.z = float(translation_inv[2])

    result.transform.rotation.x, result.transform.rotation.y, result.transform.rotation.z, result.transform.rotation.w = quaternion_inv

    return result


def odometry_to_transform(odom_msg: Odometry):
    transform_to_body = TransformStamped()
    transform_to_body.header = odom_msg.header
    transform_to_body.child_frame_id = "/base_link"  # odom_msg.child_frame_id TODO: Check if this is also coming from the mocap Odom message
    transform_to_body.transform.translation.x = odom_msg.pose.pose.position.x
    transform_to_body.transform.translation.y = odom_msg.pose.pose.position.y
    transform_to_body.transform.translation.z = odom_msg.pose.pose.position.z
    transform_to_body.transform.rotation = odom_msg.pose.pose.orientation

    return transform_to_body


def rotate_quat_into_parent_frame(odom_msg: Odometry, q_in_child):
    q_parent_from_child = quat_msg_to_list(odom_msg.pose.pose.orientation)
    q_in_parent = quaternion_multiply(q_parent_from_child, q_in_child)
    return q_in_parent


def rotate_quat_to_child(odom_msg: Odometry, q_in_parent):
    q_parent_from_child = quat_msg_to_list(odom_msg.pose.pose.orientation)
    q_child_from_parent = quaternion_inverse(q_parent_from_child)
    q_in_child = quaternion_multiply(q_child_from_parent, q_in_parent)
    return q_in_child


def quat_msg_to_list(q: Quaternion):
    return [q.x, q.y, q.z, q.w]
