#!/usr/bin/python3

from typing import Any, Callable

from py_trees.common import Status
from py_trees.behaviour import Behaviour

from .i_has_vehicle_container import HasVehicleContainer
from .i_has_clock import HasClock
from .common import VehicleBehaviour, MissionPlanBehaviour, bool_to_status
from smarc_action_base.smarc_action_base import ActionClientState

import json

from wasp_bt.waraps.waraps_task_handler import WaraPSTaskHandler, HasWaraPSTaskHandler, WaraPSTaskStates

from smarc_mission_msgs.action import BaseAction
from smarc_action_base.smarc_action_base import SMARCActionClient
from wasp_bt.bt.client import BTActionClient

class A_WaitForData(VehicleBehaviour):
    def __init__(self,
                 bt: HasClock,
                 sensor_name: str):
        name = name = f"{self.__class__.__name__}({sensor_name})"
        super().__init__(bt, name)
        self._bb = Blackboard()
        self._sensor_name = sensor_name
        self._first_tick_seconds = None


    @property
    def _now(self):
        return self._bt.now_seconds

    def update(self) -> Status:
        if self._first_tick_seconds is None:
            self._first_tick_seconds = self._now

        sensor = self._bt.vehicle_container.vehicle_state[self._sensor_name]
        
        # has this sensor every gotten anything?
        if sensor.last_update_seconds is None:
            # nope
            # are we letting it chill for a little?
            initial_silence_seconds = self._bb.get(BBKeys.SENSOR_INITIAL_GRACE_PERIOD)
            dt_since_first = self._now - self._first_tick_seconds
            if dt_since_first < initial_silence_seconds:
                # yeah, chill for a bit
                self.feedback_message = f"{dt_since_first:.0f}/{initial_silence_seconds} of initial silence."
                return Status.RUNNING
            else:
                # no, its been too long
                self.feedback_message = f"Sensor dead?"
                return Status.FAILURE

        # it has gotten data at least once
        # but how far behind is it?
        allowed_silence_seconds = self._bb.get(BBKeys.SENSOR_SILENCE_PERIOD)
        
        dt = self._now - sensor.last_update_seconds 
        if dt > allowed_silence_seconds:
            # too far behind
            self.feedback_message = f"{dt} > {allowed_silence_seconds}!"
            return Status.FAILURE
        
        # not too far behind. we good.
        self.feedback_message = f"{dt:.1f}s since last update"
        return Status.SUCCESS
    
    def terminate(self, new_status: Status) -> None:
        self.feedback_message = None

# class A_Abort(VehicleBehaviour):
#     def __init__(self, bt: HasVehicleContainer):
#         super().__init__(bt)

#     def update(self) -> Status:
#         self._bt.vehicle_container.abort()
#         self.feedback_message = "!! ABORTED !!"
#         return Status.SUCCESS


class A_Chilling(VehicleBehaviour):
    """
    An Action to just do nothing (while waiting for task input)
    """

    def __init__(self, bt: HasClock):
        name = f"{self.__class__.__name__}"
        super().__init__(bt, name)



    def update(self) -> Status:
        self.feedback_message = f"Just chillin'... Got something for me to do?"
        return Status.RUNNING
    
    def terminate(self, new_status: Status) -> None:
        if new_status == Status.INVALID:
            # action is finished proper. 
            self.feedback_message = None
        return

    
    
