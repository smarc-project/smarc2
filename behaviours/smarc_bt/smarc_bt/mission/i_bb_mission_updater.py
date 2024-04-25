#!/usr/bin/python3

class IBBMissionUpdater():
    """
    An interactive object that manages the mission plan in a blackboard
    """
    def _new_mission_cb(self): pass
    def _mission_control_cb(self): pass
    def _log(self, s:str): pass

    def tick(self): pass
    def plan_dubins(self, turning_radius:float = None, step_size:float = None): pass