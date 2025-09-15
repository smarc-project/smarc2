#!/usr/bin/python3

import enum

class IDivePub:
    """
    An interface for some kind of "view" that can do _something_ with a given RPM value.
    """
    def set_rpm(self, rpm: int) -> None:
        print("UNIMPLEMENTED")

    def set_thrust_vector(self, horizontal_tv: float, vertical_tv: float) -> None:
        print("UNIMPLEMNETED")

    def set_vbs(self, vbs: float) -> None:
        print("UNIMPLEMENTED")

    def set_lcg(self, lcg: float) -> None:
        print("UNIMPLEMENTED")


class MissionStates(enum.Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    EMERGENCY = "EMERGENCY"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"
    NONE = "NONE"
    ACCEPTED = "ACCEPTED"
    CANCELLED = "CANCELED"
    REJECTED = "REJECTED"

    def __str__(self):
        return self.name

    def TERMINAL_STATES():
        return [MissionStates.COMPLETED,
                MissionStates.CANCELLED,
                MissionStates.STOPPED,
                MissionStates.NONE]


class ActuatorStates(enum.Enum):
    """
    Enum for actuator states to check if they've been set to neutral for publishing once before taking hands off.
    """
    NEUTRAL = "NEUTRAL"
    ENGAGED = "ENGAGED"
    DISENGAGED = "DISENGAGED"

    def __str__(self):
        return self.name
