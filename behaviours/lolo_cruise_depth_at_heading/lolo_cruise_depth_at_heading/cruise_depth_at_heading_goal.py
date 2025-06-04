
class CruiseDepthHeadingGoal():
    def __init__(self):
        self.heading = None        # in [deg], NED compass heading from 0 (North) to 360.
        self.target_depth = None   # In [m], positive depth is below the surface.
        self.min_altitude = None   # In [m], minimum distance to the seafloor.
        self.rpm = None            # Desired RPMs for horizontal thrusters.
        self.timeout = None        # In [s], time duration before aborting.

    def __str__(self):
        return f"heading:   {self.heading}\n"\
               + f"tgt_depth: {self.target_depth}\n"\
               + f"min_alt:   {self.min_altitude}\n"\
               + f"rpm:       {self.rpm}\n"\
               + f"timeout:   {self.timeout}\n"

