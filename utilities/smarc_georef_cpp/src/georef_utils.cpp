#include "smarc_georef_cpp/georef_utils.hpp"

#include <cmath>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>

#include "GeographicLib/UTMUPS.hpp"
#include "tf2/LinearMath/Matrix3x3.h"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/exceptions.h"
#include "tf2/time.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

namespace
{

const std::regex kUtmFrame("^utm_([0-9]{1,2})_([C-HJ-NP-X])$");

// Same bands as geodesy.utm.gridZone. X is the wide band from 72 N to 84 N.
char latitude_band(double latitude)
{
  if (latitude < -80.0 || latitude > 84.0) {
    throw std::invalid_argument("latitude out of UTM range");
  }
  if (latitude >= 72.0) {
    return 'X';
  }
  static const char bands[] = "CDEFGHJKLMNPQRSTUVWX";
  const int index = static_cast<int>(std::floor((latitude + 80.0) / 8.0));
  return bands[index];
}

int longitude_zone(double longitude)
{
  if (longitude < -180.0 || longitude > 180.0) {
    throw std::invalid_argument("invalid longitude");
  }
  return static_cast<int>(std::floor((longitude + 180.0) / 6.0)) + 1;
}

bool match_utm_frame(const std::string & frame, int & zone, char & band)
{
  std::smatch match;
  if (!std::regex_match(frame, match, kUtmFrame)) {
    return false;
  }
  zone = std::stoi(match[1].str());
  if (zone < 1 || zone > 60) {
    return false;
  }
  band = match[2].str()[0];
  return true;
}

}  // namespace

GeorefUtils::GeorefUtils(rclcpp::Node * node)
{
  // TF. The listener subscribes through the node, but spins its subscriptions in its own
  // thread (spin_thread = true) instead of in the node's executor.
  tf_buffer_ = std::make_unique<tf2_ros::Buffer>(node->get_clock());
  tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_, node, true);
}

std::string GeorefUtils::get_utm_frame()
{
  return find_utm_frame().name;
}

geometry_msgs::msg::PointStamped GeorefUtils::geopoint_to_point_stamped(
  const geographic_msgs::msg::GeoPoint & geopoint,
  const std::string & target_frame)
{
  const UtmFrame utm_frame = find_utm_frame();
  const bool frame_northp = utm_frame.band >= 'N';

  // Force the zone of the utm frame, even if the point lies in a neighbouring zone.
  // zone, gamma and k are outputs required by Forward but not used.
  int zone;
  bool northp;
  double easting, northing, gamma, k;
  GeographicLib::UTMUPS::Forward(
    geopoint.latitude, geopoint.longitude, zone, northp,
    easting, northing, gamma, k, utm_frame.zone);

  // Express northing in the hemisphere convention of the utm frame
  if (northp && !frame_northp) {
    northing += GeographicLib::UTMUPS::UTMShift();
  } else if (!northp && frame_northp) {
    northing -= GeographicLib::UTMUPS::UTMShift();
  }

  geometry_msgs::msg::PointStamped point;
  point.header.frame_id = utm_frame.name;
  point.point.x = easting;
  point.point.y = northing;
  point.point.z = geopoint.altitude;

  if (target_frame.empty() || target_frame == utm_frame.name) {
    return point;
  }
  // Zero timestamp, so the latest transform is used
  return tf_buffer_->transform(point, target_frame);
}

geographic_msgs::msg::GeoPoint GeorefUtils::point_stamped_to_geopoint(
  const geometry_msgs::msg::PointStamped & point)
{
  const UtmFrame utm_frame = find_utm_frame();

  // In the utm frame x is easting and y is northing
  const auto utm_point = tf_buffer_->transform(point, utm_frame.name);

  const bool northp = utm_frame.band >= 'N';
  geographic_msgs::msg::GeoPoint geopoint;
  GeographicLib::UTMUPS::Reverse(
    utm_frame.zone, northp, utm_point.point.x, utm_point.point.y,
    geopoint.latitude, geopoint.longitude);
  geopoint.altitude = utm_point.point.z;
  return geopoint;
}

GeorefUtils::UtmFrame GeorefUtils::find_utm_frame()
{
  std::lock_guard<std::mutex> lock(mutex_);
  if (utm_frame_) {
    return *utm_frame_;
  }

  std::vector<UtmFrame> found;
  for (const auto & frame : tf_buffer_->getAllFrameNames()) {
    int zone;
    char band;
    if (!match_utm_frame(frame, zone, band)) {
      continue;
    }
    found.push_back(UtmFrame{frame, zone, band});
  }

  if (found.empty()) {
    throw tf2::LookupException("No utm_{zone}_{band} frame found in the tf tree");
  }
  if (found.size() > 1) {
    std::string names;
    for (const auto & utm_frame : found) {
      names += (names.empty() ? "" : ", ") + utm_frame.name;
    }
    throw tf2::TransformException("Multiple utm frames found in the tf tree: " + names);
  }
  utm_frame_ = found.front();
  return *utm_frame_;
}

