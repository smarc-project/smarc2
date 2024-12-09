import os
from glob import glob
import pathlib
from typing import List

from rosbags.typesys import get_typestore, get_types_from_msg, Stores, store

class SmarcRosbagTypestore:
    """User path and configuration independent SMaRC typestore constructor for rosbags.

        WARN: Still dependent on repo configuration and message location within repo.

        # Example usage:
        ```
            from rosbag_types import SmarcRosbagTypestore

            smarc_types = SmarcRosbagTypestore()
            typestore = smarc_types.construct_custom_typestore()

            # Example iteration through rosbag can be found here:
            # https://ternaris.gitlab.io/rosbags/topics/rosbag2.html#reading-rosbag2
            # All items are the same just use the extended typestore with SMaRC custom messages
    """
    def __init__(self):
        self._typestore = get_typestore(Stores.ROS2_HUMBLE)
        self._script_path = pathlib.Path(__file__).parent.resolve()
        self._glob_path = self._construct_glob_path()
        self._message_paths = []
        self._custom_types = {}


    def _construct_glob_path(self):
        """Constructs glob path for finding all message files within repository.

            WARN: constructs relative to this files location
        """
        glob_path = self._script_path.parent.parent.resolve()
        glob_path = glob_path / "messages/**/*.msg"
        return glob_path

    def override_glob_path(self, glob_path: pathlib.Path):
        """Allows overriding of glob path that defaults based on repo.

            Can be useful if other types are located elsewhere and needed their own typestore.
            Args:
                glob_path: Path or string that is a glob type path that will be passed to glob.glob()
            Returns:
                None
        """
        self._glob_path = glob_path


    def find_all_msg_files(self) -> List[str]:
        """Finds all smarc msg files located in smarc2/messages folder structure
            Updates internal class structure.
        Returns:
            list of all absolute paths to messages files
        """
        # glob requires a string, which is annoying, and I don't like the Path Glob
        self._message_paths = glob(str(self._glob_path), recursive=True)
        return self._message_paths

    def construct_custom_typestore(self) -> store.Typestore:
        """Constructs custom typestore by guessing at message format name.

            Format internal to repo is generally as follows:
                `folder/msg/MsgName`
            Examples include: `smarc_msgs/msg/PercentStamped`
            Examples include: `sensor_msgs/msg/Imu`
        """
        self.find_all_msg_files()
        for msg_file in self._message_paths:
            msg_name = self.reconstruct_message_name(msg_file)
            msg_text = pathlib.Path(msg_file).read_text()
            msg_type = get_types_from_msg(msg_text, msg_name)
            self._custom_types.update(msg_type)
        self._typestore.register(self._custom_types)
        return self._typestore


    @staticmethod
    def reconstruct_message_name(msg_path) -> str:
        """Guesses at message name structure for ROS typestore.

            Format internal to repo is generally as follows:
                `folder/msg/MsgName`
            Examples include: `smarc_msgs/msg/PercentStamped`
            Examples include: `sensor_msgs/msg/Imu`

            Args:
                msg_path: absolute path of message filew
            Returns:
                message name within SMaRC system
        """
        split_path = msg_path.split("/")
        ros_message = split_path[-3:]
        joined_name = r"/".join(ros_message)
        return joined_name.split('.')[0]

if __name__ == "__main__":
    smarc_types = SmarcRosbagTypestore()
    print(smarc_types._script_path)
    print(smarc_types._glob_path)
    smarc_types.find_all_msg_files()
    smarc_types.construct_custom_typestore()