class A_JustChillFor(VehicleBehaviour):
    def __init__(self, bt: HasClock, task_handler: WaraPSTaskHandler, duration: float):
        name = f"{self.__class__.__name__}({duration})Seconds"
        super().__init__(bt, name)

        self._start_time = None
        self._duration = duration
        self._task_handler = task_handler
        self._elapsed_time = 0

    def initialise(self):
        self._start_time = None
        self.feedback_message = None
        self.paused = False

    def setup(self, timeout: int = 1) -> None:
        self._start_time = None
        self._duration = self._duration
        self._task_handler.set_current_task_status(WaraPSTaskStates.STARTED.value)
        self.feedback_message = "Task started. Waiting for task to finish..."
        return True

    def update(self) -> Status:
        if self._start_time is None:
            self._start_time = self._bt.now_seconds

        # handle status signals
        latest_status = self._task_handler.get_current_task_status()
        
        if latest_status == WaraPSTaskStates.STARTED.value or latest_status == WaraPSTaskStates.RESUMED.value:
            
            self._task_handler.set_current_task_status(WaraPSTaskStates.RUNNING.value)
            self._start_time = self._bt.now_seconds

            if self.paused:
                self.paused = False
            
        if latest_status == WaraPSTaskStates.PAUSED.value:
            self.feedback_message = "Task paused. Waiting for resume..."
            # set duration
            if not self.paused:
                self._elapsed_time += self._bt.now_seconds - self._start_time
                self._duration = self._duration - self._elapsed_time
                self.paused = True
            return Status.RUNNING
        
        elif latest_status == WaraPSTaskStates.ABORTED.value or latest_status == WaraPSTaskStates.ENOUGH.value:
            self.feedback_message = "Task cancelled. Removing from Task Queue..."
            # remove task from queue
            self._task_handler.clear_task_queue()
            return Status.SUCCESS
        
        if latest_status == WaraPSTaskStates.RUNNING.value:
            dt = self._bt.now_seconds - self._start_time
            if dt > self._duration:
                self.feedback_message = f"I've been chillin for {self._elapsed_time + dt:.1f}s. Chillin' is OVER. Gimme some work!"
                return Status.SUCCESS

            self.feedback_message = f"I've been chillin for {self._elapsed_time + dt:.1f}s. Chillin' will continue for {self._duration-dt:.1f}s"
            return Status.RUNNING
    
    def terminate(self, new_status: Status) -> None:
        if new_status == Status.SUCCESS:
            # action is finished proper. 
            self.feedback_message = "Task finished!"
            self._task_handler.set_current_task_status(WaraPSTaskStates.FINISHED.value)
            self._task_handler.clear_task_queue()

            # reset everything
            self._start_time = None
            self._elapsed_time = 0
            self._duration = self._duration

        return
    
class A_ClearTaskQueue(VehicleBehaviour):
    def __init__(self, task_handler: WaraPSTaskHandler):
        super().__init__(self.__class__.__name__)
        self._task_handler = task_handler

    def update(self) -> Status:

        
        self._task_handler.clear_task_queue()
        self.feedback_message = "Cleared task queue"
        return Status.RUNNING
    
class A_ClearCurrentTask(VehicleBehaviour):
    def __init__(self, task_handler: WaraPSTaskHandler):
        super().__init__(self.__class__.__name__)
        self._task_handler = task_handler

    def update(self) -> Status:
        self._task_handler.clear_current_task()
        self.feedback_message = "Cleared current task"
        return Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = None

class A_TaskAbortedFlagReset(VehicleBehaviour):
    def __init__(self, task_handler: WaraPSTaskHandler):
        super().__init__(self.__class__.__name__)
        self._task_handler = task_handler

    def update(self) -> Status:
        self._task_handler.aborted_flag = False
        self.feedback_message = "Aborted flag reset"
        return Status.SUCCESS

    def terminate(self, new_status: Status) -> None:
        if new_status == Status.SUCCESS:
            # action is finished proper. 
            self.feedback_message = None
        return

class A_Abort(VehicleBehaviour):
    def __init__(self, task_handler: WaraPSTaskHandler):
        super().__init__(self.__class__.__name__)
        self.task_handler = task_handler

    def update(self) -> Status:
        # if self.task_handler.aborted_flag == False:
        self.task_handler.abort()
    
        self.feedback_message = "!! ABORTED !!"
        return Status.SUCCESS
    
