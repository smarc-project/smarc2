#!/usr/bin/python3

from py_trees.blackboard import Blackboard
from .i_bb_updater import IBBUpdater
from .bb_keys import BBKeys

from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, IntegerRange, FloatingPointRange

class SAMBBUpdater(IBBUpdater):
    def __init__(self,
                 node: Node,
                 initialize_bb = True):
        super().__init__()

        self._bb = Blackboard()
        self._node = node

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



    def update_bb(self) -> None:
        self._bb.set(BBKeys.MIN_ALTITUDE,
                     self._node.get_parameter(BBKeys.MIN_ALTITUDE.name).get_parameter_value().double_value)
        self._bb.set(BBKeys.MAX_DEPTH,
                     self._node.get_parameter(BBKeys.MAX_DEPTH.name).get_parameter_value().double_value)


