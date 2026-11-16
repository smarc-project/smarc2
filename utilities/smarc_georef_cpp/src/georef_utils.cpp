#include "smarc_georef_cpp/georef_utils.hpp"

#include <regex>
#include <vector>

#include "GeographicLib/UTMUPS.hpp"
#include "tf2/exceptions.h"
#include "tf2/time.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

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
  static const std::regex utm_regex("^utm_([0-9]{1,2})_([C-HJ-NP-X])$");

  std::lock_guard<std::mutex> lock(mutex_);
  if (utm_frame_) {
    return *utm_frame_;
  }

  std::vector<UtmFrame> found;
  for (const auto & frame : tf_buffer_->getAllFrameNames()) {
    std::smatch match;
    if (!std::regex_match(frame, match, utm_regex)) {
      continue;
    }
    const int zone = std::stoi(match[1].str());
    if (zone < 1 || zone > 60) {
      continue;
    }
    found.push_back(UtmFrame{frame, zone, match[2].str()[0]});
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
