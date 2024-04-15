#!/usr/bin/python3

import enum

from py_trees.behaviour import Behaviour
# https://py-trees.readthedocs.io/en/devel/behaviours.html
from py_trees.common import Status
from py_trees.blackboard import Blackboard

from .bb_keys import BBKeys
from .trunk import HasVehicleContainer
from .i_has_vehicle_container import HasVehicleContainer


def bool_to_status(b: bool) -> enum.Enum:
    if b: return Status.SUCCESS
    else: return Status.FAILURE


class VehicleBehavour(Behaviour):
    """
    A wrapper around the py_trees Behaviour that accepts
    an _optional_ name and probably a behavior tree wrapper that
    contains a vehicle container object inside
    """
    def __init__(self, bt: HasVehicleContainer, name: str = None):
        if name is None: 
            name = self.__class__.__name__
        super().__init__(name)
        self._bt = bt



class C_VehicleSensorsWorking(VehicleBehavour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        state = self._bt.vehicle_container.vehicle_state
        return bool_to_status(state.all_sensors_working)
        

        
