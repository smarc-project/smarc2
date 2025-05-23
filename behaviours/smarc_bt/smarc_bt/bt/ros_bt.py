#!/usr/bin/python3

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


from .conditions import C_CheckMissionPlanState,\
                        C_CheckSensorBool,\
                        C_NotAborted,\
                        C_SensorOperatorBlackboard,\
                        C_MissionTimeoutOK

from .actions import A_Abort,\
                     A_Heartbeat,\
                     A_UpdateMissionPlan,\
                     A_ProcessBTCommand,\
                     A_ActionClient,\
                     A_WaitForData



class BT(HasVehicleContainer, HasClock):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer,
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
        

    def setup(self) -> bool:
        
        root = Sequence("S_Root", memory=False, children=[
            A_Heartbeat(self),
            A_ProcessBTCommand(self._mission_updater),
            self._liveliness_tree(),
            self._safety_tree(),
            self._run_tree()
        ])

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
    from ..mission.ros_mission_updater import ROSMissionUpdater
    from ..mission.ros_action_goto_waypoint import ROSGotoWaypoint
    import rclpy, sys

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("smarc_bt")

    def ros_seconds() -> int:
        nonlocal node
        secs, _ = node.get_clock().now().seconds_nanoseconds()
        return int(secs)

    
    sam = SAMAuv(node)
    sam_bbu = ROSBBUpdater(node, initialize_bb=True)
    ros_mission_updater = ROSMissionUpdater(node)
    ros_goto_wp = ROSGotoWaypoint(node)
    bt = BT(vehicle_container = sam,
            bb_updater        = sam_bbu,
            mission_updater   = ros_mission_updater,
            goto_wp_action    = ros_goto_wp,
            now_seconds_func  = ros_seconds)
    bt.setup()


    bt_str = ""
    def print_bt():
        nonlocal bt, bt_str, node, ros_goto_wp, ros_mission_updater, sam
        new_str = pt.display.ascii_tree(bt._bt.root, show_status=True)
        if new_str != bt_str:
            s = f"\nBT::\n{new_str}\n"
            s += f"GOTOWP Client::\n{ros_goto_wp.feedback_message}\n\n"
            s += f"Vehicle::\nAborted:{sam.vehicle_state.aborted}\nHealthy:{sam.vehicle_state.vehicle_healthy}\n"
            node.get_logger().info(s)
            bt_str = new_str


    def update():
        nonlocal bt
        bt.tick()

    node.create_timer(0.2, update)
    node.create_timer(0.5, print_bt)
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