from enum import Enum
import json

import numpy as np

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from std_msgs.msg import String, Header
#import rospy


class ActionComponent(Enum):
    GOAL = 0
    FEEDBACK = 2


class PathAction:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionComponent,
    ) -> Path:

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
            path = self.convert_lists_to_ndarrays(fmt_dict["path"])
            return path

        elif component is ActionComponent.FEEDBACK:
            return float(fmt_dict["index"])


    def encode(
        self,
        path: list | float,
    ) -> String | None:

        """Encodes action message into string."""

        str_msg = String()
        path_dict = {}

        if isinstance(path, (list,)):
            path_dict["path"] = self.convert_ndarrays(path)

        elif isinstance(path, (float,)):
            path_dict["index"] = path 
        else:
            return None

        str_val = json.dumps(path_dict)
        str_msg.data = str_val
        return str_msg


    def convert_lists_to_ndarrays(self, obj):
        if isinstance(obj, list):
            # Check if this list looks like a matrix/vector
            if all(isinstance(el, (int, float, list)) for el in obj):
                try:
                    return np.array(obj)
                except:
                    # If not uniform shape, keep it as a list of arrays
                    return [self.convert_lists_to_ndarrays(el) for el in obj]
            else:
                return [self.convert_lists_to_ndarrays(el) for el in obj]
        elif isinstance(obj, dict):
            return {k: self.convert_lists_to_ndarrays(v) for k, v in obj.items()}
        else:
            return obj

    def convert_ndarrays(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            return [self.convert_ndarrays(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_ndarrays(val) for key, val in obj.items()}
        else:
            return obj



