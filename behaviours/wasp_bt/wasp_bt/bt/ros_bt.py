#!/usr/bin/python3

import json
from std_msgs.msg import String

import operator
import typing

import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.blackboard import Blackboard
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy
from py_trees.behaviours import Running, Success, Failure

from ..vehicles.vehicle import IVehicleStateContainer
from ..vehicles.sensor import SensorNames
from .i_has_vehicle_container import HasVehicleContainer
from .i_has_clock import HasClock
from .bb_keys import BBKeys
from ..mission.i_action_client import IActionClient

from ..waraps.waraps_task_handler import WaraPSTaskHandler, HasWaraPSTaskHandler, WaraPSTaskStates



from .conditions import C_CheckMissionPlanState,\
                        C_CheckSensorBool,\
                        C_NotAborted,\
                        C_SensorOperatorBlackboard,\
                        C_MissionTimeoutOK,\
                        C_TaskIs,\
                        C_TaskStatus,\
                        C_AbortedPreviousTask,\
                        C_NoEmergencyAbortSignalDetected

from .actions import A_Abort,\
                     A_Heartbeat,\
                     A_ActionClient,\
                    A_JustChillFor,\
                    A_ClearTaskQueue,\
                    A_TaskAbortedFlagReset, \
                    A_Chilling,\
                     A_ClearCurrentTask

class BT(HasVehicleContainer, HasClock, HasWaraPSTaskHandler):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer,
                 task_handler:WaraPSTaskHandler,
                 now_seconds_func: typing.Callable,
                 move_to_action: IActionClient = None,
                 move_depth_action: IActionClient = None,
                cruise_depth_action: IActionClient = None,
                 ):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._task_handler = task_handler
        self._bt = None
        self.move_to_action = move_to_action
        self.move_depth_action = move_depth_action
        self.cruise_depth_action = cruise_depth_action
        self._now_seconds_func = now_seconds_func

        self._last_state_str = ""


    @property
    def vehicle_container(self) -> IVehicleStateContainer:
        return self._vehicle_container
    
    @property
    def mqtt_interactor(self) -> typing.Any:
        return self._task_handler
    
    @property
    def now_seconds(self) -> int:
        return self._now_seconds_func()
    
    def _liveliness_tree(self):
        liveliness_tree = Parallel("P_Liveliness", policy=ParallelPolicy.SuccessOnAll(synchronise=False) , children=[
            A_WaitForData(self, SensorNames.VEHICLE_HEALTHY),
            A_WaitForData(self, SensorNames.POSITION)
            # Maybe add other sensors too, depth, altitude?
        ])

        return liveliness_tree

 
    def _safety_tree(self):
        safety_checks = Parallel("P_Safetty_Checks", policy=ParallelPolicy.SuccessOnAll(synchronise=False) , children=[
            C_NotAborted(self),
            C_CheckSensorBool(self, SensorNames.VEHICLE_HEALTHY),
            Inverter("Not leaking", C_CheckSensorBool(self, SensorNames.LEAK)),
            C_SensorOperatorBlackboard(self, SensorNames.ALTITUDE, operator.gt, BBKeys.MIN_ALTITUDE),
            C_SensorOperatorBlackboard(self, SensorNames.DEPTH, operator.lt, BBKeys.MAX_DEPTH),
            C_MissionTimeoutOK()
        ])

        safety_tree = Fallback("F_Safety", memory=False, children=[
            safety_checks,
            # modify mission?
            Parallel("P_EMERGENCY", policy=ParallelPolicy.SuccessOnAll(synchronise=False), children=[
                A_Abort(self),
                Running("TODO: A_EmergencyAction")
            ])
        ])

        return safety_tree
    
    def _handle_emergency_tree(self):
        """
        A tree that handles emergency situations, such as aborting the mission
        """
        return Fallback("F_HandleEmergency", memory=False, children=[
            C_NoEmergencyAbortSignalDetected(self._task_handler),
            # chill for a bit
            A_Chilling(self), # should be replaced with EmergencyAction from Li
        ])
                    
    def _one_task_tree(self, task_name: str, action_client: IActionClient):
        """
        A tree that handles a single task type, such as move-to or depth-move-to
        """
        task_tree = Sequence(f"S_{task_name}", memory=False, children=[
            C_TaskIs(self._task_handler, task_name),
            Fallback("F_StatusCheck", memory=False, children=[
                C_TaskStatus(self._task_handler, WaraPSTaskStates.STARTED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RESUMED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RUNNING.value),
            ]),
            A_ActionClient(action_client, self._task_handler),
            # when done, clear the task queue
            A_ClearCurrentTask(self._task_handler),
        ])

        return task_tree


    def _task_handler_tree(self):
        """
        Fallback root node, connecting together sequences of {is the current action a certain kind of action? If so, run the corresponding action server}
        """

        task_handler = Fallback("F_Task_Handler", memory=False, children=[
            
            Sequence("S_BreathAfterAborting", memory=False, children=[
                C_AbortedPreviousTask(self._task_handler),
                # chill for a bit
                # A_JustChillFor(self, 5.0),
                # reset the aborted flag
                A_TaskAbortedFlagReset(self._task_handler),
            ]),

            # is the current task a move to task? If so, do it
            # Sequence("S_MoveTo", memory=False, children=[
            #     C_TaskIs(self._task_handler, "move-to"),
            #     Fallback("F_StatusCheck", memory=False, children=[
            #         C_TaskStatus(self._task_handler, WaraPSTaskStates.STARTED),
            #         C_TaskStatus(self._task_handler, WaraPSTaskStates.RESUMED),
            #         C_TaskStatus(self._task_handler, WaraPSTaskStates.RUNNING),
            #     ]),
            #     #TODO: need to handle task failure gracefully
            #     A_ActionClient(self.move_to_action, self._task_handler),
            #     # when done, clear the task queue
            #     A_ClearCurrentTask(self._task_handler),
            #     # A_ClearTaskQueue(self._task_handler),
            #     ]),
            self._one_task_tree("move-to", self.move_to_action),
            self._one_task_tree("auv-depth-move-to", self.move_depth_action),
            self._one_task_tree("cruise-depth-at-heading", self.cruise_depth_action),

            #TODO: implement more tasks types

            # last type: just do nothing
            A_Chilling(self),
            # succeed by default
            # Success(),
        ])

        return task_handler

    def setup(self) -> bool:

        children = [
            A_Heartbeat(self),
            self._handle_emergency_tree(),
            # self._liveliness_tree(),
            
            # self._safety_tree(), # should look at julian safety node topic

            # add the mission tree
            self._task_handler_tree(),
            # self._run_tree()
        ]

        # clean out Nones   
        children = [c for c in children if c is not None]

        # make the sequence tree
        root = Sequence("S_Root", memory=False, children=children)

        self._bt = pt.trees.BehaviourTree(root)
        return self._bt.setup()



    def tick(self):
        self._bt.tick()


