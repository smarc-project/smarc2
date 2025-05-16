#!/usr/bin/python3



class IWaypoint():
    @property
    def name(self) -> str: pass
    @property
    def is_actionable(self) -> bool: pass
    @property
    def position(self) -> tuple[float, float, float]: pass
    @property
    def reference_frame(self) -> str: pass
    def __str__(self) -> str: pass
    @property
    def arrival_heading(self) -> float: pass

class IUnderwaterWaypoint(IWaypoint):
    @property
    def travel_depth(self) -> float: pass
    @property
    def travel_altitude(self) -> float: pass



class Waypoint(IWaypoint):
    def __init__(self) -> None:
        print("NOT IMPLEMENTED")


class UnderwaterWaypoint(IUnderwaterWaypoint):
    def __str__(self) -> str:
        return f"[WP {self.name}] Posi:{self.position} D:{self.travel_depth} A:{self.travel_altitude}"


    