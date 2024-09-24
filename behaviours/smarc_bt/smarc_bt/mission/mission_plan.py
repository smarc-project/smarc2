#!/usr/bin/python3

import enum, time

from .waypoint import IWaypoint

class MissionPlanStates(enum.Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    EMERGENCY = "EMERGENCY"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"

    def __str__(self):
        return self.name





class MissionPlan():
    def __init__(self,
                 plan_id: str,
                 hash: str,
                 timeout: int,
                 waypoints: list[IWaypoint]) -> None:
        """
        A mission plan object that keeps track of mission state
        and waypoints. Use with an Updater object to create and manage
        it depending on how you interact with mission plans.
        """
        self._state = MissionPlanStates.RECEIVED
        self._plan_id = plan_id
        self._hash = hash
        self._timeout = timeout
        self._current_wp_index = -1
        self._waypoints = waypoints
        self._start_time_seconds = None


    def _log(self, s):
        print(f"[Mission {self._plan_id}]\t{s}")


    def _change_state(self, new_state: MissionPlanStates) -> bool:
        if self._state == MissionPlanStates.EMERGENCY:
            self._log("Not changing state away from EMERGENCY")
            return False
        
        if new_state == self._state: return True

        self._log(f"Mission state change: {self._state} -> {new_state}")
        self._state = new_state
        return True

    def __str__(self) -> str:
        s = f"[Mission {self._plan_id}]\n"
        for wp in self._waypoints:
            s += f"\t{wp}"
        return s
    
    def _get_time(self):
        return int(time.time())

    def _start_timeout(self):
        self._start_time_seconds = self._get_time()

    def _stop_timeout(self):
        self._start_time_seconds = None

    @property
    def seconds_to_timeout(self) -> int:
        if self._start_time_seconds is None: return 999999
        elapsed = self._get_time() - self._start_time_seconds
        return self._timeout - elapsed

    @property
    def timeout_reached(self) -> bool:
        # never started
        if self._start_time_seconds is None: return False

        if self.seconds_to_timeout <= 0:
            return True
        return False
    

    def start(self) -> bool:
        self._current_wp_index = 0
        self._start_timeout()
        return self._change_state(MissionPlanStates.RUNNING)

    def pause(self) -> bool:
        return self._change_state(MissionPlanStates.PAUSED)

    def resume(self) -> bool:
        return self._change_state(MissionPlanStates.RUNNING)
    
    def stop(self) -> bool:
        self._current_wp_index = -1
        self._stop_timeout()
        return self._change_state(MissionPlanStates.STOPPED)
    
    def complete(self) -> bool:
        self._current_wp_index = len(self._waypoints)
        self._stop_timeout()
        return self._change_state(MissionPlanStates.COMPLETED)
    
    def emergency(self) -> bool:
        self._current_wp_index = -1
        self._log("EMERGENCY TRIGGERED")
        self._stop_timeout()
        return self._change_state(MissionPlanStates.EMERGENCY)

    def complete_current_wp(self):
        if self._state == MissionPlanStates.RUNNING:
            self._current_wp_index += 1

        if self._current_wp_index >= len(self._waypoints):
            self.complete()


    @property
    def current_wp(self):
        if self._state != MissionPlanStates.RUNNING: return None
        return self._waypoints[self._current_wp_index] 
    
    @property
    def state(self):
        return self._state
    
    @property
    def planar_wps(self):
        wps = [(wp.position[0], wp.position[1], wp.arrival_heading) for wp in self._waypoints]
        return wps
    