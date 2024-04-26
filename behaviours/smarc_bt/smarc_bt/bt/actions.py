#!/usr/bin/python3

from typing import Callable

from py_trees.common import Status
from py_trees.blackboard import Blackboard
from py_trees.behaviour import Behaviour

from .i_has_vehicle_container import HasVehicleContainer

from .common import VehicleBehaviour, MissionPlanBehaviour, bool_to_status

from .bb_keys import BBKeys
from ..mission.i_bb_mission_updater import IBBMissionUpdater


class A_Abort(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        self._bt.vehicle_container.abort()
        self.feedback_message = "!! ABORTED !!"
        return Status.FAILURE

    

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
            
        
class A_ProcessBTCommand(Behaviour):
    def __init__(self, mission_updater:IBBMissionUpdater ):
        super().__init__(self.__class__.__name__)

        self._accepted_commands = set()
        self._accepted_commands.add("plan_dubins")
        self._mission_updater = mission_updater

        self._bb = Blackboard()

    def update(self) -> Status:
        try:
            cmd_q = self._bb.get(BBKeys.BT_CMD_QUEUE)
        except:
            self.feedback_message = "No command to process (there is no queue)"
            return Status.SUCCESS
        
        if cmd_q is None or len(cmd_q) == 0:
            self.feedback_message = "No command to process (queue empty)"
            return Status.SUCCESS
        
        cmd, arg = cmd_q[0]
        cmd_q = cmd_q[1:]
        self._bb.set(BBKeys.BT_CMD_QUEUE, cmd_q)

        if not cmd in self._accepted_commands:
            self.feedback_message = f"Command [{cmd}] not accepted. Ignored."
            return Status.SUCCESS
        
        if cmd == "plan_dubins":
            # the arg should be a float coming from the interacter, if any
            if(arg): arg = float(arg)
            self._mission_updater.plan_dubins(turning_radius=arg)
            self.feedback_message = "Plan dubins called"
            return Status.SUCCESS


        self.feedback_message = "Invalid state of action?"
        return Status.FAILURE

