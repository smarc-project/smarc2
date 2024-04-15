#!/usr/bin/python3

import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.blackboard import Blackboard
from py_trees.decorators import Inverter

from ..vehicles.vehicle import IVehicleStateContainer
from ..vehicles.sensor import SensorNames
from .i_has_vehicle_container import HasVehicleContainer
from .bb_keys import BBKeys

from .conditions import *

import operator


class SMaRCBT(HasVehicleContainer):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._bt = None

    @property
    def vehicle_container(self) -> IVehicleStateContainer:
        return self._vehicle_container


    def setup(self) -> bool:
        root = Sequence("S_Root",
                        memory=False,
                        children=[
            C_VehicleSensorsWorking(self),
            Inverter("Not leaking", C_CheckBooleanState(self, SensorNames.LEAK)),
            C_BlackboardOperatorSensor(self, BBKeys.MIN_ALTITUDE, operator.lt, SensorNames.ALTITUDE)
        ])

        self._bt = pt.trees.BehaviourTree(root)
        return self._bt.setup()


    def tick(self):
        self._bt.tick()



def test_bt_setup():
    from ..vehicles.vehicle import MockVehicleStateContainer, VehicleState, UnderwaterVehicleState


    v = MockVehicleStateContainer(VehicleState)

    bt = SMaRCBT(v)
    bt.setup()

    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    v.vehicle_state.update_sensor(SensorNames.POSITION, [2,3,4], 0)
    v.vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, [1,2,3], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_POSITION, [1,2], 0)
    v.vehicle_state.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [1], 0)
    v.vehicle_state.update_sensor(SensorNames.BATTERY, [1,2], 0)

    print('='*10)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))



def test_bt_conditions():
    from ..vehicles.vehicle import MockVehicleStateContainer, UnderwaterVehicleState
    bb = Blackboard()
    bb.set(BBKeys.MIN_ALTITUDE, 20)

    v = MockVehicleStateContainer(UnderwaterVehicleState)

    bt = SMaRCBT(v)
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