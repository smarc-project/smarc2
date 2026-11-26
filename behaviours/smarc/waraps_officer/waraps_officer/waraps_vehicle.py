#!/usr/bin/python3
"""WARA-PS level 1 for one vehicle: heartbeat, sensor strings, sensor_info.

Reads the smarc/* vehicle topics and republishes them as JSON Strings under
``Topics.WARA_PS_SENSOR_PREFIX`` once per pulse. ``sensor_info`` lists every
String topic any node under the robot publishes under that prefix, so a
sensor added by another node (a stick, the officer's executing_tasks) shows
up without editing this file. Levels in the heartbeat follow who is on the
graph: ``direct_execution`` while something publishes the direct execution
info topic, ``tst_execution`` likewise. The payloads are built in ``level1``.
"""

import uuid

import rclpy
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.publisher import Publisher
from smarc_msgs.msg import Topics
from smarc_utilities.topic_utils import node_string_topics_under
from std_msgs.msg import Float32, String
from transforms3d.euler import quat2euler

from waraps_officer.level1 import (
    Agent,
    LatLon,
    Reading,
    agent_levels,
    all_finite,
    fresh,
    heartbeat_json,
    position_json,
    scalar_json,
    sensor_info_json,
)
from waraps_officer.ros_clock import now_s


class Ros2WarapsVehicle:
    def __init__(self, node: Node) -> None:
        self._node = node
        robot_name = node.declare_parameter('robot_name', '').get_parameter_value().string_value
        if not robot_name:
            raise ValueError('robot_name parameter is required; it is the agent name on the broker')
        agent_uuid = node.declare_parameter('agent_uuid', '').get_parameter_value().string_value or str(uuid.uuid4())
        pulse_rate = node.declare_parameter('pulse_rate', 1.0).get_parameter_value().double_value
        self._agent = Agent(
            agent_type=node.declare_parameter('agent_type', 'air').get_parameter_value().string_value,
            agent_uuid=agent_uuid,
            name=robot_name,
            rate_hz=pulse_rate,
        )
        self._stale_after_s = node.declare_parameter('stale_after_s', 10.0).get_parameter_value().double_value

        self._latlon: LatLon | None = None
        # The latest odom orientation and when it arrived; roll and pitch are worked out once per pulse.
        self._orientation: tuple[Quaternion, float] | None = None
        # Scalars keyed by the WARA-PS topic they go out on.
        self._readings: dict[str, Reading] = {}
        self._heartbeat_pub = node.create_publisher(String, Topics.WARA_PS_HEARTBEAT_TOPIC, 10)
        self._sensor_info_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_INFO_TOPIC, 10)
        # A sensor topic is created the first time a reading qualifies, so
        # sensor_info only lists what this vehicle really has. Which sensors
        # those are is only known at run time, hence a dict.
        self._sensor_pubs: dict[str, Publisher] = {}

        node.create_subscription(GeoPoint, Topics.POS_LATLON_TOPIC, self._store_latlon, 10)
        node.create_subscription(Odometry, Topics.ODOM_TOPIC, self._store_orientation, 10)
        for vehicle_topic, waraps_topic in (
            (Topics.HEADING_TOPIC, Topics.WARA_PS_SENSOR_HEADING_TOPIC),
            (Topics.COURSE_TOPIC, Topics.WARA_PS_SENSOR_COURSE_TOPIC),
            (Topics.SPEED_TOPIC, Topics.WARA_PS_SENSOR_SPEED_TOPIC),
            (Topics.DEPTH_TOPIC, Topics.WARA_PS_SENSOR_DEPTH_TOPIC),
            (Topics.ALTITUDE_TOPIC, Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC),
        ):
            node.create_subscription(
                Float32,
                vehicle_topic,
                lambda msg, topic=waraps_topic: self._store_reading(topic, msg.data),
                10,
            )

        node.create_timer(1.0 / pulse_rate, self.publish_pulse)
        node.get_logger().info(f"waraps_vehicle '{robot_name}' ({self._agent.agent_type}) uuid {agent_uuid}, {pulse_rate} Hz")

    # ---- inputs -------------------------------------------------------------

    def _store_latlon(self, msg: GeoPoint) -> None:
        self._latlon = LatLon(msg.latitude, msg.longitude, msg.altitude, now_s(self._node))

    def _store_orientation(self, msg: Odometry) -> None:
        self._orientation = (msg.pose.pose.orientation, now_s(self._node))

    def _store_reading(self, waraps_topic: str, value: float) -> None:
        self._readings[waraps_topic] = Reading(value, now_s(self._node))

    # ---- outputs ------------------------------------------------------------

    def _publish_sensor(self, topic: str, text: str) -> None:
        if topic not in self._sensor_pubs:
            self._sensor_pubs[topic] = self._node.create_publisher(String, topic, 10)
        self._sensor_pubs[topic].publish(String(data=text))

    def _is_fresh(self, reading: Reading | LatLon | None, now: float) -> bool:
        return reading is not None and fresh(reading.stamp_s, now, self._stale_after_s)

    def current_levels(self) -> list[str]:
        return agent_levels(
            direct_execution=self._node.count_publishers(Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC) > 0,
            tst_execution=self._node.count_publishers(Topics.WARA_PS_TST_EXEC_INFO_TOPIC) > 0,
        )

    def sensor_names(self) -> list[str]:
        found = node_string_topics_under(self._node, self._node.get_namespace(), Topics.WARA_PS_SENSOR_PREFIX)
        return [t.name for t in found]

    def publish_pulse(self) -> None:
        now = now_s(self._node)
        self._heartbeat_pub.publish(String(data=heartbeat_json(self._agent, self.current_levels(), now)))

        latlon = self._latlon
        # A stale or NaN position is left out rather than sent as if it were current.
        if self._is_fresh(latlon, now) and all_finite(latlon.latitude, latlon.longitude, latlon.altitude):
            self._publish_sensor(
                Topics.WARA_PS_SENSOR_POSITION_TOPIC,
                position_json(latlon.latitude, latlon.longitude, latlon.altitude),
            )

        if self._orientation is not None:
            q, stamp_s = self._orientation
            roll, pitch, _ = quat2euler([q.w, q.x, q.y, q.z])
            self._readings[Topics.WARA_PS_SENSOR_ROLL_TOPIC] = Reading(roll, stamp_s)
            self._readings[Topics.WARA_PS_SENSOR_PITCH_TOPIC] = Reading(pitch, stamp_s)

        for topic, reading in self._readings.items():
            if self._is_fresh(reading, now) and all_finite(reading.value):
                self._publish_sensor(topic, scalar_json(reading.value))

        self._sensor_info_pub.publish(String(data=sensor_info_json(self._agent, self.sensor_names(), now)))


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Node('waraps_vehicle')
    Ros2WarapsVehicle(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
