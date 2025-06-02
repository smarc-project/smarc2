#!/usr/bin/python3

from py_trees.common import Status
import enum
from py_trees.behaviour import Behaviour
from py_trees.blackboard import Blackboard
from .i_has_vehicle_container import HasVehicleContainer    
from .bb_keys import BBKeys
from ..mission.mission_plan import MissionPlan


def bool_to_status(b: bool) -> enum.Enum:
    if b == True: return Status.SUCCESS
    else: return Status.FAILURE


class VehicleBehaviour(Behaviour):
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


class MissionPlanBehaviour(Behaviour):
    def _get_plan(self) -> MissionPlan:
        try:
            self._bb = Blackboard()
            plan = self._bb.get(BBKeys.MISSION_PLAN)
        except KeyError:
            self.feedback_message = "No mission key"
            return None
        if plan is None:
            self.feedback_message = "Mission==None"
            return None
        
        return plan
        
