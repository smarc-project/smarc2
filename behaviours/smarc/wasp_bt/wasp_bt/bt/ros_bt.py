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
from smarc_msgs.msg import Topics as SMaRCTopics

from ..vehicles.vehicle import IVehicleStateContainer
from ..vehicles.sensor import SensorNames
from .i_has_vehicle_container import HasVehicleContainer
from .i_has_clock import HasClock

from wasp_bt.waraps.waraps_task_handler import WaraPSTaskHandler, HasWaraPSTaskHandler, WaraPSTaskStates

from smarc_action_base.smarc_action_base import ActionType
from wasp_bt.bt.client import BTActionClient
from smarc_msgs.action import BaseAction



from .conditions import C_TaskIs,\
                        C_TaskStatus,\
                        C_AbortedPreviousTask,\
                        C_NoEmergencyAbortSignalDetected,\
                        C_VehicleHealthStatus,\
                        C_HealthNodeAlive,\
                        C_HasHeardFromVehicleHealth,\
                        C_MissionNotInError

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
                 get_ready_action: BTActionClient = None,
                 emergency_action: BTActionClient = None,
                 action_client_list: typing.List[BTActionClient] = None,
                 bt_health_timeout: float = 10.0
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
        self.get_ready_action = get_ready_action

        self._last_state_str = ""

        self._bt_health_timeout = bt_health_timeout

        # Keep action client instances alive across tree rebuilds so in-flight
        # goals and cancel handles remain reachable.
        self._action_client_cache: typing.Dict[str, BTActionClient] = {}
        
        # Add tracking for dynamic tree updates
        self._last_available_tasks = []
        self._task_handler_node = None  # Reference to the task handler node in the tree

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
    
    def _health_tree(self):
        """
        A tree that checks the health status of the vehicle
        """

        health_checks = Fallback("F_Health_Handler", memory=False, children=[
            Sequence("S_Health_Status", memory=False, children=[
                # C_HasHeardFromVehicleHealth(self._task_handler),  # check if the vehicle health returns SUCCESS (Vehicle is ready)
                C_HealthNodeAlive(self._task_handler, timeout=self._bt_health_timeout),  # check if the last heartbeat was within 10 seconds
                Fallback("F_Health_Checks", memory=False, children=[
                    C_VehicleHealthStatus(self._task_handler, desired_status = SMaRCTopics.VEHICLE_HEALTH_READY),
                    C_VehicleHealthStatus(self._task_handler, desired_status = SMaRCTopics.VEHICLE_HEALTH_WAITING),
                ]),
            ]),
            A_Abort(self._task_handler),
        ])

        return health_checks

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
                emergency_children.append(
                    A_ActionClient(
                        self.emergency_action, 
                        bt = self,
                        task_handler = self._task_handler
                    )
                )
        else:
            # if there is no emergency action, we can just chill
            emergency_children.append(A_Chilling(self))

        return Fallback("F_HandleEmergency", memory=False, children=emergency_children)
                    
    def _one_task_tree(self, task_name: str, action_client: BTActionClient):
        """
        A tree that handles a single task type, such as move-to or depth-move-to
        """
        task_tree = Sequence(f"S_{task_name}", memory=False, children=[
            C_MissionNotInError(self._task_handler),  # Fail immediately if mission is in ERROR
            C_TaskIs(self._task_handler, task_name),
            Fallback("F_StatusCheck", memory=False, children=[
                C_TaskStatus(self._task_handler, WaraPSTaskStates.STARTED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RESUMED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RUNNING.value),
            ]),

            # run the action client
            A_ActionClient(
                action_client,
                bt = self,
                task_handler = self._task_handler
            ),
            # when done, clear the task queue
            A_ClearCurrentTask(self._task_handler),
        ])

        return task_tree

    def _get_ready_tree(self, task_name: str, action_client: BTActionClient):
        """
        A tree that handles a single task type, such as move-to or depth-move-to
        """


        # check if the action server is alive (setup like below)
        status = action_client._setup(num_iters=1, timeout = 0.5)
        if not status:
            # if the action server is not alive, we cannot run the action
            self._task_handler._node.get_logger().warn(f"Action server for {task_name} is not alive")

            # remove the action from the available tasks in the WaraPSTaskHandler so that it doesn't show up in the task handler tree
            removed = self._task_handler.remove_available_task(task_name=task_name)
            if removed:
                self._task_handler._node.get_logger().info(
                    f"Removed unavailable task '{task_name}' from available tasks"
                )
            
            return None

        ready_tree = Sequence(f"S_{task_name}", memory=False, children=[

            C_MissionNotInError(self._task_handler),  # Fail immediately if mission is in ERROR

            Fallback("F_CanIGetReady?", memory=False, children = [
                C_VehicleHealthStatus(self._task_handler, desired_status = SMaRCTopics.VEHICLE_HEALTH_WAITING),
                C_VehicleHealthStatus(self._task_handler, desired_status = SMaRCTopics.VEHICLE_HEALTH_READY),
            ]),

            C_TaskIs(self._task_handler, task_name),
            Fallback("F_StatusCheck", memory=False, children=[
                C_TaskStatus(self._task_handler, WaraPSTaskStates.STARTED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RESUMED.value),
                C_TaskStatus(self._task_handler, WaraPSTaskStates.RUNNING.value),
            ]),

            # run the action client
            A_ActionClient(
                action_client,
                bt = self,
                task_handler = self._task_handler
            ),
            # when done, clear the task queue
            A_ClearCurrentTask(self._task_handler),
        ])

        return ready_tree


    def _task_handler_tree(self, action_client_list: typing.List[BTActionClient] = None):
        """
        Fallback root node, connecting together sequences of {is the current action a certain kind of action? If so, run the corresponding action server}
        """

        def _remember_action_client(action_client: BTActionClient):
            self._action_client_cache[action_client.get_action_name()] = action_client
            return action_client

        def _get_or_create_action_client(ros_task_name: str, action_type: ActionType):
            cached_action_client = self._action_client_cache.get(ros_task_name)
            if cached_action_client is not None:
                return cached_action_client

            return _remember_action_client(
                BTActionClient(self._task_handler._node, ros_task_name, action_type)
            )

        task_children = [
            # check if the previous task was aborted, if so, reset the flag
            Sequence("S_BreatheAfterAbort", memory=False, children=[
                C_AbortedPreviousTask(self._task_handler),
                A_TaskAbortedFlagReset(self._task_handler),
            ]),
        ]

        if self.get_ready_action is not None:
            get_ready_tree = self._get_ready_tree("get-ready", self.get_ready_action)
            if get_ready_tree is not None:
                task_children.append(get_ready_tree)

        # create a action_client_list from the heartbeats of action clients, as stored by the WaraPSTaskHandler

        tasks_available = self._task_handler.get_available_tasks()

        ros_task_names = []

        for i in range(len(tasks_available)):
            # we will wait for the next task to be available
            ros_task_name = tasks_available[i]["ros_name"]
            
            # only append to the list of available task if it's not the emergency task. We don't want emergency to be available to the user in the task handler tree.
            if "emergency" not in ros_task_name and "ready" not in ros_task_name:
                ros_task_names.append(ros_task_name)
            
        # self._task_handler._node.get_logger().info(f"Available tasks: {ros_task_names}")

        # if action_client_list is None, we will use the action clients from the WaraPSTaskHandler
        if action_client_list == None:
            action_type = ActionType(BaseAction)
            
            action_client_list = [
                _get_or_create_action_client(ros_task_name, action_type)
                for ros_task_name in ros_task_names
            ]
        else:
            for action_client in action_client_list:
                _remember_action_client(action_client)

        mission_children = [
            C_VehicleHealthStatus(self._task_handler, desired_status=SMaRCTopics.VEHICLE_HEALTH_READY)
        ]

        mission_task_children = []

        # we will append the task trees to this list programmatically
        if action_client_list is not None:
            self._task_handler._node.get_logger().info(f"Action clients: {[ac.get_action_name() for ac in action_client_list]}")

            for action_client in action_client_list:

                # first, check if the corresponding action server is available
                availability_check = action_client._setup(num_iters = 1, timeout = 0.5)

                if not availability_check:
                    # if the action client is not available, skip it
                    continue

                # if the action client is available, we can proceed

                # parse the action client name to get the task name according to the WaraPS naming convention
                task_name = action_client.get_action_name().split('/')[-1].replace("_", "-")

                task_tree = self._one_task_tree(task_name, action_client)
                mission_task_children.append(task_tree)

        # make a fallback out of mission_task_children
        mission_task_fallback = Fallback("F_Tasks", memory=False, children=mission_task_children)

        # add mission_task_fallback to the mission_children
        mission_children.append(mission_task_fallback)

        # construct the mission tree
        mission_tree = Sequence("S_Mission", memory=False, children=mission_children)


        # add the mission tree to task handler
        task_children.append(mission_tree)

        # add the chill task
        task_children.append(A_Chilling(self))

        task_handler = Fallback("F_Task_Handler", memory=False, children=task_children)
                                
        return task_handler

    def _update_task_handler_tree(self):
        """
        Check if available tasks have changed and rebuild the task handler subtree if needed.
        Returns True if tree was updated, False otherwise.
        """
        if self._bt is None or self._task_handler_node is None:
            return False
            
        # Get current available tasks
        current_tasks = self._task_handler.get_available_tasks()
        current_task_names = [task["ros_name"] for task in current_tasks 
                             if "emergency" not in task["ros_name"] and "ready" not in task["ros_name"]]
        
        # Check if tasks have changed
        if set(current_task_names) != set(self._last_available_tasks):
            self._task_handler._node.get_logger().info(
                f"Tasks changed from {self._last_available_tasks} to {current_task_names}. Rebuilding tree..."
            )
            
            # Rebuild the task handler tree
            new_task_handler = self._task_handler_tree(self.action_client_list)
            
            # Find the task handler node in the tree and replace it
            # This assumes F_Task_Handler is a direct child of S_Root
            root = self._bt.root
            for i, child in enumerate(root.children):
                if child.name == "F_Task_Handler":
                    # Replace the old node with the new one
                    root.children[i] = new_task_handler
                    # Setup the new subtree
                    new_task_handler.setup_with_descendants()
                    self._task_handler_node = new_task_handler
                    break
            
            self._last_available_tasks = current_task_names
            return True
            
        return False

    def setup(self) -> bool:

        children = [
            A_Heartbeat(self),
            self._handle_emergency_tree(),
            # self._liveliness_tree(),
            self._health_tree(),
            
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
        
        # Store reference to task handler node for dynamic updates
        for child in root.children:
            if child.name == "F_Task_Handler":
                self._task_handler_node = child
                break
        
        # Initialize tracking for available tasks
        tasks_available = self._task_handler.get_available_tasks()
        self._last_available_tasks = [task["ros_name"] for task in tasks_available 
                                     if "emergency" not in task["ros_name"] and "ready" not in task["ros_name"]]
        
        return self._bt.setup()



    def tick(self):
        # Update tree structure before ticking if tasks changed
        self._update_task_handler_tree()
        self._bt.tick()


def wasp_bt():
    from ..vehicles.smarc_vehicle import GenericSMaRCVehicle
    from ..vehicles.vehicle import VehicleState, UnderwaterVehicleState
    from wasp_bt.bt.client import BTActionClient
    from smarc_msgs.msg import Topics

    from smarc_action_base.smarc_action_base import (
        ActionFeedback,
        ActionResult,
        ActionType,
        SMARCActionClient,
    )
    from smarc_msgs.action import BaseAction

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


    bt_status_pub = node.create_publisher(String, Topics.BT_STATUS_TOPIC, qos_profile=10)

    
    # agent = SAMAuv(node)
    agent = GenericSMaRCVehicle(node, UnderwaterVehicleState)
    action_type = ActionType(BaseAction)
    
    # get-ready action client: None if does not exist, else
    get_ready_action_client = BTActionClient(node, "get_ready", action_type)
    # get_ready_action_client = None

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
    node.declare_parameter("pulse_rate", 1.0) # Hz
    node.declare_parameter("domain", "simulation")

    agent_type = node.get_parameter("agent_type").value
    levels = ["sensor", "direct_execution", "tst_execution"]
    pulse_rate = node.get_parameter("pulse_rate").value
    robot_name = node.get_parameter("robot_name").value if node.has_parameter("robot_name") else "sam0"

    agent_waraps_dict = {
            "agent-type": agent_type,
            "agent-uuid": None, # there is a callback in the WaraPSTaskHandler that will read this from the lvl1 WaraPSVehicle
            "levels": levels,
            "name": robot_name,
            "pulse_rate": pulse_rate,
        }
    
    # declare the parameter for printing bt (mode)
    node.declare_parameter("bt_log_mode", "verbose") # can be "verbose" or "compact"
    bt_log_mode = node.get_parameter("bt_log_mode").value

    
    # start_offset = 5.0
    node.declare_parameter("bt_launch_delay", 5.0) # seconds
    bt_launch_delay = node.get_parameter("bt_launch_delay").value

    # get the BT timeout ros parameter
    node.declare_parameter("bt_health_timeout", 15.0) # seconds
    bt_health_timeout = node.get_parameter("bt_health_timeout").value

    # timeout for considering action-server heartbeats stale in task discovery
    node.declare_parameter("task_liveliness_timeout", 10.0) # seconds
    task_liveliness_timeout = node.get_parameter("task_liveliness_timeout").value


    wara_ps_task_handler = WaraPSTaskHandler(
        node,
        agent_waraps_dict,
        start_offset=bt_launch_delay,
        task_liveliness_timeout=task_liveliness_timeout,
    )
    bt = BT(vehicle_container = agent,
            task_handler    = wara_ps_task_handler,
            get_ready_action = get_ready_action_client,
            emergency_action = emergency_action_client,
            # action_client_list = action_client_list,
            # the commented out line above means that you're listening for available tasks from the WaraPSTaskHandler. You can also provide a list of action clients to use if you like.
            now_seconds_func  = ros_seconds_float,
            bt_health_timeout        = bt_health_timeout
            )
    # bt.setup()
    need_bt_setup = False
    is_bt_setup = False

    bt_tip = None
    old_bt_tip = None

    bt_str = ""
    def print_bt(mode: str = "verbose"): # can be "verbose" or "compact"
        nonlocal bt, bt_str, node, action_client_list, agent, wara_ps_task_handler, bt_tip, old_bt_tip

        if mode == "verbose":
            new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
            if new_str != bt_str:
                s = f"\nBT::\n{new_str}\n"
                s+= f"WARA PS Task Handler::\n{wara_ps_task_handler}\n"
                node.get_logger().info(s)
                bt_str = new_str
            return
        elif mode == "compact":
            # print a compact version of the BT
            # log that you're here
            # node.get_logger().info("Printing compact BT...")
            new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
            if new_str != bt_str:

                new_tip = bt._bt.root.tip()
                if  old_bt_tip is None or new_tip!= old_bt_tip:
                    old_bt_tip = new_tip
                    s = f"\nBT::\n{new_str}\n"
                    bt_str = new_str

                    s+= f"WARA PS Task Handler::\n{wara_ps_task_handler}\n"
                    node.get_logger().info(s)
            return

            

    def update():
        nonlocal bt, is_bt_setup, need_bt_setup

        if not is_bt_setup and need_bt_setup:
            bt.setup()
            is_bt_setup = True
            need_bt_setup = False

        if is_bt_setup:
            bt.tick()
            print_bt(mode=bt_log_mode)
    
    def check_tree_updates():
        """Periodically check if available tasks have changed (separate from tick for efficiency)"""
        nonlocal bt, is_bt_setup
        if is_bt_setup:
            # The actual update happens in tick(), this is just for logging purposes
            # or you could call bt._update_task_handler_tree() here if you want less frequent checks
            pass
        
    node.create_timer(0.1, update)
    node.create_timer(5.0, check_tree_updates)  # Optional: Add explicit periodic check
    # node.create_timer(0.5, print_bt)

    def publish_bt_tip():
        nonlocal bt, node, wara_ps_task_handler

        # publish the BT tip to the WaraPS task handler
        if is_bt_setup:
            bt_tip = bt._bt.root.tip()
            if bt_tip is not None:
                # parse the tip to a string
                tip_str = f"{bt_tip.name} ({bt_tip.status})"
                # publish the tip to the WaraPS task handler
                wara_ps_task_handler.publish_bt_tip(tip_str)
        else:
            node.get_logger().info("BT is not setup yet, cannot publish tip.")
    
    node.create_timer(1, publish_bt_tip) 
    
    def pub_bt_status():
        nonlocal bt_status_pub, bt, node, is_bt_setup
        
        if not is_bt_setup:
            # node.get_logger().warn("BT is not setup yet, cannot publish status.")
            return
        # publish the BT status to the BT_STATUS_TOPIC
        bt_status_pub.publish(String(data=pt.display.ascii_tree(bt._bt.root, show_status=True)))

    # create a timer to publish the BT status to BT_STATUS_TOPIC
    status_str_timer = node.create_timer(0.1,pub_bt_status)

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
            if now_time - start_time > bt_launch_delay: # give 5 seconds for living action servers to provide a heartbeat to the WaraPSTaskHandler object
                need_bt_setup = True
            else:
                node.get_logger().info(f"Launching WaraPS BT in {bt_launch_delay - (now_time - start_time):.2f} seconds...")

    node.create_timer(1.0/wara_ps_task_handler.wara_ps_dict["pulse_rate"], wara_ps_lvl_2_comms)

    rclpy.spin(node)