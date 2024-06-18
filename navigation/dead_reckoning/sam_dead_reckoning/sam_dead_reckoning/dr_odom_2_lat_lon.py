#!/usr/bin/python

# General
import math
import time as python_time
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
from tf_transformations import euler_from_quaternion  # quaternion_from_euler

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

from geodesy.utm import UTMPoint


class DrOdom2LatLon(Node):
    """
    This node will convert the yaw (enu) to compass heading in degrees
    """

    def __init__(self, namespace=None):
        super().__init__("dr_odom_2_lat_lon", namespace=namespace)
        self.get_logger().info("Starting node defined in dr_odom_2_lat_lon.py")

        self.robot_name = namespace
        # Subscription topics
        self.odom_topic = DRTopics.DR_ODOM_TOPIC
        # Publisher topics
        # Todo: update

        # Frame names
        self.utm_frame = 'utm'
        self.odom_frame = 'odom'

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(msg_type=Odometry, topic=self.odom_topic,
                                 callback=self.odom_callback, qos_profile=10)

        self.utm_zone_status = False
        self.utm_zone = []
        self.transform_status = False
        self.conversion_timeout = 2.5

        # Parameters for controlling behavior
        self.perform_conversion = False  # If False, callback will not perform conversion

        # Todo: update
        # self.compass_heading_pub = self.create_publisher(msg_type=Float64, topic=self.compass_heading_topic,
        #                                                  qos_profile=10)

        # Lat/Lon conversion client
        self.latlon_client = self.create_client(UTMLatLon,
                                                MissionTopics.UTM_LATLON_CONVERSION_SERVICE)
        self.future = None

        # Wait for the conversion service
        while not self.latlon_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f"Can't reach the service {MissionTopics.UTM_LATLON_CONVERSION_SERVICE}")

        # wait until the utm zone and bands are determined
        # while not self.utm_zone_status:
        #     self.determine_utm_zone()
            # if not self.utm_zone_status:
            #     python_time.sleep(1.0)

    def determine_utm_zone(self):
        if self.utm_zone_status:
            return

        self.get_logger().info("Determining UTM zone and band")

        # yaml method for finding the utm zone
        frames_yaml = self.tf_buffer.all_frames_as_yaml()
        frames_dict = yaml.safe_load(frames_yaml)
        if len(frames_dict) < 1:
            self.get_logger().info(f"TF Buffer has no frames")
            return
        frame_names = frames_dict.keys()

        # Verify  that utm frame is present
        if "utm" not in frame_names:
            return

        # Zone info is contained in the name of the utm frame parent, utm_%%_##
        utm_parent = frames_dict["utm"]["parent"]
        utm_parent_split = utm_parent.split("_")

        # Check that split results in expected number of elements, 3
        if len(utm_parent_split) != 3:
            return

        self.utm_zone = [utm_parent_split[1], utm_parent_split[2]]
        self.utm_zone_status = True

        self.get_logger().info(f'UTM Zone: {self.utm_zone}')

    def determine_transform_status(self, frame_name):

        if not self.utm_zone_status:
            return False

        try:
            transform_status = self.tf_buffer.can_transform(target_frame=f"utm_{self.utm_zone[0]}_{self.utm_zone[1]}",
                                                            source_frame=frame_name,
                                                            time=rclpy.time.Time(),
                                                            return_debug_tuple=True)

            if not transform_status:
                self.get_logger().info("say something here?")

            return transform_status

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().warn(f'Error while checking transform: {e}')
            return False

    def odom_callback(self, odom_msg):
        """
        Callback function for converting odometry messages to lat lon coordinates
        """

        odom_frame_id = odom_msg.header.frame_id

        self.determine_utm_zone()
        transform_status = self.determine_transform_status(odom_frame_id)

        # Check that both the utm zone and the transform between odom and utm are valid
        if False in [self.utm_zone_status, transform_status]:
            self.get_logger().info(f"UTM status: {self.utm_zone_status} - Transform status: {transform_status}")
            return

        try:
            utm_transform = self.tf_buffer.lookup_transform(target_frame=self.utm_frame,
                                                            source_frame=odom_msg.header.frame_id,
                                                            time=rclpy.time.Time())

            odom_utm_pose = self.transformed_odometry_to_pose(odom_msg, utm_transform, self.utm_frame)
            self.get_logger().info(f"utm transform")

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().error(f'Failed to transform odometry: {e}')
            return

        # Construct the request
        # Testing data: ((59.348518, 18.071837), (333508.24, 6582521.93, 34, "V")), # -> smarc
        self.get_logger().info(f"Construct Request")
        req = UTMLatLon.Request()
        req.utm_points = []
        req.lat_lon_points = []

        ps = PointStamped()
        # ps.header.frame_id = f"utm_{self.utm_zone[0]}_{self.utm_zone[1]}"
        # ps.point.x = odom_utm_pose.position.x
        # ps.point.y = odom_utm_pose.position.y
        ps.header.frame_id = "utm_34_V"
        ps.point.x = 333508.24
        ps.point.y = 6582521.93
        req.utm_points.append(ps)

        # Just for testing
        gp = GeoPoint()
        gp.latitude = 59.348518
        gp.longitude = 18.071837
        req.lat_lon_points.append(gp)

        #
        # self.get_logger().info(f"Call async")
        # future = self.latlon_client.call_async(request=req)
        # self.get_logger().info(f"Spin until complete")
        # rclpy.spin_until_future_complete(node=self, future=future, timeout_sec=self.conversion_timeout)

        if self.perform_conversion:
            self.future = self.latlon_client.call_async(req)

            while rclpy.ok():
                rclpy.spin_once(self)
                if self.future.done():
                    try:
                        response = self.future.result()
                        self.get_logger().info(f'Response: {response}')
                    except Exception as e:
                        self.get_logger().error(f'Service call failed: {e}')
                    break
                else:
                    self.get_logger().info('Waiting for service response...')

            # Check for completion, timeout
            if not self.future.done():
                self.get_logger().info(f"LAT LON Service failed!!")
                return

            # Check if the future resulted in an exception
            if self.future.result() is None:
                self.get_logger().error(f"Service call failed with exception: {self.future.exception()}")
                return

            self.get_logger().info(f"LAT LON Service complete!!")

            result = self.future.result()
            gp_result = result.lat_lon_points[0]

            self.get_logger().info(f"LAT: {gp_result.latitude} / LON: {gp_result.longitude} ")
        else:
            self.get_logger().info(f"Odom conversion not performed!")
        # Publish the geopoint to make ozer happy

    def transformed_odometry_to_pose(self, odom_msg, transform, target_frame) -> Pose:
        # Create a new odometry message for the transformed odometry
        transformed_odom = Odometry()

        # Copy the header and twist information
        transformed_odom.header.stamp = self.get_clock().now().to_msg()
        transformed_odom.header.frame_id = target_frame
        transformed_odom.child_frame_id = odom_msg.child_frame_id
        transformed_odom.twist = odom_msg.twist

        # Transform the pose
        transformed_pose = do_transform_pose(odom_msg.pose.pose, transform)

        return transformed_pose


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
