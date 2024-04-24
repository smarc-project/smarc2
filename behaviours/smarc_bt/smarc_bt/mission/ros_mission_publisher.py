#!/usr/bin/python3

from rclpy.node import Node
from py_trees.blackboard import Blackboard

from smarc_mission_msgs.msg import MissionControl
from smarc_mission_msgs.msg import Topics as MissionTopics

from ..bt.bb_keys import BBKeys
from .i_mission_publisher import IMissionPublisher
from .ros_waypoint import SMaRCWP

class ROSMissionPublisher(IMissionPublisher):
    def __init__(self,
                 node: Node) -> None:
        
        self._node = node
        self._bb = Blackboard()

        self._mission_control_pub = node.create_publisher(MissionControl,
                                                          MissionTopics.MISSION_CONTROL_TOPIC,
                                                          10)

        self._feedback_message = ""

    @property
    def feedback_message(self) -> str:
        return str(self._feedback_message)
    

    def _log(self, s:str):
        self._node.get_logger().info(s)


    def publish(self) -> bool:
        mplan = self._bb.get(BBKeys.MISSION_PLAN)
        if mplan is None:
            self._feedback_message = "No mission plan to publish"
            return False
        
               
        mc = MissionControl()
        mc.command = MissionControl.CMD_IS_FEEDBACK
        mc.name = mplan._plan_id
        mc.hash = mplan._hash
        mc.waypoints = []

        if len(mplan._waypoints) == 0:
            self._mission_control_pub.publish(mc)
            self._feedback_message = f"Published plan:{mc.name} with 0 wps"
            return True
        
        for wp in mplan._waypoints:
            if type(wp) != SMaRCWP:
                self._feedback_message = f"Plan {mc.name} had a non-ros WP in it."
                return False
            mc.waypoints.append(wp._goto_wp)

        self._mission_control_pub.publish(mc)
        self._feedback_message = f"Published plan:{mc.name} with {len(mc.waypoints)} wps"
        return True
            
