#!/usr/bin/python3

import json
from rclpy.node import Node

from py_trees.blackboard import Blackboard
from py_trees.common import Status

from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange
from smarc_mission_msgs.msg import BTCommand, Topics as MissionTopics
from py_trees_ros_interfaces.msg import Behaviour

from .i_bb_updater import IBBUpdater
from .bb_keys import BBKeys

class ROSBBUpdater(IBBUpdater):
    def __init__(self,
                 node: Node,
                 initialize_bb = True):
        super().__init__()

        self._bb = Blackboard()
        self._node = node

        self._bt_cmd_sub = node.create_subscription(BTCommand,
                                                    MissionTopics.BT_COMMAND_TOPIC,
                                                    self._bt_cmd_cb,
                                                    10)
        
        self._tip_msg = Behaviour()
        self._bt_tip_pub = node.create_publisher(Behaviour,
                                                 MissionTopics.BT_TIP_TOPIC,
                                                 10)

        for key in BBKeys._member_names_:
            if initialize_bb:
                self._bb.set(key, None)


        node.declare_parameter(BBKeys.MAX_DEPTH.name, 10.0, ParameterDescriptor(
            name = BBKeys.MAX_DEPTH.name,
            description = "Maximum depth robot is allowed to dive to, usually positive float. Negative would disable it.",
            floating_point_range = [
                FloatingPointRange(
                    from_value = -1.0,
                    to_value = 100.0,
                    step = 0.1
                )
            ]
        ))


        node.declare_parameter(BBKeys.MIN_ALTITUDE.name, 2.0, ParameterDescriptor(
            name = BBKeys.MIN_ALTITUDE.name,
            description = "Minimum altitude from the seabed before emergency. Negative would disable it, usually.",
            floating_point_range = [
                FloatingPointRange(
                    from_value = -1.0,
                    to_value = 500.0,
                    step = 0.1
                )
            ]
        ))

        node.declare_parameter(BBKeys.MISSION_PLAN_STORAGE.name, "~/MissionPlans/", ParameterDescriptor(
            name = BBKeys.MISSION_PLAN_STORAGE.name,
            description = "Where mission plans given to the vehicle will be stored. Used as a cache."
        ))

        node.declare_parameter(BBKeys.DUBINS_TURNING_RADIUS.name, 5.0, ParameterDescriptor(
            name = BBKeys.DUBINS_TURNING_RADIUS.name,
            description = "Turning radius to use when refining a given plan using a dubins planner",
            floating_point_range = [
                FloatingPointRange(
                    from_value = 0.1,
                    to_value = 50.0,
                    step = 0.1
                )
            ]
        ))

        node.declare_parameter(BBKeys.DUBINS_STEP_SIZE.name, 5.0, ParameterDescriptor(
            name = BBKeys.DUBINS_STEP_SIZE.name,
            description = "How far apart points on a dubins plan should be.",
            floating_point_range = [
                FloatingPointRange(
                    from_value = 0.1,
                    to_value = 50.0,
                    step = 0.1
                )
            ]
        ))

        node.declare_parameter(BBKeys.SENSOR_INITIAL_GRACE_PERIOD.name, 10.0, ParameterDescriptor(
            name = BBKeys.SENSOR_INITIAL_GRACE_PERIOD.name,
            description = "How long to wait for a sensor to publish SOMEthing before we get suspicious. In seconds.",
            floating_point_range = [
                FloatingPointRange(
                    from_value = -1.0,
                    to_value = 5 * 60.0,
                    step = 0.1
                )
            ]
        ))

        node.declare_parameter(BBKeys.SENSOR_SILENCE_PERIOD.name, 5.0, ParameterDescriptor(
            name = BBKeys.SENSOR_SILENCE_PERIOD.name,
            description = "How long to allow silence between sensor readings. In seconds.",
            floating_point_range = [
                FloatingPointRange(
                    from_value = -1.0,
                    to_value = 5 * 60.0,
                    step = 0.1
                )
            ]
        ))

    def _log(self, s):
        self._node.get_logger().info(s)

    def _bt_cmd_cb(self, msg: BTCommand):
        if msg.msg_type == BTCommand.TYPE_FB: return
        try:
            q = self._bb.get(BBKeys.BT_CMD_QUEUE)
            if q is None: q = []
        except:
            q = []

        try:
            cmd_json = json.loads(msg.cmd_json)
            self._log(f"cmdjson:{cmd_json}")
        except:
            self._log(f"Could not parse string as json, ignoring. String:\n{cmd_json}")
            return
        
        cmd = cmd_json['cmd']
        try:
            arg = cmd_json['arg']
        except:
            arg = None
        
        q.append((cmd, arg))
        self._bb.set(BBKeys.BT_CMD_QUEUE, q)


    def set_params(self):
        self._bb.set(BBKeys.MIN_ALTITUDE,
                     self._node.get_parameter(BBKeys.MIN_ALTITUDE.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.MAX_DEPTH,
                     self._node.get_parameter(BBKeys.MAX_DEPTH.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.MISSION_PLAN_STORAGE,
                     self._node.get_parameter(BBKeys.MISSION_PLAN_STORAGE.name).get_parameter_value().string_value)
        self._bb.set(BBKeys.DUBINS_TURNING_RADIUS,
                     self._node.get_parameter(BBKeys.DUBINS_TURNING_RADIUS.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.DUBINS_STEP_SIZE,
                     self._node.get_parameter(BBKeys.DUBINS_STEP_SIZE.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.SENSOR_SILENCE_PERIOD,
                     self._node.get_parameter(BBKeys.SENSOR_SILENCE_PERIOD.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.SENSOR_INITIAL_GRACE_PERIOD,
                self._node.get_parameter(BBKeys.SENSOR_INITIAL_GRACE_PERIOD.name).get_parameter_value().double_value)
        


    def update_bb(self) -> None:
        self.set_params()

        tip = self._bb.get(BBKeys.TREE_TIP)
        if tip is None: return
        
        self._tip_msg.name = tip.name
        self._tip_msg.message = tip.feedback_message

        if tip.status == Status.SUCCESS:
            self._tip_msg.status = Behaviour.SUCCESS
        elif tip.status == Status.FAILURE:
            self._tip_msg.status = Behaviour.FAILURE
        elif tip.status == Status.RUNNING:
            self._tip_msg.status = Behaviour.RUNNING
        elif tip.status == Status.INVALID:
            self._tip_msg.status = Behaviour.INVALID
        else:
            self._tip_msg.status = 0


        self._bt_tip_pub.publish(self._tip_msg)

