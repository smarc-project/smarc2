#!/usr/bin/python3

class IThrustView:
    """
    An interface for some kind of "view" that can do _something_ with a given RPM value.
    """
    def set_rpm(self, rpm: int) -> None:
        print("UNIMPLEMENTED")
