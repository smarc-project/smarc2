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

from smarc_action_base.smarc_action_base import ActionType
from wasp_bt.bt.client import BTActionClient
from smarc_mission_msgs.action import BaseAction



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
                    A_WaitForData,\
                     A_ClearCurrentTask

class BT(HasVehicleContainer, HasClock, HasWaraPSTaskHandler):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer,
                 task_handler:WaraPSTaskHandler,
                 now_seconds_func: typing.Callable,
                 emergency_action: BTActionClient = None,
                 action_client_list: typing.List[BTActionClient] = None
                 ):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._task_handler = task_handler
        self._bt = None
        self.action_client_list = action_client_list
        self._now_seconds_func = now_seconds_func
        self.emergency_action = emergency_action

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

        emergency_children = [C_NoEmergencyAbortSignalDetected(self._task_handler)]
        if self.emergency_action is not None:
            # if there is an emergency action given to us
            # first, check if the action client is available
            availability_check = self.emergency_action._setup(num_iters=3)
            if not availability_check:
                # if the action client is not available, we cannot run it
                # we can just chill
                emergency_children.append(A_Chilling(self))
            else:
                # if the action client is available, we can run it
                emergency_children.append(A_ActionClient(self.emergency_action, self._task_handler))
        else:
            # if there is no emergency action, we can just chill
            emergency_children.append(A_Chilling(self))

        return Fallback("F_HandleEmergency", memory=False, children=emergency_children)
                    
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


    def _task_handler_tree(self, action_client_list: typing.List[IActionClient] = None):
        """
        Fallback root node, connecting together sequences of {is the current action a certain kind of action? If so, run the corresponding action server}
        """

        task_children = [
            # check if the previous task was aborted, if so, reset the flag
            Sequence("S_BreatheAfterAbort", memory=False, children=[
                C_AbortedPreviousTask(self._task_handler),
                A_TaskAbortedFlagReset(self._task_handler),
            ]),
        ]


        # create a action_client_list from the heartbeats of action clients, as stored by the WaraPSTaskHandler

        tasks_available = self._task_handler.get_available_tasks()

        ros_task_names = []

        for i in range(len(tasks_available)):
            # we will wait for the next task to be available
            ros_task_name = tasks_available[i]["ros_name"]
            ros_task_names.append(ros_task_name)
            
        # self._task_handler._node.get_logger().info(f"Available tasks: {ros_task_names}")

        # if action_client_list is None, we will use the action clients from the WaraPSTaskHandler
        if action_client_list == None:
            action_type = ActionType(BaseAction)
            
            action_client_list = [BTActionClient(self._task_handler._node, ros_task_name, action_type) for ros_task_name in ros_task_names]


        # we will append the task trees to this list programmatically
        if action_client_list is not None:
            #TODO: implement this
            self._task_handler._node.get_logger().info(f"Action clients: {[ac.get_action_name() for ac in action_client_list]}")

            for action_client in action_client_list:

                # first, check if the corresponding action server is available
                availability_check = action_client._setup(num_iters = 3)

                if not availability_check:
                    # if the action client is not available, skip it
                    continue

                # if the action client is available, we can proceed

                # parse the action client name to get the task name according to the WaraPS naming convention
                task_name = action_client.get_action_name().split('/')[-1].replace("_", "-")

                task_tree = self._one_task_tree(task_name, action_client)
                task_children.append(task_tree)

        # add the chill task
        task_children.append(A_Chilling(self))

        task_handler = Fallback("F_Task_Handler", memory=False, children=task_children)
                                
        return task_handler

    def setup(self) -> bool:

        children = [
            A_Heartbeat(self),
            self._handle_emergency_tree(),
            # self._liveliness_tree(),
            
            # self._safety_tree(), # should look at julian safety node topic

            # add the mission tree
            self._task_handler_tree(self.action_client_list),
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
        
    # emergency action
    emergency_action_client = BTActionClient(node, "emergency_action", action_type)
    # emergency_action_client = None

    # list of remaining action clients
    action_client_list = [
        BTActionClient(node, "move_to", action_type),
        BTActionClient(node, "auv_depth_move_to", action_type),
        BTActionClient(node, "cruise_depth_at_heading", action_type),
        # ADD NEW ACTION CLIENTS HERE

    ]

    # action_client_list = None

    # Declare and get parameters with defaults
    node.declare_parameter("agent_type", "air")
    node.declare_parameter("levels", ["sensor", "direct_execution"])
    node.declare_parameter("pulse_rate", 1.0) # Hz
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
            emergency_action = emergency_action_client,
            # action_client_list = action_client_list,
            # the commented out line above means that you're listening for available tasks from the WaraPSTaskHandler. You can also provide a list of action clients to use if you like.
            now_seconds_func  = ros_seconds_float)
    # bt.setup()
    need_bt_setup = False
    is_bt_setup = False


    bt_str = ""
    def print_bt():
        nonlocal bt, bt_str, node, action_client_list, agent
        new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
        if new_str != bt_str:
            s = f"\nBT::\n{new_str}\n"
            s+= f"WARA PS Task Handler::\n{wara_ps_task_handler}\n"
            s += f"Vehicle::\nAborted:{agent.vehicle_state.aborted}\nHealthy:{agent.vehicle_state.vehicle_healthy}\n"
            node.get_logger().info(s)
            bt_str = new_str


    def update():
        nonlocal bt, is_bt_setup, need_bt_setup

        if not is_bt_setup and need_bt_setup:
            bt.setup()
            is_bt_setup = True
            need_bt_setup = False

        if is_bt_setup:
            bt.tick()
            print_bt()
        
    node.create_timer(0.1, update)
    # node.create_timer(0.5, print_bt)

    start_time = None

    def wara_ps_lvl_2_comms():
        nonlocal wara_ps_task_handler, need_bt_setup, start_time, node

        # get the current time
        now_time = ros_seconds_float()
        if start_time is None:
            start_time = now_time
        # task execution info
        wara_ps_task_handler.lvl_2_heartbeat(now_time)
        # tst execution info
        wara_ps_task_handler.lvl_3_heartbeat(now_time)

        if not is_bt_setup:
            # if the BT is not ticking, we can start it
            if now_time - start_time > 2.0: # give 2 seconds for living action servers to provide a heartbeat to the WaraPSTaskHandler object
                need_bt_setup = True
            else:
                node.get_logger().info(f"Waiting for action servers to provide heartbeat, current time: {now_time}, start time: {start_time}, diff: {now_time - start_time}")

    node.create_timer(1.0/wara_ps_task_handler.wara_ps_dict["pulse_rate"], wara_ps_lvl_2_comms)

    rclpy.spin(node)