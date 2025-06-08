from enum import Enum
import json

from lolo_loiter.loiter_goal import LoiterGoal
from std_msgs.msg import String


class ActionSubMsg(Enum):
    GOAL = 0
    FEEDBACK = 2


class LoiterActionParsing:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionSubMsg,
    ) -> LoiterGoal | float:
        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and LoiterGoal types for usage in client and server.

        """
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionSubMsg.GOAL:
            goal = LoiterGoal()
            # goal.geopoint.latitude = float(fmt_dict["waypoint"]["latitude"])
            # goal.geopoint.longitude = float(fmt_dict["waypoint"]["longitude"])
            # goal.target_depth = float(fmt_dict["waypoint"]["target_depth"])
            # goal.min_altitude = float(fmt_dict["waypoint"]["min_altitude"])
            # goal.rpm = float(fmt_dict["waypoint"]["rpm"])
            goal.timeout = float(fmt_dict["loiter"]["timeout"])
            return goal
        elif component is ActionSubMsg.FEEDBACK:
            return float(fmt_dict["time_remaining"])

    def encode(
        self,
        val: LoiterGoal | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        if isinstance(val, (LoiterGoal,)):
            fmt_dict["loiter"] = {}
            # fmt_dict["waypoint"]["latitude"] = val.geopoint.latitude
            # fmt_dict["waypoint"]["longitude"] = val.geopoint.longitude
            # fmt_dict["waypoint"]["target_depth"] = val.target_depth
            # fmt_dict["waypoint"]["min_altitude"] = val.min_altitude
            # fmt_dict["waypoint"]["rpm"] = val.rpm
            fmt_dict["loiter"]["timeout"] = val.timeout
        elif isinstance(val, (float,)):
            fmt_dict["time_remaining"] = val
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
