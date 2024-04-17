#!/usr/bin/python3

from py_trees.common import Status
import enum
from py_trees.behaviour import Behaviour
from .i_has_vehicle_container import HasVehicleContainer    


def bool_to_status(b: bool) -> enum.Enum:
    if b == True: return Status.SUCCESS
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