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
from .i_bb_updater import IBBUpdater
from .bb_keys import BBKeys
from ..mission.mission_plan import MissionPlanStates, MissionPlan
from ..mission.i_bb_mission_updater import IBBMissionUpdater
from ..mission.i_action_client import IActionClient

from ..waraps.waraps_task_handler import WaraPSTaskHandler, HasWaraPSTaskHandler
from ..waraps.waraps_vehicle import WaraPSVehicle


from .conditions import C_CheckMissionPlanState,\
                        C_CheckSensorBool,\
                        C_NotAborted,\
                        C_SensorOperatorBlackboard,\
                        C_MissionTimeoutOK,\
                        C_TaskIs,\
                        C_TaskStatus

from .actions import A_Abort,\
                     A_Heartbeat,\
                     A_UpdateMissionPlan,\
                     A_ProcessBTCommand,\
                     A_ActionClient,\
                     A_WaitForData,\
                    A_JustChillFor,\
                    A_ClearTaskQueue,\
                    A_Chilling

class BT(HasVehicleContainer, HasClock, HasWaraPSTaskHandler):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer,
                 task_handler:WaraPSTaskHandler,
                 bb_updater: IBBUpdater,
                 mission_updater: IBBMissionUpdater,
                 goto_wp_action: IActionClient,
                 now_seconds_func: typing.Callable
                 ):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._task_handler = task_handler
        self._bt = None
        self._bb_updater = bb_updater
        self._mission_updater = mission_updater
        self._goto_wp_action = goto_wp_action
        self._bb = Blackboard()
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
        
    def _run_tree(self):
        finalize_mission = Sequence("S_Finalize_Mission", memory=False, children=[
            C_CheckMissionPlanState(MissionPlanStates.COMPLETED),
            A_UpdateMissionPlan(MissionPlan.complete)
        ])

        follow_wp_plan = Sequence("S_Follow_WP_Plan", memory=False, children=[
            C_CheckMissionPlanState(MissionPlanStates.RUNNING),
            A_ActionClient(client=self._goto_wp_action),
            A_UpdateMissionPlan(MissionPlan.complete_current_wp)
        ])

        mission = Fallback("F_Mission", memory=False, children=[
            # Other types of plans go here
            follow_wp_plan
        ])

        run = Fallback("F_Run", memory=False, children=[
            C_CheckMissionPlanState(MissionPlanStates.STOPPED),
            finalize_mission,
            mission
        ])
        return run
            
    def _task_handler_tree(self):
        """
        Fallback root node, connecting together sequences of {is the current action a certain kind of action? If so, run the corresponding action server}
        """

        task_handler = Fallback("F_Task_Handler", memory=False, children=[
            # is the current task a move to task? If so, do it
            Sequence("S_MoveTo", memory=False, children=[
                C_TaskIs(self._task_handler, "move-to"),
                A_JustChillFor(self, self._task_handler, duration=20),
                A_ClearTaskQueue(self._task_handler),
            ]), 
            #TODO: implement more tasks types
            # is the current task a move path task? If so, do it

            # last type: just do nothing
            A_Chilling(self),
            # succeed by default
            # Success(),
        ])

        return task_handler

    def setup(self) -> bool:

        children = [
            A_Heartbeat(self),
            # A_ProcessBTCommand(self._mission_updater),
            # self._liveliness_tree(),
            # self._safety_tree(),
            # add the mission tree
            self._task_handler_tree(),
            # self._run_tree()
        ]

        # clean out Nones   
        children = [c for c in children if c is not None]

        # make the sequence tree
        root = Sequence("S_Root", memory=False, children=children)

        self._bt = pt.trees.BehaviourTree(root)
        self._bb_updater.update_bb()
        return self._bt.setup()



    def tick(self):
        self._bb_updater.update_bb()
        self._mission_updater.tick()
        self._bt.tick()
        self._bb.set(BBKeys.TREE_TIP, self._bt.tip())


