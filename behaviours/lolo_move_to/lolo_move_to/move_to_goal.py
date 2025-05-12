from geographic_msgs.msg import GeoPoint

class MoveToGoal():
    def __init__(self):
        self.geopoint = GeoPoint() # Lat/lon.
        self.target_depth = None   # In [m], positive depth is below the surface.
        self.min_altitude = None   # In [m], minimum distance to the seafloor.
        self.rpm = None            # Desired RPMs for horizontal thrusters.
        self.timeout = None        # In [s], time duration before aborting.

    def __str__(self):
        return f"lat:   {self.geopoint.latitude}\n"\
               + f"lon:   {self.geopoint.longitude}\n"\
               + f"tgt_depth: {self.target_depth}\n"\
               + f"min_alt:   {self.min_altitude}\n"\
               + f"rpm:       {self.rpm}\n"\
               + f"timeout:   {self.timeout}\n"

