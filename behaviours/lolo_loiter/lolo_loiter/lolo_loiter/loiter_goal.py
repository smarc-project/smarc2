from geographic_msgs.msg import GeoPoint

class LoiterGoal():
    def __init__(self):
        self.timeout = None        # In [s], time duration before aborting.

    def __str__(self):
        return f"timeout: {self.timeout}\n"