def wasp_bt():
    from ..vehicles.smarc_vehicle import GenericSMaRCVehicle
    from ..vehicles.vehicle import VehicleState, UnderwaterVehicleState
    from wasp_bt.bt.client import BTActionClient

    from go_to_geopoint.geopoint_client import GeopointClient

    from smarc_action_base.smarc_action_base import (
        ActionFeedback,
        ActionResult,
        ActionType,
        SMARCActionClient,
    )
    from smarc_mission_msgs.action import BaseAction

    import rclpy, sys
    import uuid

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("wasp_bt_executor")

    def ros_seconds() -> int:
        nonlocal node
        secs, _ = node.get_clock().now().seconds_nanoseconds()
        return int(secs)
    
    def ros_seconds_float() -> float:
        nonlocal node
        secs, nsecs = node.get_clock().now().seconds_nanoseconds()
        return float(secs) + float(nsecs) * 1e-9

    
    # agent = SAMAuv(node)
    agent = GenericSMaRCVehicle(node, UnderwaterVehicleState)
    action_type = ActionType(BaseAction)
    
    # for drone, use the following line
    action_client_move_to = BTActionClient(node, "move_to", action_type)
    # for lolo, use the following line
    action_client_move_depth = BTActionClient(node, "auv_depth_move_to", action_type)
    action_client_cruise_depth = BTActionClient(node, "cruise_depth_at_heading", action_type)
    


    # Declare and get parameters with defaults
    node.declare_parameter("agent_type", "air")
    node.declare_parameter("levels", ["sensor", "direct_execution"])
    node.declare_parameter("pulse_rate", 1)
    node.declare_parameter("domain", "simulation")

    agent_type = node.get_parameter("agent_type").value
    levels = node.get_parameter("levels").value
    pulse_rate = node.get_parameter("pulse_rate").value
    robot_name = node.get_parameter("robot_name").value if node.has_parameter("robot_name") else "sam0"

    agent_waraps_dict = {
            "agent-type": agent_type,
            "agent-uuid": None, # there is a callback in the WaraPSTaskHandler that will read this from the lvl1 WaraPSVehicle
            "levels": levels,
            "name": robot_name,
            "pulse_rate": pulse_rate,
        }
    
    wara_ps_task_handler = WaraPSTaskHandler(node, agent_waraps_dict)
    bt = BT(vehicle_container = agent,
            task_handler    = wara_ps_task_handler,
            move_to_action    = action_client_move_to,
            move_depth_action= action_client_move_depth,
            cruise_depth_action = action_client_cruise_depth,
            now_seconds_func  = ros_seconds_float)
    bt.setup()


    bt_str = ""
    def print_bt():
        nonlocal bt, bt_str, node, action_client_move_to, agent
        new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
        if new_str != bt_str:
            s = f"\nBT::\n{new_str}\n"
            # s += f"GOTOWP Client::\n{action_client_move_to.feedback_message}\n\n"
            s+= f"WARA PS Task Handler::\n{wara_ps_task_handler}\n"
            s += f"Vehicle::\nAborted:{agent.vehicle_state.aborted}\nHealthy:{agent.vehicle_state.vehicle_healthy}\n"
            node.get_logger().info(s)
            bt_str = new_str


    def update():
        nonlocal bt
        bt.tick()
        print_bt()
        
    node.create_timer(0.1, update)
    # node.create_timer(0.5, print_bt)

    def wara_ps_lvl_2_comms():
        nonlocal wara_ps_task_handler

        # get the current time
        now_time = ros_seconds_float()
        # task execution info
        wara_ps_task_handler.lvl_2_heartbeat(now_time)
        # tst execution info
        wara_ps_task_handler.lvl_3_heartbeat(now_time)

    node.create_timer(1.0/wara_ps_task_handler.wara_ps_dict["pulse_rate"], wara_ps_lvl_2_comms)

    rclpy.spin(node)