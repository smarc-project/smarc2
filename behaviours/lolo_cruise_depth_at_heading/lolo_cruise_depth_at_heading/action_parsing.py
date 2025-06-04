from enum import Enum
import json

from lolo_cruise_depth_at_heading.cruise_depth_at_heading_goal import CruiseDepthHeadingGoal
from std_msgs.msg import String


class ActionSubMsg(Enum):
    GOAL = 0
    FEEDBACK = 2


class CruiseDepthHeadingActionParsing:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionSubMsg,
    ) -> CruiseDepthHeadingGoal | float:
        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and CruiseDepthHeadingGoal types for usage in client and server.

        """
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionSubMsg.GOAL:
            goal = CruiseDepthHeadingGoal()
            goal.heading = float(fmt_dict["target_heading"]["heading"])
            goal.target_depth = float(fmt_dict["target_depth"]["depth"])
            goal.min_altitude = float(fmt_dict["min_altitude"]["altitude"])
            goal.rpm = float(fmt_dict["rpm"])
            goal.timeout = float(fmt_dict["timeout"])
            return goal
        elif component is ActionSubMsg.FEEDBACK:
            return float(fmt_dict["time_remaining"])

    def encode(
        self,
        val: CruiseDepthHeadingGoal | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        fmt_dict["target_heading"] = {}
        fmt_dict["target_depth"] = {}
        fmt_dict["min_altitude"] = {}
        if isinstance(val, (CruiseDepthHeadingGoal,)):
            fmt_dict["target_heading"]["heading"] = val.heading
            fmt_dict["target_depth"]["depth"] = val.target_depth
            fmt_dict["min_altitude"]["altitude"] = val.min_altitude
            fmt_dict["rpm"] = val.rpm
            fmt_dict["timeout"] = val.timeout
        elif isinstance(val, (float,)):
            fmt_dict["time_remaining"] = val
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
