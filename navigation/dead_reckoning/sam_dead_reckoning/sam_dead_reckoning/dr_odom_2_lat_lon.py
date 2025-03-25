#!/usr/bin/python

# General
import yaml

# ROS
import rclpy
from rclpy.node import Node
from rclpy import time

# Transforms
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

from tf2_geometry_msgs import do_transform_pose

# Messages
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped

# Services
from smarc_mission_msgs.srv import UTMLatLon

# SMaRC Topics
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics
from smarc_mission_msgs.msg import Topics as MissionTopics
from utm_latlon_converter.converter_service_node import GeoConverterService
import asyncio

from geodesy.utm import UTMPoint

try:
    from .helpers.ros_helpers import rcl_time_to_secs
except ImportError:
    from helpers.ros_helpers import rcl_time_to_secs


class DrOdom2LatLon(Node):
    """
    This node will convert the yaw (enu) to compass heading in degrees
    """

    def __init__(self, namespace=None):
        super().__init__("dr_odom_2_lat_lon", namespace=namespace)
        self._log("Starting node defined in dr_odom_2_lat_lon.py")

        self.robot_name = namespace
        # Subscription topics
        self.odom_topic = DRTopics.DR_ODOM_TOPIC
        # Publisher topics
        self.lat_lon_topic = DRTopics.DR_LAT_LON_TOPIC

        # Frame names
        self.map_frame = self.get_parameter("map_frame").value
        self.tf_buffer = Buffer(rclpy.duration.Duration(seconds=5.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(msg_type=Odometry, topic=self.odom_topic,
                                 callback=self.odom_callback, qos_profile=10)

        self.utm_zone_status = False
        self.utm_zone = []
        self.transform_status = False
        self.conversion_timeout = 2.5

        # Parameters for controlling behavior
        self.perform_conversion = True  # If False, callback will not perform conversion
        self.perform_test_conversion = True  # Only use for testing
        self.status_last_time = None
        self.status_min_period = 2.0
        self.verbose_conversion = False

        self.lat_lon_pub = self.create_publisher(msg_type=GeoPoint, topic=self.lat_lon_topic,
                                                         qos_profile=10)

        # # Lat/Lon conversion client
        # self.latlon_client = self.create_client(UTMLatLon,
        #                                         MissionTopics.UTM_LATLON_CONVERSION_SERVICE)

        # self.future = None  # Note sure if this is needed

        # # Wait for the conversion service
        # while not self.latlon_client.wait_for_service(timeout_sec=1.0):
        #     self._log(f"Can't reach the service {MissionTopics.UTM_LATLON_CONVERSION_SERVICE}")

    def _log(self, message):
        self.get_logger().info(message)

    def determine_utm_zone(self):
        # if self.utm_zone_status:
        #     return

        # self._log("Determining UTM zone and band")

        frames_yaml = self.tf_buffer.all_frames_as_yaml(rclpy.time.Time())
        frames_dict = yaml.safe_load(frames_yaml)
        if len(frames_dict) < 1:
            self._log(f"TF Buffer has no frames")
            return
        frame_names = frames_dict.keys()

        # # Verify  that utm frame is present
        if self.map_frame not in frame_names:
            return

        # # Zone info is contained in the name of the utm frame parent, utm_%%_##
        utm_frame = frames_dict["map"]["parent"]
        utm_parent_split = utm_frame.split("_")
        self.get_logger().info(f'UTM frame: {utm_frame}', once=True)

        # # Check that split results in expected number of elements, 3
        if len(utm_parent_split) != 3:
            return

        # self.utm_zone = [utm_parent_split[1], utm_parent_split[2]]
        self.utm_zone = ["34", "V"]
        self.utm_zone_status = True


    def determine_transform_status(self, frame_name):

        if not self.utm_zone_status:
            return False

        try:
            transform_status = self.tf_buffer.can_transform(target_frame=f"utm_{self.utm_zone[0]}_{self.utm_zone[1]}",
                                                            source_frame=frame_name,
                                                            time=rclpy.time.Time(),
                                                            return_debug_tuple=True)

            if not transform_status:
                self._log("say something here?")

            return transform_status

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().warn(f'Error while checking transform: {e}')
            return False

    def odom_callback(self, odom_msg):
        """
        Callback function for converting odometry messages to lat lon coordinates
        """
        # # Check that the service is available
        # if not self.latlon_client.service_is_ready():
        #     return

        # Regulate the rate of status and latlon updates
        # Might be better to move to a timer at some point...
        current_odom_time = rcl_time_to_secs(self.get_clock().now())
        if self.check_status_valid(current_odom_time) and self.verbose_conversion:
            self._log("Odom Callback")
        else:
            return

        # Check that both the utm zone and the transform between odom and utm are valid
        odom_frame_id = odom_msg.header.frame_id
        self.determine_utm_zone()
        transform_status = self.determine_transform_status(odom_frame_id)

        if False in [self.utm_zone_status, transform_status]:
            self._log(f"UTM status: {self.utm_zone_status} - Transform status: {transform_status}")
            return

        # Perform the odom -> utm conversion
        try:
            utm_transform = self.tf_buffer.lookup_transform(target_frame=f"utm_{self.utm_zone[0]}_{self.utm_zone[1]}",
                                                            source_frame=odom_msg.header.frame_id,
                                                            time=rclpy.time.Time())

            odom_utm_pose = do_transform_pose(odom_msg.pose.pose, utm_transform)

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().error(f'Failed to transform odometry: {e}')
            return
        
        self.lat_long_conv(odom_utm_pose)


    def lat_long_conv(self, odom_utm_pose):
        
        # Construct real request
        req = UTMLatLon.Request()
        req.utm_points = []
        req.lat_lon_points = []

        ps = PointStamped()
        ps.header.frame_id = f"utm_{self.utm_zone[0]}_{self.utm_zone[1]}"
        ps.point.x = odom_utm_pose.position.x
        ps.point.y = odom_utm_pose.position.y
        req.utm_points.append(ps)

        response = GeoConverterService.convert(req, UTMLatLon.Response())
        lat_lon_points = response.lat_lon_points

        # Check service response Lat Lon points
        # (1) lat_lon_points is a non-empty list
        # (2) Valid point != None
        if len(lat_lon_points) == 0:
            self._log(f"LAT LON conversion returned no points")
            return

        if lat_lon_points[0] is None:
            self._log(f"LAT LON conversion returned no valid points")
            return

        if self.verbose_conversion:
            self._log(f"Latitude: {lat_lon_points[0].latitude}, Longitude: {lat_lon_points[0].longitude}")

        self.lat_lon_pub.publish(lat_lon_points[0])


    def check_status_valid(self, current_time: float):
        """
        check if it is time to provide a status update
        """
        if self.status_last_time is None:
            self.status_last_time = current_time
            status_valid = True
        elif current_time - self.status_last_time >= self.status_min_period:
            self.status_last_time = current_time
            status_valid = True
        else:
            status_valid = False

        return status_valid


def main(args=None, namespace=None):
    rclpy.init(args=args)
    lat_lon_node = DrOdom2LatLon(namespace=namespace)
    try:
        rclpy.spin(lat_lon_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "sam0"
    main(namespace=default_namespace)
