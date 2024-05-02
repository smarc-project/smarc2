#!/usr/bin/python3
import numpy as np
import time
import enum

class SensorNames(str, enum.Enum):
    POSITION = "position"
    ORIENTATION_EULER = "orientation_euler"
    GLOBAL_POSITION = "global_position"
    GLOBAL_HEADING_DEG = "global_heading_deg"
    BATTERY = "battery"
    ALTITUDE = "altitude"
    DEPTH = "depth"
    LEAK = "leak"
    VBS = "VBS"
    LCG = "LCG"
    TCG = "TCG"
    THRUSTERS = "thrusters"
    VEHICLE_HEALTHY = "vehicle_healthy"

    def __str__(self):
        return self.name

class Sensor:
    def __init__(self,
                 name: str,
                 reference_frame: str,
                 size: int,
                 value_names: list = None):
        """
        A sensor class to keep track of when things were recorded and their values.
        name: Name of the sensor
        reference_frame: if the values are in reference to something else. Usually TF frames if ROS
        size: how many values are there
        value_names: optional names for each of the values to keep track
        """
        assert size > 0, f"Sensor values must have positive number of values! Given: {size}"
        assert len(reference_frame) > 0, f"Reference frame must not be empty!"

        self._name = name
        self._reference_frame = reference_frame
        
        self._values = np.array([None]*size)

        self._value_names = value_names
        self._last_update_seconds = None
        self._status_str = ""


    @property
    def name(self):
        return self._name

    @property
    def working(self):
        return all([v is not None for v in self._values])

    @property
    def last_update_seconds(self) -> int:
        return self._last_update_seconds


    # Some convenience functions to
    # make it possible to access the sensor values
    def __getitem__(self, key):
        if self._value_names is None:
            return self._values[key]
        idx = self._value_names.index(key)
        return self._values[idx]
    
    def __setitem__(self, key, value):
        if self._value_names is None:
            self._values[key] = value
            return
        idx = self._value_names.index(key)
        self._values[idx] = value


    def _last_update_str(self):
        tdiff = time.time() - self._last_update_seconds
        if tdiff > 60*5:
            tstr = f"{int(tdiff/60)} mins"
        else:
            tstr = f"{int(tdiff)} secs"
        return tstr
    

    def update(self, values, time: float):
        assert len(values) == len(self._values), "Update to a sensor must be made with the same number of values!"
        for i in range(len(self._values)):
            self._values[i] = values[i]
        self._last_update_seconds = time


    def update_status_str(self, s: str):
        self._status_str = s


    def __str__(self):
        s = f"{self._name} (ref:{self._reference_frame}):"

        if self._last_update_seconds is None:
            s += "Never updated"
            return s

        if self._value_names is None:
            s += str(self._values) + "\n"
        else:
            s += "\n"
            for name, val in zip(self._value_names, self._values):
                s += f"\t{name} = {val}\n"

        
        s += f"\tLast update:{self._last_update_str()} ago.\n"
        s += f"\tStatus:{self._status_str}"
        return s