geometry_msgs::msg::TransformStamped GeorefUtils::lookup_transform(
  const std::string & target_frame,
  const std::string & source_frame,
  double timeout_sec)
{
  return tf_buffer_->lookupTransform(
    target_frame, source_frame, tf2::TimePointZero,
    tf2::durationFromSec(timeout_sec));
}

bool GeorefUtils::can_transform(
  const std::string & target_frame,
  const std::string & source_frame,
  double timeout_sec)
{
  return tf_buffer_->canTransform(
    target_frame, source_frame, tf2::TimePointZero,
    tf2::durationFromSec(timeout_sec));
}

geometry_msgs::msg::PointStamped convert_latlon_to_utm(
  const geographic_msgs::msg::GeoPoint & geopoint)
{
  const int zone = longitude_zone(geopoint.longitude);
  const char band = latitude_band(geopoint.latitude);

  int forward_zone;
  bool northp;
  double easting;
  double northing;
  double gamma;
  double k;
  GeographicLib::UTMUPS::Forward(
    geopoint.latitude, geopoint.longitude, forward_zone, northp,
    easting, northing, gamma, k, zone);
  // geodesy.utm reports southern northing as negative. GeographicLib adds the
  // 10e6 false northing instead.
  if (!northp) {
    northing -= GeographicLib::UTMUPS::UTMShift();
  }

  geometry_msgs::msg::PointStamped point;
  point.header.frame_id = "utm_" + std::to_string(zone) + "_" + band;
  point.point.x = easting;
  point.point.y = northing;
  point.point.z = geopoint.altitude;
  return point;
}

geographic_msgs::msg::GeoPoint convert_utm_to_latlon(
  const geometry_msgs::msg::PointStamped & utm)
{
  int zone;
  char band;
  if (!match_utm_frame(utm.header.frame_id, zone, band)) {
    throw std::invalid_argument(
            "UTM frame_id must be utm_<zone>_<band>, got '" + utm.header.frame_id + "'");
  }

  const bool northp = band >= 'N';
  double northing = utm.point.y;
  if (!northp) {
    northing += GeographicLib::UTMUPS::UTMShift();
  }

  geographic_msgs::msg::GeoPoint geopoint;
  GeographicLib::UTMUPS::Reverse(
    zone, northp, utm.point.x, northing, geopoint.latitude, geopoint.longitude);
  geopoint.altitude = utm.point.z;
  return geopoint;
}

double convert_enu_pose_to_heading(const geometry_msgs::msg::Pose & enu_pose)
{
  const auto & q = enu_pose.orientation;
  tf2::Quaternion quat(q.x, q.y, q.z, q.w);
  double roll;
  double pitch;
  double yaw;
  tf2::Matrix3x3(quat).getRPY(roll, pitch, yaw);
  const double yaw_deg = yaw * (180.0 / std::acos(-1.0));
  double heading = std::fmod(90.0 - yaw_deg, 360.0);
  if (heading < 0.0) {
    heading += 360.0;
  }
  return heading;
}

namespace
{

double stamp_seconds(const builtin_interfaces::msg::Time & stamp)
{
  return static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1e-9;
}

double wrap_degrees(double degrees)
{
  double wrapped = std::fmod(degrees, 360.0);
  if (wrapped < 0.0) {
    wrapped += 360.0;
  }
  return wrapped;
}

}  // namespace

double compute_course_from_two_poses(
  const geometry_msgs::msg::PoseStamped & prev_pose,
  const geometry_msgs::msg::PoseStamped & current_pose)
{
  const double dx = current_pose.pose.position.x - prev_pose.pose.position.x;
  const double dy = current_pose.pose.position.y - prev_pose.pose.position.y;
  return wrap_degrees(std::atan2(dy, dx) * (180.0 / std::acos(-1.0)));
}

double compute_speed_from_two_poses(
  const geometry_msgs::msg::PoseStamped & prev_pose,
  const geometry_msgs::msg::PoseStamped & current_pose)
{
  const double dx = current_pose.pose.position.x - prev_pose.pose.position.x;
  const double dy = current_pose.pose.position.y - prev_pose.pose.position.y;
  const double dt = stamp_seconds(current_pose.header.stamp) - stamp_seconds(prev_pose.header.stamp);
  if (dt <= 0.0) {
    return 0.0;
  }
  return std::sqrt(dx * dx + dy * dy) / dt;
}
