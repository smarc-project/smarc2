#!/usr/bin/python3

from .waypoint import UnderwaterWaypoint
from smarc_mission_msgs.msg import GotoWaypoint

class ROSWP(UnderwaterWaypoint):
    def __init__(self, goto_waypoint: GotoWaypoint) -> None:
        super().__init__()

        self.goto_wp = goto_waypoint

    @property
    def name(self) -> str:
        return self.goto_wp.name

    @property
    def is_actionable(self) -> bool:
        """
        Check that the WP is not all 0s...
        """
        x,y,z = self.position
        d = self.travel_depth
        a = self.travel_altitude
        if all([x==0, y==0, z==0, d==0, a==0]): return False
        return True
    
    @property
    def position(self) -> tuple[float, float, float]:
        p = self.goto_wp.pose.pose.position
        return (p.x, p.y, p.z)
    
    @property
    def reference_frame(self) -> str:
        return self.goto_wp.pose.header.frame_id
    
    @property
    def travel_depth(self) -> float:
        return self.goto_wp.travel_depth
    
    @property
    def travel_altitude(self) -> float:
        return self.goto_wp.travel_altitude
    
    @property
    def arrival_heading(self) -> float:
        if self.goto_wp.use_heading:
            return self.goto_wp.arrival_heading
        else: 
            return None