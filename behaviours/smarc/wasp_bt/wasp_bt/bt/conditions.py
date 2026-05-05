#!/usr/bin/python3

import enum
from typing import Callable

from py_trees.common import Status
from py_trees.blackboard import Blackboard
from py_trees.behaviour import Behaviour

from .i_has_vehicle_container import HasVehicleContainer
from .i_has_clock import HasClock
from .common import VehicleBehaviour, bool_to_status
from ..vehicles.sensor import SensorNames       

from ..waraps.waraps_task_handler import HasWaraPSTaskHandler, WaraPSTaskHandler, WaraPSTaskStates


class C_CheckSensorBool(VehicleBehaviour):
    def __init__(self,
                 bt: HasVehicleContainer,
                 sensor_name: str,
                 sensor_key = 0):
        """
        Returns S if vehicle[sensor_name][sensor_key] == True, F otherwise
        """
        name = name = f"{self.__class__.__name__}({sensor_name}[{sensor_key}])"
        self._sensor_name = sensor_name
        self._sensor_key = sensor_key
        super().__init__(bt, name)

    def update(self) -> Status:
        sensor = self._bt.vehicle_container.vehicle_state[self._sensor_name]
        return bool_to_status(sensor[self._sensor_key])
    



class C_SensorOperatorBlackboard(VehicleBehaviour):
    def __init__(self,
                 bt: HasVehicleContainer,
                 sensor_name: str,
                 operator: Callable,
                 bb_key: enum.Enum,
                 sensor_key = 0):
        """
        Returns S if operator(vehicle[sensor_name][sensor_key], bb[bb_key]) == True
        """
        name = f"C_{sensor_name}[{sensor_key}] {operator.__name__} {bb_key}"
        self._sensor_name = sensor_name
        self._sensor_key = sensor_key
        self._bb_key = bb_key
        self._operator = operator
        super().__init__(bt, name)

    def update(self) -> Status:
        sensor = self._bt.vehicle_container.vehicle_state[self._sensor_name]
        value = sensor[self._sensor_key]
        bb = Blackboard()
        
        if not bb.exists(self._bb_key):
            self.feedback_message = f"Key {self._bb_key} not in BB!"  
            return Status.FAILURE
        
        bb_value = bb.get(self._bb_key)
        bb_value_str = "None"
        if bb_value is not None:
            bb_value_str = f"{bb_value:.2f}"
            
        value_str = "None"
        if value is not None:
            value_str = f"{value:.2f}"

        self.feedback_message = f"{self._operator.__name__}({value_str}, {bb_value_str})"

        if value is None or bb_value is None:
            return Status.SUCCESS

        self.feedback_message = f"{self._operator.__name__}({value_str}, {bb_value_str})"
        return bool_to_status(self._operator(value, bb_value))
        
        
