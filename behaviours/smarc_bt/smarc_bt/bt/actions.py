#!/usr/bin/python3

from typing import Callable

from py_trees.common import Status
from py_trees.blackboard import Blackboard
from py_trees.behaviour import Behaviour

from .i_has_vehicle_container import HasVehicleContainer
from .common import VehicleBehaviour, MissionPlanBehaviour, bool_to_status

from .bb_keys import BBKeys
from ..mission.mission_plan import MissionPlanStates


class A_Abort(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        return bool_to_status(self._bt.vehicle_container.abort())

    

class A_Heartbeat(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        return bool_to_status(self._bt.vehicle_container.heartbeat())
    

class A_UpdateMissionPlan(MissionPlanBehaviour):
    def __init__(self, state_change_func: Callable):
        self._state_change_func = state_change_func
        name = name = f"{self.__class__.__name__}({self._state_change_func.__name__})"
        super().__init__(name)

    def update(self) -> Status:
        self.feedback_message = ""
        plan = self._get_plan()
        if plan is None: return Status.FAILURE

        return bool_to_status(self._state_change_func(plan))
            
        