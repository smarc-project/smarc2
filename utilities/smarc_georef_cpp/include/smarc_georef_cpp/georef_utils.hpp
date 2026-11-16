#ifndef SMARC_GEOREF_CPP__GEOREF_UTILS_HPP_
#define SMARC_GEOREF_CPP__GEOREF_UTILS_HPP_

#include <memory>
#include <mutex>
#include <optional>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "geographic_msgs/msg/geo_point.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"

// Helper for converting between lat lon and frames in the tf tree. Create it as a member of
// the node that uses it, e.g. GeorefUtils georef_(this). It uses the node's clock (so
// use_sim_time works) and receives tf on its own background thread, so its functions can be
// called with a timeout from the node's callbacks. The node must outlive it.
class GeorefUtils
{
public:
  explicit GeorefUtils(rclcpp::Node * node);

  // Name of the top level utm frame in the tf tree, e.g. "utm_33_V". Cached after the first
  // successful lookup. Throws tf2::LookupException if there is none (e.g. no transforms
  // received yet) and tf2::TransformException if there are several.
  std::string get_utm_frame();

  // GeoPoint to PointStamped in target_frame (the utm frame if empty). Altitude is copied to z
  // in the utm frame. The transform to target_frame uses the latest available transform.
  // Throws tf2::TransformException if there is no utm frame or more than one, or the transform
  // to target_frame is not available.
  geometry_msgs::msg::PointStamped geopoint_to_point_stamped(
    const geographic_msgs::msg::GeoPoint & geopoint,
    const std::string & target_frame = "");

  // PointStamped in any frame to GeoPoint. The point is transformed to the utm frame using the
  // timestamp in its header (zero means latest). z is copied to altitude. Throws
  // tf2::TransformException if there is no utm frame or more than one, or the transform to the
  // utm frame is not available.
  geographic_msgs::msg::GeoPoint point_stamped_to_geopoint(
    const geometry_msgs::msg::PointStamped & point);

  // Latest tf transform from source_frame to target_frame, waiting up to timeout_sec for it.
  // Throws tf2::TransformException if it is not available in time.
  geometry_msgs::msg::TransformStamped lookup_transform(
    const std::string & target_frame,
    const std::string & source_frame,
    double timeout_sec = 0.0);

  // Whether the latest tf transform from source_frame to target_frame is available, waiting up
  // to timeout_sec for it. Never throws.
  bool can_transform(
    const std::string & target_frame,
    const std::string & source_frame,
    double timeout_sec = 0.0);

private:
  struct UtmFrame
  {
    std::string name;  // e.g. "utm_33_V"
    int zone;          // 1-60
    char band;         // C-X, excluding I and O
  };

  // Find the frame named utm_{zone}_{band} among the frames currently in the tf buffer.
  // The result is cached after the first successful lookup.
  // Throws tf2::LookupException if there is none (e.g. no transforms received yet)
  // and tf2::TransformException if there are several.
  UtmFrame find_utm_frame();

  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::unique_ptr<tf2_ros::TransformListener> tf_listener_;
  std::optional<UtmFrame> utm_frame_;  // Cached by find_utm_frame()
  std::mutex mutex_;  // Only one thread is allowed to access variables at a time
};

#endif  // SMARC_GEOREF_CPP__GEOREF_UTILS_HPP_
