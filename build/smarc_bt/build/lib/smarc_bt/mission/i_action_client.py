#!/usr/bin/python3

from rclpy.node import Node
import enum

class ActionClientState(enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    READY = "READY"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    CANCELLING = "CANCELLING"
    ERROR = "ERROR"

    def __str__(self):
        return self.name
    


class IActionClient():
    def __init__(self, node: Node): pass
    @property
    def feedback_message(self) -> str: pass
    @property
    def state(self) -> ActionClientState: pass
    def setup(self, timeout:int=10) -> bool: pass
    def send_goal(self, wp) -> bool: pass
    def cancel_goal(self): pass
    def get_ready(self): pass
    def _log(self, s:str):pass