#!/usr/bin/python3

import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.blackboard import Blackboard
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy

from ..vehicles.vehicle import IVehicleStateContainer
from ..vehicles.sensor import SensorNames
from .i_has_vehicle_container import HasVehicleContainer
from .i_bb_updater import IBBUpdater
from .bb_keys import BBKeys
from ..mission_handling.mission_plan import MissionPlanStates, MissionPlan

from .conditions import C_CheckMissionPlanState,\
                        C_CheckVehicleSensorState,\
                        C_NotAborted,\
                        C_SensorOperatorBlackboard,\
                        C_VehicleSensorsWorking

from .actions import A_Abort,\
                     A_Heartbeat,\
                     A_UpdateMissionPlan

import operator


class ROSBT(HasVehicleContainer):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer,
                 bb_updater: IBBUpdater = None):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._bt = None
        self._bb_updater = bb_updater

    @property
    def vehicle_container(self) -> IVehicleStateContainer:
        return self._vehicle_container


    def _safety_tree(self):
        safety_checks = Parallel("P_Safety_Checks", policy=ParallelPolicy.SuccessOnAll(synchronise=False) , children=[
            C_NotAborted(self),
            C_SensorOperatorBlackboard(self, SensorNames.ALTITUDE, operator.gt, BBKeys.MIN_ALTITUDE),
            C_SensorOperatorBlackboard(self, SensorNames.DEPTH, operator.lt, BBKeys.MAX_DEPTH),
            Inverter("Not leaking", C_CheckVehicleSensorState(self, SensorNames.LEAK)),
            pt.behaviours.Success(name="TODO mission timeout not reached")
            # https://github.com/smarc-project/smarc_missions/blob/b1bf53cea3855c28f9a2c004ef2d250f02885afe/smarc_bt/src/bt_conditions.py#L19
        ])

        safety_tree = Fallback("F_Safety", memory=False, children=[
            safety_checks,
            # modify mission?
            A_Abort(self)
        ])

        return safety_tree
    
    def _run_tree(self):
    
        finalize_mission = Sequence("S_FinalizeMission", memory=False, children=[
            C_CheckMissionPlanState(MissionPlanStates.COMPLETED),
            A_UpdateMissionPlan(MissionPlan.complete)
        ])

        follow_wp_plan = Sequence("S_Follow_WP_Plan", memory=False, children=[
            C_CheckMissionPlanState(MissionPlanStates.RUNNING),
            pt.behaviours.Running(name="TODO Goto action"),
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
            C_VehicleSensorsWorking(self),
            A_Heartbeat(self),
            self._safety_tree(),
            self._run_tree()
        ])

        self._bt = pt.trees.BehaviourTree(root)
        self._update_bb()
        return self._bt.setup()


    def _update_bb(self):
        if self._bb_updater:
            self._bb_updater.update_bb()


    def tick(self):
        self._update_bb()
        self._bt.tick()


def test_sam_bt():
    from ..vehicles.sam_auv import SAMAuv
    from .sam_bb_updater import SAMBBUpdater
    import rclpy, sys

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_sam_bt")

    sam = SAMAuv(node)
    sam_bbu = SAMBBUpdater(node, initialize_bb=True)
    bb = Blackboard()
    bb.set(BBKeys.VEHICLE_STATE_CONTAINER, sam)
    bt = ROSBT(sam, sam_bbu)
    bt.setup()

    def update():
        nonlocal bt
        print(pt.display.ascii_tree(bt._bt.root, show_status=True))
        bt.tick()

    node.create_timer(0.2, update)
    rclpy.spin(node)




def test_bt_setup():
    from ..vehicles.vehicle import MockVehicleStateContainer, VehicleState, UnderwaterVehicleState



    v = MockVehicleStateContainer(VehicleState)

    bt = ROSBT(v)
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

    bt = ROSBT(v)
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