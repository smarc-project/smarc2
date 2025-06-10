#!/usr/bin/python3
from geodesy.utm import fromMsg, UTMPoint
from geometry_msgs.msg import PointStamped, Pose, PoseStamped
from geographic_msgs.msg import GeoPoint
from std_msgs.msg import Float32
from tf_transformations import euler_from_quaternion
import math

def convert_latlon_to_utm(gp: GeoPoint) -> PointStamped:
    """
    Convert a GeoPoint to a PointStamped in UTM coordinates.
    """
    pt = fromMsg(gp)
    ps = PointStamped()
    ps.point = pt.toPoint()
    zone, band = pt.gridZone()
    ps.header.frame_id = f"utm_{zone}_{band}"
    return ps


def convert_utm_to_latlon(utm: PointStamped | PoseStamped) -> GeoPoint:
    """
    Convert a PointStamped or PoseStamped in UTM coordinates to a GeoPoint.
    The header frame_id must be in the format "utm_<zone>_<band>".
    """
    utm_pt = UTMPoint()

    if isinstance(utm, PoseStamped):
        utm_point = utm.pose.position
    elif isinstance(utm, PointStamped):
        utm_point = utm.point
    else:
        raise TypeError("Input must be a PointStamped or PoseStamped.")
    utm_pt.easting = utm_point.x
    utm_pt.northing = utm_point.y
    _, zone, band = utm.header.frame_id.split("_")
    utm_pt.zone = int(zone)
    utm_pt.band = band
    msg = utm_pt.toMsg()

    return msg


def convert_enu_pose_to_heading(enu_pose: Pose) -> Float32:
    """
    Convert an ENU pose to a heading in degrees.
    :param enu_pose: Pose in ENU coordinates
    :return: Float32 message with compass heading in degrees (0-360)
    """
    enu_orientation = enu_pose.orientation
    rpy_enu = euler_from_quaternion(
        [enu_orientation.x, enu_orientation.y, enu_orientation.z, enu_orientation.w])
    yaw = rpy_enu[2]  # Yaw in radians

    # Convert input yaw to degrees
    yaw_deg = yaw * (180 / math.pi)

    # Convert yaw (ENU) to heading (NED)
    heading = 90. - yaw_deg

    # Bound to 0 - 360
    compass_heading = heading % 360.

    compass_heading_msg = Float32()
    compass_heading_msg.data = compass_heading

    return compass_heading_msg

def compute_course_from_two_poses(prev_pose: PoseStamped, current_pose: PoseStamped) -> Float32:
    """
    Computes the course from the previous and current poses.
    Returns the course in degrees (0-360).
    """
    if prev_pose is None or current_pose is None:
        return None
    dx = current_pose.pose.position.x - prev_pose.pose.position.x
    dy = current_pose.pose.position.y - prev_pose.pose.position.y
    course_rad = math.atan2(dy, dx)
    course_deg = math.degrees(course_rad) % 360.0
    return Float32(data=course_deg)

def compute_speed_from_two_poses(prev_pose: PoseStamped, current_pose: PoseStamped) -> Float32:
    """
    Computes the speed from the previous and current poses.
    Returns the speed in meters per second.
    """
    if prev_pose is None or current_pose is None:
        return None
    dx = current_pose.pose.position.x - prev_pose.pose.position.x
    dy = current_pose.pose.position.y - prev_pose.pose.position.y
    dt = (current_pose.header.stamp.sec + current_pose.header.stamp.nanosec * 1e-9) - \
         (prev_pose.header.stamp.sec + prev_pose.header.stamp.nanosec * 1e-9)
    speed = math.sqrt(dx**2 + dy**2) / dt if dt > 0 else 0.0
    return Float32(data=speed)