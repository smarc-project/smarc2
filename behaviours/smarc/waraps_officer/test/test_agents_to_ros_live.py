"""One mirrored agent becomes latlon and odom on a private domain."""

import json
import math

from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.parameter import Parameter
from rclpy.time import Time
from smarc_msgs.msg import Topics
from smarc_georef_cpp import GeorefUtils
from smarc_utilities.testing import wait_for
from std_msgs.msg import String
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from transforms3d.euler import quat2euler

from waraps_officer.waraps_agents_encoding import absolute, body_velocity, enu_yaw
from waraps_officer.waraps_agents_to_ros import AgentsToRos

ROBOT = 'evolo'
AGENT = 'aldo_evolo'
LAT, LON, ALT = 58.85, 17.67, 1.5
SPEED = 1.25


def test_a_mirrored_agent_becomes_latlon_and_odom(ros_graph):
    source = ros_graph('source')
    point = GeoPoint()
    point.latitude = LAT
    point.longitude = LON
    point.altitude = ALT
    with GeorefUtils(node=source) as georef:
        utm = georef.geopoint_to_point_stamped(point)

    transform = TransformStamped()
    transform.header.stamp = source.get_clock().now().to_msg()
    transform.header.frame_id = f'{ROBOT}/odom'
    transform.child_frame_id = utm.header.frame_id
    transform.transform.rotation.w = 1.0
    StaticTransformBroadcaster(source).sendTransform(transform)

    position = json.dumps({
        'type': 'GeoPoint',
        'latitude': LAT,
        'longitude': LON,
        'altitude': ALT,
    })
    pubs = {
        Topics.WARA_PS_SENSOR_POSITION_TOPIC: position,
        Topics.WARA_PS_SENSOR_HEADING_TOPIC: json.dumps(0.0),
        Topics.WARA_PS_SENSOR_COURSE_TOPIC: json.dumps(90.0),
        Topics.WARA_PS_SENSOR_SPEED_TOPIC: json.dumps(SPEED),
    }
    publishers = []
    for root in (AGENT, ROBOT):
        for constant in pubs:
            publishers.append(source.create_publisher(String, absolute(root, constant), 10))

    def tick():
        index = 0
        for _root in (AGENT, ROBOT):
            for constant, payload in pubs.items():
                publishers[index].publish(String(data=payload))
                index += 1

    source.create_timer(0.05, tick)

    node = ros_graph('agents', parameter_overrides=[
        Parameter('robot_name', value=ROBOT),
        Parameter('publish_rate_hz', value=20.0),
        Parameter('transform_timeout_s', value=0.2),
        Parameter('position_covariance.ellipse_x_m', value=1.0),
        Parameter('position_covariance.ellipse_y_m', value=0.5),
        Parameter('position_covariance.ellipse_z_m', value=0.0),
    ])
    agents = AgentsToRos(node)
    heard = {}

    def keep(kind):
        def callback(msg):
            heard[kind] = msg
            heard[kind + '_n'] = heard.get(kind + '_n', 0) + 1
        return callback

    latlon_name = node.get_parameter('latlon_name').value
    odom_name = node.get_parameter('odom_name').value
    source.create_subscription(GeoPoint, absolute(AGENT, latlon_name), keep('latlon'), 10)
    source.create_subscription(Odometry, absolute(AGENT, odom_name), keep('odom'), 10)
    source.create_subscription(GeoPoint, absolute(ROBOT, latlon_name), keep('own'), 10)

    assert wait_for(lambda: heard.get('odom_n', 0) >= 2, timeout_s=8.0)
    # Each odom carries its position's arrival stamp, not the static transform's.
    first = Time.from_msg(heard['odom'].header.stamp)
    assert first > Time.from_msg(transform.header.stamp)
    assert wait_for(lambda: Time.from_msg(heard['odom'].header.stamp) > first, timeout_s=4.0)
    latlon = heard['latlon']
    odom = heard['odom']
    assert abs(latlon.latitude - LAT) < 1e-9
    assert abs(latlon.longitude - LON) < 1e-9
    assert abs(latlon.altitude - ALT) < 1e-9
    assert abs(odom.pose.pose.position.x - utm.point.x) < 1e-3
    assert abs(odom.pose.pose.position.y - utm.point.y) < 1e-3
    assert abs(odom.pose.pose.position.z - ALT) < 1e-3
    assert odom.header.frame_id == agents.odom_frame
    assert odom.child_frame_id == f'{AGENT}/base_link'
    _roll, _pitch, yaw = quat2euler([
        odom.pose.pose.orientation.w,
        odom.pose.pose.orientation.x,
        odom.pose.pose.orientation.y,
        odom.pose.pose.orientation.z,
    ], axes='sxyz')
    assert abs(yaw - math.pi / 2) < 1e-6
    vx, vy = body_velocity(SPEED, enu_yaw(0.0, 'deg'), enu_yaw(90.0, 'deg'))
    assert abs(odom.twist.twist.linear.x - vx) < 1e-6
    assert abs(odom.twist.twist.linear.y - vy) < 1e-6
    assert odom.pose.covariance[0] == 1.0
    assert odom.pose.covariance[7] == 0.25
    assert odom.pose.covariance[14] == 0.0
    assert 'own' not in heard
