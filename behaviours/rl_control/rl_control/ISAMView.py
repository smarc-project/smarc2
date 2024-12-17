#!/usr/bin/python3

import enum
from nav_msgs.msg import Odometry

class ISAMView:
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

    def get_state(self) -> Odometry:
        print("UNIMPLEMENTED")