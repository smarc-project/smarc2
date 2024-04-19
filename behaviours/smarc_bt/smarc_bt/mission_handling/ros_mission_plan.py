#!/usr/bin/python3

from rclpy.node import Node

from .waypoint import IWaypoint
from .mission_plan import MissionPlan, MissionPlanStates

from smarc_mission_msgs.msg import Topics as MissionTopics
from std_msgs.msg import Empty

class ROSMissionPlan(MissionPlan):
    def __init__(self,
                 node: Node,
                 plan_id: str,
                 waypoints: list[IWaypoint]) -> None:
        super().__init__(plan_id, waypoints)
        self._node = node

        self._complete_pub = self._node.create_publisher(Empty, MissionTopics.MISSION_COMPLETE_TOPIC, 10)

    def _log(self, s):
        self._node.get_logger().info(s)

    def complete(self) -> bool:
        self._complete_pub.publish(Empty())
        return super().complete()

    
        