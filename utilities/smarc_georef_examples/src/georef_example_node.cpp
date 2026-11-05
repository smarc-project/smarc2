// Example of using GeorefUtils from a C++ node.
//
// Once a second it runs three separate examples:
//   1. Convert a hard coded GeoPoint to a PointStamped in lolo/base_link
//   2. Convert a hard coded PointStamped in lolo/base_link to a GeoPoint
//   3. Get the transform from lolo/base_link to lolo/odom
//
//   ros2 run smarc_georef_examples georef_example_node

#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp/create_timer.hpp"
#include "geographic_msgs/msg/geo_point.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "tf2/exceptions.h"

#include "smarc_georef_cpp/georef_utils.hpp"

class GeorefExampleNode : public rclcpp::Node
{
public:
  GeorefExampleNode()
  : Node("georef_example_node"), georef_(this)
  {
    // Uses the node's clock, so it follows sim time when use_sim_time is set
    timer_ = rclcpp::create_timer(
      this, this->get_clock(), rclcpp::Duration::from_seconds(1.0),
      [this]() {timer_callback();});
  }

private:
  void timer_callback()
  {
    geopoint_to_vehicle_frame();
    vehicle_frame_to_geopoint();
    base_link_to_odom_transform();
  }

  // 1. GeoPoint -> PointStamped in lolo/base_link
  void geopoint_to_vehicle_frame()
  {
    geographic_msgs::msg::GeoPoint geopoint;
    geopoint.latitude = 59.35;
    geopoint.longitude = 18.07;
    geopoint.altitude = 0.0;

    try {
      const auto point = georef_.geopoint_to_point_stamped(geopoint, "lolo/base_link");
      RCLCPP_INFO(
        this->get_logger(), "1. GeoPoint (%.7f, %.7f) -> %s (%.2f, %.2f, %.2f)",
        geopoint.latitude, geopoint.longitude, point.header.frame_id.c_str(),
        point.point.x, point.point.y, point.point.z);
    } catch (const tf2::TransformException & e) {
      // Happens until the utm frame and lolo/base_link have been received over tf
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 5000, "1. Not ready: %s", e.what());
    }
  }

  // 2. PointStamped in lolo/base_link -> GeoPoint
  void vehicle_frame_to_geopoint()
  {
    geometry_msgs::msg::PointStamped point;
    point.header.frame_id = "lolo/base_link";
    point.point.x = 10.0;  // 10 m ahead of the vehicle

    try {
      const auto geopoint = georef_.point_stamped_to_geopoint(point);
      RCLCPP_INFO(
        this->get_logger(), "2. %s (%.2f, %.2f, %.2f) -> GeoPoint (%.7f, %.7f, %.2f)",
        point.header.frame_id.c_str(), point.point.x, point.point.y, point.point.z,
        geopoint.latitude, geopoint.longitude, geopoint.altitude);
    } catch (const tf2::TransformException & e) {
      // Happens until the utm frame and lolo/base_link have been received over tf
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 5000, "2. Not ready: %s", e.what());
    }
  }

  // 3. Transform from lolo/base_link to lolo/odom, i.e. the vehicle pose in lolo/odom
  void base_link_to_odom_transform()
  {
    try {
      const auto tf = georef_.lookup_transform("lolo/odom", "lolo/base_link");
      const auto & t = tf.transform.translation;
      RCLCPP_INFO(
        this->get_logger(), "3. lolo/base_link in lolo/odom: (%.2f, %.2f, %.2f)",
        t.x, t.y, t.z);
    } catch (const tf2::TransformException & e) {
      // Happens until lolo/odom and lolo/base_link have been received over tf
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 5000, "3. Not ready: %s", e.what());
    }
  }

  GeorefUtils georef_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GeorefExampleNode>());
  rclcpp::shutdown();
  return 0;
}
