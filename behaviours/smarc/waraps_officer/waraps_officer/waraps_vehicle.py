#!/usr/bin/python3
"""WARA-PS level 1 for one vehicle: heartbeat, sensor strings, sensor_info.

Reads the smarc/* vehicle topics and republishes them as JSON Strings under
``Topics.WARA_PS_SENSOR_PREFIX`` once per pulse. ``sensor_info`` lists every
String topic any node under the robot publishes under that prefix, so a
sensor added by another node (a stick, the officer's executing_tasks) shows
up without editing this file. Levels in the heartbeat follow who is on the
graph: ``direct_execution`` while something publishes the direct execution
info topic, ``tst_execution`` likewise.
"""

import uuid

import rclpy
from geographic_msgs.msg import GeoPoint
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
    finite,
    fresh,
    heartbeat_json,
    levels,
    position_json,
    scalar_json,
    sensor_info_json,
)


class WarapsVehicle:
    def __init__(self, node: Node):
        self._node = node
        gp = node.declare_parameter
        robot_name = gp('robot_name', '').value
        if not robot_name:
            raise ValueError('robot_name parameter is required; it is the agent name on the broker')
        agent_uuid = gp('agent_uuid', '').value or str(uuid.uuid4())
        pulse_rate = gp('pulse_rate', 1.0).value
        self._agent = Agent(
            agent_type=gp('agent_type', 'air').value,
            agent_uuid=agent_uuid,
            name=robot_name,
            rate_hz=pulse_rate,
        )
        self._stale_after_s = gp('stale_after_s', 10.0).value

        self._latlon: LatLon | None = None
        # Scalars keyed by the WARA-PS topic they go out on.
        self._readings: dict[str, Reading] = {}
        # Heartbeat and sensor_info always exist; a sensor topic is created
        # the first time a reading qualifies, so sensor_info only lists what
        # this vehicle really has.
        self._publishers: dict[str, Publisher] = {
            topic: node.create_publisher(String, topic, 10)
            for topic in (Topics.WARA_PS_HEARTBEAT_TOPIC, Topics.WARA_PS_SENSOR_INFO_TOPIC)
        }

        node.create_subscription(GeoPoint, Topics.POS_LATLON_TOPIC, self._latlon_cb, 10)
        node.create_subscription(Odometry, Topics.ODOM_TOPIC, self._odom_cb, 10)
        for vehicle_topic, waraps_topic in (
            (Topics.HEADING_TOPIC, Topics.WARA_PS_SENSOR_HEADING_TOPIC),
            (Topics.COURSE_TOPIC, Topics.WARA_PS_SENSOR_COURSE_TOPIC),
            (Topics.SPEED_TOPIC, Topics.WARA_PS_SENSOR_SPEED_TOPIC),
            (Topics.DEPTH_TOPIC, Topics.WARA_PS_SENSOR_DEPTH_TOPIC),
            (Topics.ALTITUDE_TOPIC, Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC),
        ):
            node.create_subscription(Float32, vehicle_topic, self._scalar_cb(waraps_topic), 10)

        node.create_timer(1.0 / pulse_rate, self.pulse)
        node.get_logger().info(f"waraps_vehicle '{robot_name}' ({self._agent.agent_type}) uuid {agent_uuid}, {pulse_rate} Hz")

    # ---- inputs -------------------------------------------------------------

    def _now_s(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _latlon_cb(self, msg: GeoPoint):
        self._latlon = LatLon(msg.latitude, msg.longitude, msg.altitude, self._now_s())

    def _odom_cb(self, msg: Odometry):
        q = msg.pose.pose.orientation
        roll, pitch, _ = quat2euler([q.w, q.x, q.y, q.z])
        now = self._now_s()
        self._readings[Topics.WARA_PS_SENSOR_ROLL_TOPIC] = Reading(roll, now)
        self._readings[Topics.WARA_PS_SENSOR_PITCH_TOPIC] = Reading(pitch, now)

    def _scalar_cb(self, waraps_topic):
        def cb(msg: Float32):
            self._readings[waraps_topic] = Reading(msg.data, self._now_s())
        return cb

    # ---- outputs ------------------------------------------------------------

    def _publish(self, topic, text):
        if topic not in self._publishers:
            self._publishers[topic] = self._node.create_publisher(String, topic, 10)
        self._publishers[topic].publish(String(data=text))

    def _fresh(self, reading, now):
        return reading is not None and fresh(reading.stamp_s, now, self._stale_after_s)

    def current_levels(self):
        return levels(
            direct_execution=self._node.count_publishers(Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC) > 0,
            tst_execution=self._node.count_publishers(Topics.WARA_PS_TST_EXEC_INFO_TOPIC) > 0,
        )

    def sensor_names(self):
        found = node_string_topics_under(self._node, self._node.get_namespace(), Topics.WARA_PS_SENSOR_PREFIX)
        return [t.name for t in found]

    def pulse(self):
        now = self._now_s()
        self._publish(Topics.WARA_PS_HEARTBEAT_TOPIC, heartbeat_json(self._agent, self.current_levels(), now))

        if (self._fresh(self._latlon, now)
                and finite(self._latlon.latitude, self._latlon.longitude, self._latlon.altitude)):
            self._publish(Topics.WARA_PS_SENSOR_POSITION_TOPIC,
                          position_json(self._latlon.latitude, self._latlon.longitude, self._latlon.altitude))

        for topic, reading in self._readings.items():
            if self._fresh(reading, now) and finite(reading.value):
                self._publish(topic, scalar_json(reading.value))

        self._publish(Topics.WARA_PS_SENSOR_INFO_TOPIC, sensor_info_json(self._agent, self.sensor_names(), now))


def main(args=None):
    rclpy.init(args=args)
    node = Node('waraps_vehicle')
    WarapsVehicle(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
