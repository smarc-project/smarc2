#include <cmath>
#include <string>

#include "gtest/gtest.h"

#include "geographic_msgs/msg/geo_point.hpp"
#include "geometry_msgs/msg/pose.hpp"
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

void expect_utm(
  double latitude, double longitude, double altitude,
  const std::string & frame, double easting, double northing)
{
  const auto utm = convert_latlon_to_utm(geopoint(latitude, longitude, altitude));
  EXPECT_EQ(utm.header.frame_id, frame);
  EXPECT_NEAR(utm.point.x, easting, 0.05);
  EXPECT_NEAR(utm.point.y, northing, 0.05);
  EXPECT_DOUBLE_EQ(utm.point.z, altitude);

  const auto back = convert_utm_to_latlon(utm);
  EXPECT_NEAR(back.latitude, latitude, 1e-8);
  EXPECT_NEAR(back.longitude, longitude, 1e-8);
  EXPECT_DOUBLE_EQ(back.altitude, altitude);
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

TEST(PureConversions, MatchesGeodesyUtm)
{
  expect_utm(59.35, 18.07, 12.5, "utm_34_V", 333411.098774, 6582691.449031);
  expect_utm(
    58.840375663143504, 17.651532086943128, -0.5,
    "utm_33_V", 653015.744925, 6525308.628946);
  expect_utm(-33.9, 151.2, 10.0, "utm_56_H", 333568.941012, -3752526.663156);
  expect_utm(0.1, 0.1, 0.0, "utm_31_N", 177164.295219, 11067.273502);
  expect_utm(72.0, 18.0, 1.0, "utm_34_X", 396566.945625, 7991508.542710);
  expect_utm(-80.0, 18.0, 0.0, "utm_34_C", 441867.784867, -8883084.955948);
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