class C_NotAborted(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        if self._bt.vehicle_container.vehicle_state.aborted:
            self.feedback_message = "!! ABORTED !!"
            return Status.FAILURE
        
        return Status.SUCCESS

    
class C_AbortedPreviousTask(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler):
        """
        Returns S if the previous task was aborted
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        name = f"{self.__class__.__name__}"
        super().__init__(name)

    def update(self) -> Status:

        if self._wara_ps_task_handler.aborted_flag == True:
            self.feedback_message = "Previous task was aborted"
            self._wara_ps_task_handler.aborted_flag = False  # reset the flag
            return Status.SUCCESS
        else:
            self.feedback_message = "Previous task was not aborted"
            return Status.FAILURE
        
class C_NoEmergencyAbortSignalDetected(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler):
        """
        Returns S if the emergency abort signal is detected
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        name = f"{self.__class__.__name__}"
        super().__init__(name)

    def update(self) -> Status:
        if self._wara_ps_task_handler.emergency_flag == True:
            self.feedback_message = "Emergency abort signal detected"
            # don't flip the flag, we want to keep the vehicle right here.
            return Status.FAILURE
        else:
            self.feedback_message = "No emergency abort signal detected"
            return Status.SUCCESS
        
    def terminate(self, new_status: Status) -> None:
        """
        clean up the feedback message
        """
        self.feedback_message = ""
        super().terminate(new_status)

from smarc_msgs.msg import Topics

class C_HealthNodeAlive(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler, timeout: float = 10.0):
        """
        Returns S if the last healthy status is ok
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        name = f"{self.__class__.__name__}"
        super().__init__(name)
        self._timeout = timeout
        self.start_time = None

    def setup(self) -> None:
        self.start_time = self._wara_ps_task_handler.current_time()

    def update(self) -> Status:
        now_time = self._wara_ps_task_handler.current_time()

        if self._wara_ps_task_handler.health_last_time is None:
            # if started more than timeout seconds ago, return failure
            if now_time - self.start_time > self._timeout:
                self.feedback_message = f"Haven't heard from vehicle in {now_time - self.start_time:.2f} seconds. Aborting!"
                return Status.FAILURE
            else:
                self.feedback_message = "Haven't heard from vehicle yet, but within timeout."
                return Status.RUNNING

        if now_time - self._wara_ps_task_handler.health_last_time >  self._timeout:
            self.feedback_message = f"Last heard from vehicle was {now_time - self._wara_ps_task_handler.health_last_time:.2f} seconds ago. Aborting!"
            return Status.FAILURE
        else:
            self.feedback_message = "Comms are fine. Vehicle health is up to date."
            return Status.SUCCESS


class C_VehicleHealthStatus(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler, desired_status: Topics):
        """
        Returns S if the vehicle is healthy
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        self._desired_status = desired_status

        self.status_dict = {
            0: "READY",
            1: "WAITING",
            2: "ERROR"
        }
        
        desired_status_str = self.status_dict[desired_status]
        name = f"{self.__class__.__name__}({desired_status_str})"
        super().__init__(name)
        self._health_status = self._wara_ps_task_handler.health_status
        self.feedback_message = ""

    def update(self) -> Status:

        # update the health status from the task handler
        self._health_status = self._wara_ps_task_handler.health_status

        if self._health_status == self._desired_status:
            self.feedback_message = f"Vehicle health status is {self._health_status}"
            return Status.SUCCESS
        else:
            self.feedback_message = f"Vehicle health status is {self._health_status}. Unknown status"
            return Status.FAILURE

        
    def terminate(self, new_status: Status) -> None:
        """
        clean up the feedback message
        """
        self.feedback_message = ""
        super().terminate(new_status)

class C_TaskIs(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler, task_name: str):
        """
        Returns S if the current task is a move_to task
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        name = f"{self.__class__.__name__} {task_name}"
        super().__init__(name)
        self._task_name = task_name

    def update(self) -> Status:

        current_executing_tasks = self._wara_ps_task_handler.get_executing_tasks()


        # if no tasks are executing, return failure
        if len(current_executing_tasks) == 0:
            self.feedback_message = "No tasks executing"
            return Status.FAILURE
        # focus only on first task. #TODO: this needs to be changed later, when we want multiple tasks to happen simultaneously
        if current_executing_tasks[0]["task"]["name"] == self._task_name:
            self.feedback_message = f"Current task is {self._task_name}"
            return Status.SUCCESS
        else:
            self.feedback_message = f"Not a {self._task_name} task"
            return Status.FAILURE
    
class C_TaskStatus(Behaviour):
    def __init__(self, wara_ps_task_handler: WaraPSTaskHandler, expected_status: WaraPSTaskStates):
        """
        Returns S if the current task status is "running"
        """
        self._wara_ps_task_handler = wara_ps_task_handler
        name = f"{self.__class__.__name__} {expected_status}"
        super().__init__(name)
        self._expected_status = expected_status

    def update(self) -> Status:
        current_executing_tasks = self._wara_ps_task_handler.get_executing_tasks()

        # if no tasks are executing, return failure
        if len(current_executing_tasks) == 0:
            self.feedback_message = "No tasks executing"
            return Status.FAILURE
        # focus only on first task. #TODO: this needs to be changed later, when we want multiple tasks to happen simultaneously
        if current_executing_tasks[0]["status"] == self._expected_status:
            self.feedback_message = f"Current task status is {self._expected_status}"
            return Status.SUCCESS
        else:
            self.feedback_message = f"Current task status is {current_executing_tasks[0]['status']}"
            return Status.FAILURE
        
class C_MissionNotInError(Behaviour):
    """
    Checks if mission status is NOT in ERROR state.
    Returns FAILURE if mission is in ERROR, SUCCESS otherwise.
    This prevents tasks from executing after a mission error.
    """
    def __init__(self, task_handler: WaraPSTaskHandler):
        self._task_handler = task_handler
        name = f"{self.__class__.__name__}"
        super().__init__(name)
        self.feedback_message = ""

    def update(self) -> Status:
        mission_status = self._task_handler.mission_status
        if mission_status == WaraPSTaskStates.ERROR.value:
            self.feedback_message = "Mission in ERROR state, blocking task execution"
            return Status.FAILURE
        else:
            return Status.SUCCESS

class C_HasHeardFromVehicleHealth(Behaviour):
    """
    An action that keeps "running" until a parameter on the task handler is true.
    """
    def __init__(self, task_handler: WaraPSTaskHandler):
        
        """
        Returns S if the vehicle health has been received
        """
        self._task_handler = task_handler
        name = f"{self.__class__.__name__}"
        super().__init__(name)
        self.feedback_message = ""

    def update(self) -> Status:
        if self._task_handler.health_last_time is not None:
            self.feedback_message = "Vehicle health received."
            return Status.SUCCESS
        else:
            self.feedback_message = "Waiting for vehicle health to be published..."
            return Status.RUNNING