def smarc_bt():
    from .ros_bb_updater import ROSBBUpdater
    from ..vehicles.sam_auv import SAMAuv
    from ..vehicles.quadrotor import Quadrotor
    from ..waraps.waraps_vehicle import WaraPSVehicle
    from ..mission.ros_mission_updater import ROSMissionUpdater
    from ..mission.ros_action_goto_waypoint import ROSGotoWaypoint
    import rclpy, sys
    import uuid

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("smarc_bt")

    def ros_seconds() -> int:
        nonlocal node
        secs, _ = node.get_clock().now().seconds_nanoseconds()
        return int(secs)
    
    def ros_seconds_float() -> float:
        nonlocal node
        secs, nsecs = node.get_clock().now().seconds_nanoseconds()
        return float(secs) + float(nsecs) * 1e-9

    
    # agent = SAMAuv(node)
    agent = Quadrotor(node)

    sam_bbu = ROSBBUpdater(node, initialize_bb=True)
    ros_mission_updater = ROSMissionUpdater(node)
    ros_goto_wp = ROSGotoWaypoint(node)
    # go_to_geopoint = ROSGotoGeopoint(node)

    action_client = ros_goto_wp
    # action_client = go_to_geopoint

    agent_waraps_dict = {
            "agent-type": "subsurface",
            "agent-uuid": str(uuid.uuid4()),
            "levels": ["sensor", "direct_execution"],
            "name": node.get_parameter("robot_name").value,
            "pulse_rate": 1,
        }        
    
    wara_ps_vehicle = WaraPSVehicle(node, agent.vehicle_state, agent_waraps_dict)
    wara_ps_task_handler = WaraPSTaskHandler(node, agent_waraps_dict)
    bt = BT(vehicle_container = agent,
            task_handler    = wara_ps_task_handler,
            bb_updater        = sam_bbu,
            mission_updater   = ros_mission_updater,
            goto_wp_action    = action_client,
            now_seconds_func  = ros_seconds_float)
    bt.setup()


    bt_str = ""
    def print_bt():
        nonlocal bt, bt_str, node, ros_goto_wp, ros_mission_updater, agent
        new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
        if new_str != bt_str:
            s = f"\nBT::\n{new_str}\n"
            s += f"GOTOWP Client::\n{ros_goto_wp.feedback_message}\n\n"
            s += f"Vehicle::\nAborted:{agent.vehicle_state.aborted}\nHealthy:{agent.vehicle_state.vehicle_healthy}\n"
            node.get_logger().info(s)
            bt_str = new_str


    def update():
        nonlocal bt
        bt.tick()

    node.create_timer(0.1, update)
    node.create_timer(0.5, print_bt)


    def wara_ps_level_1_comms():
        nonlocal wara_ps_vehicle
        # get the current time
        now_time = ros_seconds_float()
        # heartbeat
        wara_ps_vehicle.wara_ps_heartbeat(now_time)
        # sensor info
        wara_ps_vehicle.wara_ps_lvl1(now_time)

    node.create_timer(1.0/wara_ps_vehicle.wara_ps_dict["pulse_rate"], wara_ps_level_1_comms)

    def wara_ps_lvl_2_comms():
        nonlocal wara_ps_task_handler

        # get the current time
        now_time = ros_seconds_float()
        # heartbeat
        wara_ps_task_handler.lvl_2_heartbeat(now_time)

    node.create_timer(1.0/wara_ps_task_handler.wara_ps_dict["pulse_rate"], wara_ps_lvl_2_comms)

    
    rclpy.spin(node)

def test_bt_setup():
    from ..vehicles.vehicle import MockVehicleStateContainer, VehicleState, UnderwaterVehicleState



    v = MockVehicleStateContainer(VehicleState)

    bt = BT(v)
    bt.setup()

    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    v.vehicle_state.update_sensor(SensorNames.POSITION, [2,3,4], 0)
    v.vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, [1,2,3], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_POSITION, [1,2], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.BATTERY, [1,2], 0)
    v.vehicle_state.update_sensor(SensorNames.DEPTH, [1], 0)

    print('='*10)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))



def test_bt_conditions():
    from ..vehicles.vehicle import MockVehicleStateContainer, UnderwaterVehicleState
    bb = Blackboard()
    bb.set(BBKeys.MIN_ALTITUDE, 20)
    bb.set(BBKeys.MAX_DEPTH, 20)

    v = MockVehicleStateContainer(UnderwaterVehicleState)

    bt = BT(v)
    bt.setup()

    print("No update tick")
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    v.vehicle_state.update_sensor(SensorNames.POSITION, [2,3,4], 0)
    v.vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, [1,2,3], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_POSITION, [1,2], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.BATTERY, [1,2], 0)
    v.vehicle_state.update_sensor(SensorNames.ALTITUDE, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.DEPTH, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.LEAK, [False], 0)
    v.vehicle_state.update_sensor(SensorNames.VBS, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.LCG, [10], 0)
    v.vehicle_state.update_sensor(SensorNames.THRUSTERS, [1,2], 0)

    print('='*10)

    print("Single update tick")
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    print("="*10)

    print("Leak = True")
    v.vehicle_state.update_sensor(SensorNames.LEAK, [True], 1)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    print("="*10)

    print("ALT = 100")
    v.vehicle_state.update_sensor(SensorNames.LEAK, [False], 2)
    v.vehicle_state.update_sensor(SensorNames.ALTITUDE, [100], 2)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))
    print("ALT = 10")
    v.vehicle_state.update_sensor(SensorNames.ALTITUDE, [10], 2)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))