from enum import Enum
import json

from geographic_msgs.msg import GeoPoint
from std_msgs.msg import String


class ActionSubMsg(Enum):
    GOAL = 0
    FEEDBACK = 2


class GeoActionParsing:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionSubMsg,
    ) -> GeoPoint | float:
        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and ROS native types for usage in client and server.
            
        """
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionSubMsg.GOAL:
            geopoint = GeoPoint()
            geopoint.latitude = float(fmt_dict["waypoint"]["latitude"])
            geopoint.longitude = float(fmt_dict["waypoint"]["longitude"])
            geopoint.altitude = float(fmt_dict["waypoint"]["altitude"])
            return geopoint
        elif component is ActionSubMsg.FEEDBACK:
            return float(fmt_dict["distance_remaining"])

    def encode(
        self,
        val: GeoPoint | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        if isinstance(val, (GeoPoint,)):
            fmt_dict["waypoint"] = {}
            fmt_dict["waypoint"]["latitude"] = val.latitude
            fmt_dict["waypoint"]["longitude"] = val.longitude
            fmt_dict["waypoint"]["altitude"] = val.altitude
        elif isinstance(val, (float,)):
            fmt_dict["distance_remaining"] = val
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
