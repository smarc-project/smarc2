#!/usr/bin/python3
from geodesy.utm import fromMsg, UTMPoint
from geometry_msgs.msg import PointStamped
from geographic_msgs.msg import GeoPoint

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