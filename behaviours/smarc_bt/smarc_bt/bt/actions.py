#!/usr/bin/python3

from py_trees.common import Status
from py_trees.blackboard import Blackboard

from .i_has_vehicle_container import HasVehicleContainer
from .common import VehicleBehavour, bool_to_status



class A_Abort(VehicleBehavour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        return bool_to_status(self._bt.vehicle_container.abort())

    

class A_Heartbeat(VehicleBehavour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        return bool_to_status(self._bt.vehicle_container.heartbeat())