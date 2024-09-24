#!/usr/bin/python3

from rclpy.node import Node

from .ros_waypoint import ROSWP
from .mission_plan import MissionPlan, MissionPlanStates

from smarc_mission_msgs.msg import Topics as MissionTopics, MissionControl
from smarc_msgs.msg import Topics as SmarcTopics

from std_msgs.msg import Empty

class ROSMissionPlan(MissionPlan):
    def __init__(self,
                 node: Node,
                 plan_id: str,
                 hash: str,
                 timeout: int,
                 waypoints: list[ROSWP]) -> None:
        """
        Same mission plan, but this one logs into ros
        and publishes into a topic its state when needed.
        """
        super().__init__(plan_id, hash, timeout, waypoints)
        self._node = node

        self._complete_pub = node.create_publisher(Empty, MissionTopics.MISSION_COMPLETE_TOPIC, 10)
        self._abort_pub = node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)
        self._mission_control_pub = node.create_publisher(MissionControl,
                                                          MissionTopics.MISSION_CONTROL_TOPIC,
                                                          10)
        
        self._publish_mission()
        

    def _log(self, s):
        self._node.get_logger().info(s)

    def _get_time(self):
        secs, _ = self._node.get_clock().now().seconds_nanoseconds()
        return secs


    def complete(self) -> bool:
        self._complete_pub.publish(Empty())
        return super().complete()
    
    def emergency(self) -> bool:
        self._abort_pub.publish(Empty())
        return super().emergency()
    
    def _publish_mission(self):
        mc = MissionControl()
        mc.command = MissionControl.CMD_IS_FEEDBACK
        mc.name = self._plan_id
        mc.hash = self._hash
        mc.waypoints = []

        if len(self._waypoints) == 0:
            self._mission_control_pub.publish(mc)
            self._feedback_message = f"Published plan:{mc.name} with 0 wps"
            return
        
        for wp in self._waypoints:
            if type(wp) != ROSWP:
                self._feedback_message = f"Plan {mc.name} had a non-ros WP in it."
                return
            mc.waypoints.append(wp.goto_wp)

        self._mission_control_pub.publish(mc)
        self._feedback_message = f"Published plan:{mc.name} with {len(mc.waypoints)} wps"
        return True


        

    def _change_state(self, new_state: MissionPlanStates) -> bool:
        self._publish_mission()
        return super()._change_state(new_state)
        

