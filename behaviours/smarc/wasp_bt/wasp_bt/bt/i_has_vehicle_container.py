#!/usr/bin/python3
from ..vehicles.vehicle import IVehicleStateContainer

class HasVehicleContainer():
    @property
    def vehicle_container(self) -> IVehicleStateContainer: pass