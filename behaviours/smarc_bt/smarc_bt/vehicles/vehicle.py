#!/usr/bin/python3

try:
    from sensor import Sensor, SensorNames
except:
    from .sensor import Sensor, SensorNames

    
from typing import Type

class IVehicleState():
    def update_sensor(self, sensor_name:str, values, time:float): pass
    def update_sensor_status_str(self, sensor_name:str, status:str): pass
    def __getitem__(self, key:str): pass
    def abort(self) -> None: pass
    @property
    def aborted(self) -> bool: pass
    @property
    def vehicle_healthy(self) -> bool: pass


class IVehicleStateContainer():
    @property
    def vehicle_state(self) -> Type[IVehicleState]: pass
    def abort(self) -> bool: pass
    def heartbeat(self) -> bool: pass
    


class MockVehicleStateContainer(IVehicleStateContainer):
    def __init__(self, state_type: Type[IVehicleState]) -> None:
        self._vehicle_state = state_type("Mock", "Nowhere")
    
    @property
    def vehicle_state(self) -> Type[IVehicleState]:
        return self._vehicle_state
    
    def abort(self) -> bool:
        return True
    
    def heartbeat(self) -> bool:
        return True



class VehicleState(IVehicleState):
    LATLON = "LATLON"
    ABSOLUTE = "ABSOLUTE"
    PERCENT = "PERCENT"

    def __init__(self, name: str, reference_frame: str):
        """
        The base vehicle object that contains the common things every vehicle needs to have.
        name: just a string to identify the vehicle
        reference_frame: the reference frame of position stuffs
        """
        # name of the vehicle and the reference frame that
        # all its attributes work with
        # the reference frame could be 'odom', could be "utm_XY_Z"
        self._reference_frame = reference_frame
        self._name = name

        
        # x,y,height
        # where height is above sea --> negative when under water
        self._position = Sensor(SensorNames.POSITION,
                                self._reference_frame,
                                3)

        # yaw pitch roll
        self._orientation_euler = Sensor(SensorNames.ORIENTATION_EULER,
                                         self._reference_frame,
                                         3,
                                         ["roll", "pitch", "yaw"])

        # global position, lat lon heading
        # separate from the above because this'll likely come
        # from gps fixes and not DR
        self._global_position = Sensor(SensorNames.GLOBAL_POSITION,
                                       VehicleState.LATLON,
                                       2,
                                       ["lat", "lon"])
        
        self._global_heading_deg = Sensor(SensorNames.GLOBAL_HEADING_DEG,
                                          VehicleState.LATLON,
                                          1)
        
        self._battery = Sensor(SensorNames.BATTERY,
                               VehicleState.ABSOLUTE,
                               2,
                               ["V", "%"])
        
        self._vehicle_healthy = Sensor(SensorNames.VEHICLE_HEALTHY,
                                       VehicleState.ABSOLUTE,
                                       1)

        self.sensors = {}
        for k,v in vars(self).items():
            if type(v) == Sensor:
                self.sensors[v._name] = v

        self._aborted = False

    
    @property
    def aborted(self):
        return self._aborted
    
    @property
    def vehicle_healthy(self) -> bool:
        return self._vehicle_healthy[0]
    

    def __str__(self) -> str:
        s = f"Vehicle:{self._name}\n"
        
        if self.aborted:
            s += "ABORTED"
            return s
        
        for sensor_name, sensor in self.sensors.items():
            s += "- " + sensor.__str__() + "\n"
        return s
    
    
    def __getitem__(self, key: str) -> Sensor:
        return self.sensors[key]


    def abort(self):
        self._aborted = True


    # These could be convenient to write some generic "update" functions for ROS
    # related reasons later.
    def update_sensor(self, sensor_name:str, values, time:float):
        """
        sensor_name: the name of the sensor object that you can find in the constructors
        values, time: passed straight to the sensor object
        """
        self.sensors[sensor_name].update(values, time)


    def update_sensor_status_str(self, sensor_name:str, status:str):
        self.sensors[sensor_name].update_status_str(status)



class UnderwaterVehicleState(VehicleState):
    def __init__(self, name: str, reference_frame: str):
        """
        Extends the base vehicle to include underwater-related basics
        """
        
        self._depth = Sensor(SensorNames.DEPTH, VehicleState.ABSOLUTE, 1)
        self._altitude = Sensor(SensorNames.ALTITUDE, VehicleState.ABSOLUTE, 1)
        self._leak = Sensor(SensorNames.LEAK, VehicleState.ABSOLUTE, 1)
        self._vbs = Sensor(SensorNames.VBS, VehicleState.PERCENT, 1)
        self._lcg = Sensor(SensorNames.LCG, VehicleState.PERCENT, 1)
        self._thrusters = Sensor(SensorNames.THRUSTERS, VehicleState.ABSOLUTE, 2)
        
        
        super().__init__(name, reference_frame)



if __name__ == "__main__":
    v = UnderwaterVehicleState("test vehicle", "utm123")
    print(v[SensorNames.POSITION].working)
    v.update_sensor(SensorNames.POSITION, [1,2,3], 0)
    print(v[SensorNames.POSITION].working)
    v.update_sensor(SensorNames.LCG, [10], 0)
    print(v)
    v.update_sensor(SensorNames.POSITION, [2,3,4], 1)
    print(v)

    print(v.all_sensors_working)
    v.update_sensor(SensorNames.ORIENTATION_EULER, [1,2,3], 0)
    v.update_sensor(SensorNames.GLOBAL_POSITION, [1,2], 0)
    v.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [1], 0)
    v.update_sensor(SensorNames.BATTERY, [1,2], 0)
    v.update_sensor(SensorNames.ALTITUDE, [1], 0)
    v.update_sensor(SensorNames.LEAK, [False], 0)
    v.update_sensor(SensorNames.VBS, [1], 0)
    v.update_sensor(SensorNames.THRUSTERS, [1,2], 0)
    print(v.all_sensors_working)

    print([(s._name, s.working) for _,s in v.sensors.items()])