#include <cmath>
#include <memory>
#include <string>

#include "gtest/gtest.h"

#include "geographic_msgs/msg/geo_point.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/static_transform_broadcaster.h"
#include "smarc_georef_cpp/georef_utils.hpp"

namespace
{

geographic_msgs::msg::GeoPoint geopoint(double latitude, double longitude, double altitude)
{
  geographic_msgs::msg::GeoPoint point;
  point.latitude = latitude;
  point.longitude = longitude;
  point.altitude = altitude;
  return point;
}

void expect_fallback(
  GeorefUtils & georef,
  double latitude, double longitude, double altitude,
  const std::string & frame, double easting, double northing)
{
  const auto utm = georef.geopoint_to_point_stamped(geopoint(latitude, longitude, altitude));
  EXPECT_EQ(utm.header.frame_id, frame);
  EXPECT_NEAR(utm.point.x, easting, 0.05);
  EXPECT_NEAR(utm.point.y, northing, 0.05);
  EXPECT_DOUBLE_EQ(utm.point.z, altitude);
}

geometry_msgs::msg::PoseStamped pose_at(double x, double y, int sec, unsigned int nanosec)
{
  geometry_msgs::msg::PoseStamped pose;
  pose.pose.position.x = x;
  pose.pose.position.y = y;
  pose.header.stamp.sec = sec;
  pose.header.stamp.nanosec = nanosec;
  return pose;
}

geometry_msgs::msg::Pose pose_with_quat(double w, double x, double y, double z)
{
  geometry_msgs::msg::Pose pose;
  pose.orientation.w = w;
  pose.orientation.x = x;
  pose.orientation.y = y;
  pose.orientation.z = z;
  return pose;
}

}  // namespace

TEST(PureConversions, LatlonZoneUntilAFrameExists)
{
  if (!rclcpp::ok()) {
    rclcpp::init(0, nullptr);
  }
  auto node = std::make_shared<rclcpp::Node>("georef_fallback_test");
  GeorefUtils georef(node.get());

  expect_fallback(georef, 59.35, 18.07, 12.5, "utm_34_V", 333411.098774, 6582691.449031);
  expect_fallback(
    georef, 58.840375663143504, 17.651532086943128, -0.5,
    "utm_33_V", 653015.744925, 6525308.628946);
  expect_fallback(georef, 0.1, 0.1, 0.0, "utm_31_N", 177164.295219, 11067.273502);
  expect_fallback(georef, 72.0, 18.0, 1.0, "utm_34_X", 396566.945625, 7991508.542710);

  geometry_msgs::msg::TransformStamped tf;
  tf.header.frame_id = "utm_33_V";
  tf.child_frame_id = "map";
  tf.transform.rotation.w = 1.0;
  tf2_ros::StaticTransformBroadcaster broadcaster(node);
  broadcaster.sendTransform(tf);
  ASSERT_TRUE(georef.can_transform("map", "utm_33_V", 2.0));

  const auto replaced = georef.geopoint_to_point_stamped(geopoint(59.35, 18.07, 12.5));
  EXPECT_EQ(replaced.header.frame_id, "utm_33_V");
}

TEST(PureConversions, RejectsABadFrame)
{
  geometry_msgs::msg::PointStamped point;
  point.header.frame_id = "map";
  EXPECT_THROW(convert_utm_to_latlon(point), std::invalid_argument);
}

TEST(PureConversions, EnuYawToCompassHeading)
{
  EXPECT_NEAR(convert_enu_pose_to_heading(pose_with_quat(1, 0, 0, 0)), 90.0, 1e-9);
  EXPECT_NEAR(
    convert_enu_pose_to_heading(pose_with_quat(0.707106781186548, 0, 0, 0.707106781186547)),
    0.0, 1e-6);
  EXPECT_NEAR(
    convert_enu_pose_to_heading(pose_with_quat(0.707106781186548, 0, 0, -0.707106781186547)),
    180.0, 1e-6);
  EXPECT_NEAR(convert_enu_pose_to_heading(pose_with_quat(0, 0, 0, 1)), 270.0, 1e-6);
  EXPECT_NEAR(
    convert_enu_pose_to_heading(pose_with_quat(0.923879532511287, 0, 0, 0.382683432365090)),
    45.0, 1e-6);
}

TEST(PureConversions, CourseAndSpeedFromTwoPoses)
{
  const auto origin = pose_at(0.0, 0.0, 10, 0);
  EXPECT_NEAR(compute_course_from_two_poses(origin, pose_at(10.0, 0.0, 11, 0)), 0.0, 1e-9);
  EXPECT_NEAR(compute_course_from_two_poses(origin, pose_at(0.0, 10.0, 11, 0)), 90.0, 1e-9);
  EXPECT_NEAR(compute_course_from_two_poses(origin, pose_at(-10.0, 0.0, 11, 0)), 180.0, 1e-9);
  EXPECT_NEAR(compute_course_from_two_poses(origin, pose_at(0.0, -10.0, 11, 0)), 270.0, 1e-9);
  EXPECT_NEAR(compute_speed_from_two_poses(origin, pose_at(3.0, 4.0, 11, 0)), 5.0, 1e-9);
  EXPECT_DOUBLE_EQ(compute_speed_from_two_poses(origin, pose_at(3.0, 4.0, 10, 0)), 0.0);
}