class A_Heartbeat(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        return bool_to_status(self._bt.vehicle_container.heartbeat())
    

            
class A_ActionClient(Behaviour):
    def __init__(self,
                 client: BTActionClient,
                 bt: HasClock,
                 task_handler: WaraPSTaskHandler):
        super().__init__(f"A_ActionClient({client.get_action_name()})")
        
        self._bt = bt
        self._client = client
        self._task_handler = task_handler

        self._cancel_response = None
        self._feedback_message = None
        self._goal_response = None
        self._result = None

        self._failure_states = [
            ActionClientState.DISCONNECTED,
            ActionClientState.ERROR,
            ActionClientState.REJECTED,
            ActionClientState.CANCELLED
        ]

        self._success_states = [
            ActionClientState.DONE
        ]

        self._running_states = [
            ActionClientState.SENT,
            ActionClientState.ACCEPTED,
            ActionClientState.RUNNING,
            ActionClientState.CANCELLING
        ]

        self.last_feedback_time = None

        self._logger = self._client._node.get_logger()
            

    def setup(self) -> None:
        return self._client._setup(num_iters=5)
    
    def initialise(self) -> None: # this function is called when this Action is ticked for the first time
        # if previously running, get the client ready for a new run
        if self._client.state in self._running_states:
            self.feedback_message = "Clearing previous goal and getting ready for a new run..."
            self._client.cancel_goal(self._client.cancel_callback)


        self.feedback_message = None
        self._task_handler.set_current_task_status("started")
        self._task_handler.publish_feedback_to_current_task("Action client initialised. Waiting for task to start...")
        

    def terminate(self, new_status: Status) -> None:
        if new_status == Status.INVALID:
            # Only try to cancel if the goal is still active
            if self._client.state in self._running_states:
                self.feedback_message = "Preempted by higher priority in tree, cancelling goal"
                self._client.cancel_goal(self._client.cancel_callback)
            else:
                self.feedback_message = f"Preempted with Action Client state: {self._client.state}"
            
            # Publish feedback
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))

        elif new_status == Status.SUCCESS:
            # action is finished proper. get ready for a next run.
            self.feedback_message = "Action finished. Ready for next run."
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))

        if new_status == Status.FAILURE:
            # action did not finish proper.
            # should be handled by the rest of the tree
            self.feedback_message = f"Action failed. Action Client state: {self._client.state}"
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))

        # reset the client to ready state
        self._client.get_ready()

        return



    def update(self) -> Status:

        current_time = self._bt.now_seconds
        if self.last_feedback_time is None:
            self.last_feedback_time = current_time

        # log current and last feedback time
        # self._logger.debug(f"Current time: {current_time}, Last feedback time: {self.last_feedback_time}")

        s = self._client.state

        # if it was cancelled, get the client ready for a new run for later
        if s == ActionClientState.CANCELLED:
            # change state to ready
            self.feedback_message = "Action cancelled. Ready for next run."
            self._client.get_ready()    
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
            return Status.RUNNING

        if s == ActionClientState.READY:

            if self._task_handler.emergency_flag == True:
                # we're in an emergency, define custom message for the emergency action server
                self.feedback_message = "Emergency flag seen."
                mplan = {
                    "level": 1
                }

                msg_str = json.dumps(mplan)
                mission_msg = BaseAction.Goal()
                mission_msg.goal.data = msg_str
                self._client.send_goal(mission_msg)
                self._logger.info("Emergency action sent.")

                if current_time - self.last_feedback_time > 1.0:
                    self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
                    self.last_feedback_time = current_time
                
                return Status.RUNNING

            task_status = self._task_handler.get_current_task_status()
            if task_status == "started" or task_status == "resumed":
                self.feedback_message = f"Task {task_status}-ed. Waiting for task to finish..."
                self._task_handler.set_current_task_status("running")

                if current_time - self.last_feedback_time > 1.0:    
                    self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
                    self.last_feedback_time = current_time
                
            mplan = self._task_handler.get_current_task_params()
            
            if mplan is None:
                self.feedback_message = "No task to get a wp from..."

                if current_time - self.last_feedback_time > 1.0:
                    self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
                    self.last_feedback_time = current_time
                return Status.FAILURE

            
            #log the mission plan
            self._logger.info(f"Mission Plan: {mplan}")

            msg_str = json.dumps(mplan)

            # extract params, this is specific to the geopoint server made by Tim
            
            # param_dict = mplan["waypoint"]
            # msg_dict = {
            #     "geopoint": {
            #         "latitude": param_dict["latitude"],
            #         "longitude": param_dict["longitude"],
            #         "altitude": param_dict["altitude"]
            #     },
            # }
            # msg_str = json.dumps(msg_dict)


            mission_msg = BaseAction.Goal()
            mission_msg.goal.data = msg_str
            self._client.send_goal(mission_msg)

            # self._logger.info("yall I sent dat task")
            self.feedback_message = "Goal sent to action client."
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
            return Status.RUNNING
        
        if s in self._running_states:
            self.feedback_message = self._client.feedback_message
            if current_time - self.last_feedback_time > 1.0:
            # publish feedback every second
                self.last_feedback_time = current_time
                self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
            return Status.RUNNING

        if s in self._failure_states:
            self.feedback_message = f"Action client in failure state: {s}. Check logs for more info."
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))

            # remove the current task from the task handler
            self._task_handler.clear_current_task()

            return Status.FAILURE
        
        if s in self._success_states:
            self.feedback_message = "Action client succeeded."
            self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
            return Status.SUCCESS
    

        self.feedback_message = f"Unexpected status:{s}?!"
        self._task_handler.publish_feedback_to_current_task(str(self.feedback_message))
        return Status.FAILURE


