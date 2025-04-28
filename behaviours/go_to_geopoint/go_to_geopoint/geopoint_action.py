from enum import Enum
import json

from geographic_msgs.msg import GeoPoint
from std_msgs.msg import String


class ActionComponent(Enum):
    GOAL = 0
    FEEDBACK = 2


class GeoPointAction:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionComponent,
    ) -> GeoPoint | float:
        """Decodes action message from json to Python / ROS types."""
        fmt_dict = json.loads(serialized_fmt.data)
        if component is ActionComponent.GOAL:
            geopoint = GeoPoint()
            geopoint.latitude = float(fmt_dict["geopoint"]["latitude"])
            geopoint.longitude = float(fmt_dict["geopoint"]["longitude"])
            geopoint.altitude = float(fmt_dict["geopoint"]["altitude"])
            return geopoint
        elif component is ActionComponent.FEEDBACK:
            return float(fmt_dict["distance_remaining"])

    def encode(
        self,
        val: GeoPoint | float,
    ) -> String | None:
        """Encodes action message into string."""
        str_msg = String()
        fmt_dict = {}
        if isinstance(val, (GeoPoint,)):
            fmt_dict["geopoint"] = {}
            fmt_dict["geopoint"]["latitude"] = val.latitude
            fmt_dict["geopoint"]["longitude"] = val.longitude
            fmt_dict["geopoint"]["altitude"] = val.altitude
        elif isinstance(val, (float,)):
            fmt_dict["distance_remaining"] = val
        else:
            return None
        str_val = json.dumps(fmt_dict)
        str_msg.data = str_val
        return str_msg
