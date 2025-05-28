from enum import Enum
import json

from lolo_move_to.move_to_goal import MoveToGoal
from std_msgs.msg import String


class ActionSubMsg(Enum):
    GOAL = 0
    FEEDBACK = 2


class MoveToActionParsing:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionSubMsg,
    ) -> MoveToGoal | float:
        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and MoveToGoal types for usage in client and server.

        """
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionSubMsg.GOAL:
            goal = MoveToGoal()
            goal.geopoint.latitude = float(fmt_dict["geopoint"]["latitude"])
            goal.geopoint.longitude = float(fmt_dict["geopoint"]["longitude"])
            goal.target_depth = float(fmt_dict["target_depth"])
            goal.min_altitude = float(fmt_dict["min_altitude"])
            goal.rpm = float(fmt_dict["rpm"])
            goal.timeout = float(fmt_dict["timeout"])
            return goal
        elif component is ActionSubMsg.FEEDBACK:
            return float(fmt_dict["distance_remaining"])

    def encode(
        self,
        val: MoveToGoal | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        if isinstance(val, (MoveToGoal,)):
            fmt_dict["geopoint"] = {}
            fmt_dict["geopoint"]["latitude"] = val.geopoint.latitude
            fmt_dict["geopoint"]["longitude"] = val.geopoint.longitude
            fmt_dict["target_depth"] = val.target_depth
            fmt_dict["min_altitude"] = val.min_altitude
            fmt_dict["rpm"] = val.rpm
            fmt_dict["timeout"] = val.timeout
        elif isinstance(val, (float,)):
            fmt_dict["distance_remaining"] = val
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
