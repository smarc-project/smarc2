import tf2_geometry_msgs
from geometry_msgs.msg import PointStamped, TransformStamped, PoseWithCovariance, Point, Quaternion
from nav_msgs.msg import Odometry
from tf_transformations import quaternion_matrix, quaternion_multiply, quaternion_inverse


def rotate_vector_from_parent_to_child(odom_msg: Odometry, vec_in_parent):
    q = odom_msg.pose.pose.orientation
    # quaternion_matrix returns a 4x4; top-left 3x3 is rotation from child->parent
    rotation_child_parent = quaternion_matrix([q.x, q.y, q.z, q.w])[:3, :3]

    # We want parent->child, so transpose (inverse) it:
    rotation_parent_child = rotation_child_parent.T
    return rotation_parent_child.dot(vec_in_parent)


def point_odom_to_base(odom_msg: Odometry, point_in_odom):
    transform_odom_base = odom_to_transform(odom_msg)

    if isinstance(point_in_odom, PointStamped):
        pass
    if isinstance(point_in_odom, Point):
        new_point = PointStamped()
        new_point.header = odom_msg.header
        new_point.point = point_in_odom
        point_in_odom = new_point

    return tf2_geometry_msgs.do_transform_point(point_in_odom, transform_odom_base)


def odom_to_transform(odom_msg: Odometry):
    transform_to_body = TransformStamped()
    transform_to_body.header = odom_msg.header
    transform_to_body.child_frame_id = "/base_link"  # odom_msg.child_frame_id TODO: Check if this is also coming from the mocap Odom message
    transform_to_body.transform.translation.x = odom_msg.pose.pose.position.x
    transform_to_body.transform.translation.y = odom_msg.pose.pose.position.y
    transform_to_body.transform.translation.z = odom_msg.pose.pose.position.z
    transform_to_body.transform.rotation = odom_msg.pose.pose.orientation

    return transform_to_body


def quat_msg_to_list(q: Quaternion):
    return [q.x, q.y, q.z, q.w]


def rotate_quat_into_parent_frame(odom_msg: Odometry, q_in_child):
    q_parent_from_child = quat_msg_to_list(odom_msg.pose.pose.orientation)
    q_in_parent = quaternion_multiply(q_parent_from_child, q_in_child)
    return q_in_parent


def rotate_quat_into_child_frame(odom_msg: Odometry, q_in_parent):
    q_parent_from_child = quat_msg_to_list(odom_msg.pose.pose.orientation)
    q_child_from_parent = quaternion_inverse(q_parent_from_child)
    q_in_child = quaternion_multiply(q_child_from_parent, q_in_parent)
    return q_in_child
