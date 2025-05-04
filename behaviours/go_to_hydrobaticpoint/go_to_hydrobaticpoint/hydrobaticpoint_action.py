from enum import Enum
import json

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


class ActionComponent(Enum):
    GOAL = 0
    FEEDBACK = 2


class HydrobaticPointAction:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionComponent,
    ) -> PoseStamped | float:
        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and ROS native types for usage in client and server.
            
        """
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionComponent.GOAL:
            hydropoint = PoseStamped()
            hydropoint.header.frame_id = str(fmt_dict["hydropoint"]["frame_id"])
            hydropoint.pose.position.x = float(fmt_dict["hydropoint"]["position"]["x"])
            hydropoint.pose.position.x = float(fmt_dict["hydropoint"]["position"]["y"])
            hydropoint.pose.position.x = float(fmt_dict["hydropoint"]["position"]["z"])
            hydropoint.pose.orientation.x = float(fmt_dict["hydropoint"]["orientation"]["x"])
            hydropoint.pose.orientation.y = float(fmt_dict["hydropoint"]["orientation"]["y"])
            hydropoint.pose.orientation.z = float(fmt_dict["hydropoint"]["orientation"]["z"])
            hydropoint.pose.orientation.w = float(fmt_dict["hydropoint"]["orientation"]["w"])
            # TODO: add timeout
            # timeout = float(fmt_dict["hydropoint"]["timeout"])
            return hydropoint
        elif component is ActionComponent.FEEDBACK:
            # TODO: add time_remaining
            return float(fmt_dict["distance_remaining"])

    def encode(
        self,
        val: PoseStamped | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        if isinstance(val, (PoseStamped,)):
            fmt_dict["hydropoint"] = {}
            fmt_dict["hydropoint"]["frame_id"] = val.header.frame_id
            fmt_dict["hydropoint"]["position"] = {}
            fmt_dict["hydropoint"]["position"]["x"] = val.pose.position.x
            fmt_dict["hydropoint"]["position"]["y"] = val.pose.position.y
            fmt_dict["hydropoint"]["position"]["z"] = val.pose.position.z
            fmt_dict["hydropoint"]["orientation"] = {}
            fmt_dict["hydropoint"]["orientation"]["x"] = val.pose.orientation.x
            fmt_dict["hydropoint"]["orientation"]["y"] = val.pose.orientation.y
            fmt_dict["hydropoint"]["orientation"]["z"] = val.pose.orientation.z
            fmt_dict["hydropoint"]["orientation"]["w"] = val.pose.orientation.w
        elif isinstance(val, (float,)):
            fmt_dict["distance_remaining"] = val
        # TODO: add time remaining
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
