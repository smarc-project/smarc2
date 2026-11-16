"""Python wrapper around the C++ GeorefUtils.

The C++ side has its own internal rclcpp node (in its own rclcpp context) and receives tf
on its own background thread, so nothing needs to be added to an rclpy executor. Example::

    import rclpy
    from geographic_msgs.msg import GeoPoint
    from smarc_georef_cpp import GeorefUtils, TransformException

    rclpy.init()
    node = rclpy.create_node('my_node')
    with GeorefUtils(node=node) as georef:
        try:
            point = georef.geopoint_to_point_stamped(
                GeoPoint(latitude=59.35, longitude=18.07), 'lolo/base_link')
            geopoint = georef.point_stamped_to_geopoint(point)
        except TransformException as e:
            print(e)
"""

from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped, TransformStamped
from rclpy.serialization import deserialize_message, serialize_message

from smarc_georef_cpp._georef_cpp import GeorefUtilsCpp, TransformException, shutdown_context

__all__ = ['GeorefUtils', 'TransformException', 'shutdown_context']

# Parameters copied from the rclpy node (the node argument) to the internal C++ node
_COPIED_PARAMETERS = ['use_sim_time']


class GeorefUtils:
    """Creates the C++ GeorefUtils (with an internal rclcpp node) and exposes its functions."""

    def __init__(self, node=None, ros_args=None):
        """Create the C++ GeorefUtils and its internal rclcpp node.

        :param node: optional rclpy node using this. Its use_sim_time is copied to the
            internal C++ node (once, at creation).
        :param ros_args: optional ROS command line arguments for the internal C++ node, e.g.
            ['--ros-args', '-r', '__node:=my_georef', '-p', 'use_sim_time:=true'].
            These override the values copied from node.
        """
        args = []
        if node is not None:
            args.append('--ros-args')
            for name in _COPIED_PARAMETERS:
                args += ['-p', f'{name}:={_to_ros_arg(node.get_parameter(name).value)}']
        args += list(ros_args or [])
        self._impl = GeorefUtilsCpp(args)

    @property
    def node_name(self) -> str:
        return self._impl.node_name()

    def get_utm_frame(self) -> str:
        """Name of the top level utm frame in the tf tree, e.g. 'utm_33_V'.

        Raises TransformException if there is no utm frame (e.g. no transforms received yet)
        or there are several.
        """
        return self._impl.get_utm_frame()

    def geopoint_to_point_stamped(self, geopoint: GeoPoint,
                                  target_frame: str = '') -> PointStamped:
        """Convert a GeoPoint to a PointStamped in target_frame (the utm frame if empty).

        Raises TransformException if there is no utm frame or more than one, or the transform
        to target_frame is not available.
        """
        data = self._impl.geopoint_to_point_stamped(serialize_message(geopoint), target_frame)
        return deserialize_message(data, PointStamped)

    def point_stamped_to_geopoint(self, point: PointStamped) -> GeoPoint:
        """Convert a PointStamped in any frame to a GeoPoint.

        Raises TransformException if there is no utm frame or more than one, or the transform
        to the utm frame is not available.
        """
        data = self._impl.point_stamped_to_geopoint(serialize_message(point))
        return deserialize_message(data, GeoPoint)

    def lookup_transform(self, target_frame: str, source_frame: str,
                         timeout_sec: float = 0.0) -> TransformStamped:
        """Latest transform from source_frame to target_frame.

        Raises TransformException if it is not available within timeout_sec.
        """
        data = self._impl.lookup_transform(target_frame, source_frame, timeout_sec)
        return deserialize_message(data, TransformStamped)

    def can_transform(self, target_frame: str, source_frame: str,
                      timeout_sec: float = 0.0) -> bool:
        """Whether the latest transform from source_frame to target_frame is available.

        Waits up to timeout_sec for it.
        """
        return self._impl.can_transform(target_frame, source_frame, timeout_sec)

    def shutdown(self):
        """Stop the tf listener and destroy the internal node.

        Called automatically on garbage collection.
        """
        self._impl.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.shutdown()


def _to_ros_arg(value):
    """Format a parameter value for a '-p name:=value' ROS argument (YAML syntax)."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)
