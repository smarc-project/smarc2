#!/usr/bin/python3
from geodesy.utm import fromMsg, UTMPoint
from geometry_msgs.msg import PointStamped, Pose
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


def convert_utm_to_latlon(utm: PointStamped) -> GeoPoint:
    """
    Convert a PointStamped in UTM coordinates to a GeoPoint.
    The header frame_id must be in the format "utm_<zone>_<band>".
    """
    utm_pt = UTMPoint()
    utm_pt.easting = utm.point.x
    utm_pt.northing = utm.point.y
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