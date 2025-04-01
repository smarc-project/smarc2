#!/usr/bin/python3

from typing import Any, Callable

from py_trees.common import Status
from py_trees.blackboard import Blackboard
from py_trees.behaviour import Behaviour

from .i_has_vehicle_container import HasVehicleContainer
from .i_has_clock import HasClock
from .common import VehicleBehaviour, MissionPlanBehaviour, bool_to_status
from .bb_keys import BBKeys
from ..mission.i_bb_mission_updater import IBBMissionUpdater
from ..mission.i_action_client import IActionClient, ActionClientState

# import waraps_hb topic from smarc_topics
from smarc_msgs.msg import Topics as SmarcTopics

# import string
from std_msgs.msg import String
import json

class A_WarapsHeartbeat(VehicleBehaviour):
    def __init__(self,
                bt: HasClock):
        super().__init__(bt)

        # define ros publisher
        self.waraps_heartbeat_pub = bt.vehicle_container._node.create_publisher(String, SmarcTopics.WARA_PS_HEARTBEAT_TOPIC, 10)


        # compute levels
        level_str = self._bt.vehicle_container._node.get_parameter("agent_levels").value,
        
        # at this stage, it's a tuple object
        # so we need to get the first element of the tuple
        level_str = level_str[0]
        
        # string example: "level1,level2,level3"
        # convert to list
        # print(f"level_str: {level_str}")
        levels = level_str.split(",")
        # remove leading and trailing whitespace from each level
        levels = [level.strip() for level in levels]
        # remove empty strings
        levels = [level for level in levels if level != ""]
        # remove duplicates
        self.levels = list(set(levels))

        self.agent_type = self._bt.vehicle_container._node.get_parameter("agent_type").value
        self.agent_uuid = self._bt.vehicle_container._node.get_parameter("agent_uuid").value
        self.robot_name = self._bt.vehicle_container._node.get_parameter("robot_name").value
        self.agent_rate = self._bt.vehicle_container._node.get_parameter("agent_rate").value



    def update(self) -> Status:        
            

        heartbeat_data = {
            "agent-type": self.agent_type,
            "agent-uuid": self.agent_uuid,
            "levels": self.levels,
            # "name": sam.vehicle_state.,
            # use rosparam "robot_name"
            "name": self.robot_name, 
            "rate": self.agent_rate,
            "stamp": self._bt.now_seconds,
            # UTC time please
            # "stamp": node.get_clock().now().to_msg().sec + node.get_clock().now().to_msg().nanosec * 1e-9,
            "type": "HeartBeat"
        }

        # convert to string
        msg = String()
        msg.data = json.dumps(heartbeat_data)

        # publish
        self.waraps_heartbeat_pub.publish(msg)
        self.feedback_message = f"Published WARAPS heartbeat: {heartbeat_data}"
        return Status.SUCCESS




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

class A_Abort(VehicleBehaviour):
    def __init__(self, bt: HasVehicleContainer):
        super().__init__(bt)

    def update(self) -> Status:
        self._bt.vehicle_container.abort()
        self.feedback_message = "!! ABORTED !!"
        return Status.SUCCESS

    

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


class A_ActionClient(MissionPlanBehaviour):
    def __init__(self,
                 client: IActionClient):
        super().__init__(f"{self.__class__.__name__}({client.__class__.__name__})")
        self._client = client
        self._bb = Blackboard()

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

    def setup(self, timeout:int = 1) -> None:
        return self._client.setup(timeout)
        

    def terminate(self, new_status: Status) -> None:
        if new_status == Status.INVALID:
            # pre-empted by a higher priority branch, cancel the goal!
            self.feedback_message = "Preempted, cancelling goal"
            self._client.cancel_goal()
            return

        self.feedback_message = f"Terminate::{self._client.feedback_message}"

        if new_status == Status.SUCCESS:
            # action is finished proper. get ready for a next run.
            self._client.get_ready()

        if new_status == Status.FAILURE:
            # action did not finish proper.
            # should be handled by the rest of the tree
            return



    def update(self) -> Status:
        s = self._client.state

        # if it was cancelled, get the client ready for a new run for later
        if self._client.state == ActionClientState.CANCELLED:
            self._client.get_ready()    
            return Status.RUNNING

        # server is good to go
        if s == ActionClientState.READY:
            mplan = self._get_plan()
            if mplan is None:
                self.feedback_message = "No plan to get a wp from..."
                return Status.FAILURE
            
            self._client.send_goal(mplan.current_wp)
            return Status.RUNNING
        
        if s in self._running_states:
            self.feedback_message = self._client.feedback_message
            return Status.RUNNING

        if s in self._failure_states:
            return Status.FAILURE
        
        if s in self._success_states:
            return Status.SUCCESS
    

        self.feedback_message = f"Unexpected status:{s}?!"
        return Status.FAILURE

            
            
        


