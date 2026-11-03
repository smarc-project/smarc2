/* file: lolo_depth_move_to.cpp
 * description: auv_depth_move_to in c++
 * license: MIT
 */
#include <memory>
#include <string>
#include <cmath>

#include "lolo_msgs/msg/topics.hpp"
#include "smarc_msgs/msg/topics.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "std_msgs/msg/float32.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"
#include <geographic_msgs/msg/geo_point.hpp>
#include <geodesy/utm.h>

namespace auv_depth_move_to {

class AUVDepthMoveTo {
 public:
  explicit AUVDepthMoveTo(rclcpp::Node::SharedPtr node)
      : node_(std::move(node)),
        action_server_(
            node_, "auv_depth_move_to",
            std::bind(&AUVDepthMoveTo::on_goal_received, this,
                      std::placeholders::_1),
            std::bind(&AUVDepthMoveTo::on_cancel_received, this),
            std::bind(&AUVDepthMoveTo::prepare_loop, this),
            std::bind(&AUVDepthMoveTo::loop_inner, this),
            std::bind(&AUVDepthMoveTo::feedback, this),
            smarc_action_base_cpp::GentlerActionServer::Config(2.0)) 
  {
    //Limits for checking if goal is valid
    node_->declare_parameter("max_waypoint_dist", 1000.0);
    node_->declare_parameter("max_thruster_rpm", 1000.0);
    node_->declare_parameter("max_depth", 25.0);
    node_->declare_parameter("min_altitude", 0.0);
    node_->declare_parameter("max_timeout_secs", 3600.0);

    limits_max_waypoint_dist =
        node_->get_parameter("max_waypoint_dist").as_double();
    limits_max_thruster_rpm =
        node_->get_parameter("max_thruster_rpm").as_double();
    limits_max_depth =
        node_->get_parameter("max_depth").as_double();
    limits_min_altitude =
        node_->get_parameter("min_altitude").as_double();
    limits_max_timeout_secs =
        node_->get_parameter("max_timeout_secs").as_double();

    setpoint_wp_pub_ = node_->create_publisher<geometry_msgs::msg::PointStamped>(
        lolo_msgs::msg::Topics::WP_SETPOINT, 10);

    setpoint_depth_pub_ = node_->create_publisher<std_msgs::msg::Float32>(
        lolo_msgs::msg::Topics::DEPTH_SETPOINT, 10);

    setpoint_altitude_pub_ = node_->create_publisher<std_msgs::msg::Float32>(
        lolo_msgs::msg::Topics::ALTITUDE_SETPOINT, 10);

    setpoint_rpm_pub_ = node_->create_publisher<std_msgs::msg::Float32>(
        lolo_msgs::msg::Topics::RPM_SETPOINT, 10);

    feedback_odom_sub_ =
        node_->create_subscription<nav_msgs::msg::Odometry>(
            smarc_msgs::msg::Topics::ODOM_TOPIC, 10,
            std::bind(&AUVDepthMoveTo::odom_fb_sub_cb, this,
                      std::placeholders::_1));

    //initialize timers in the past to get the correct time source
    action_start_time_  = node_->get_clock()->now() - rclcpp::Duration::from_seconds(limits_max_timeout_secs + 1000);
    feedback_odom_received_time_  = node_->get_clock()->now() - rclcpp::Duration::from_seconds(100);

    //TF
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(node_->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
  }

  void request_shutdown() { action_server_.request_shutdown(); }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  bool on_goal_received(const Json& goal) {
    feedback_ = "IDLE";
    goal_json_ = goal.dump();
    RCLCPP_INFO(node_->get_logger(), "Received goal: %s",
                goal_json_.c_str());

    try{     
      bool failed_to_parse = false;
      
      if (!goal.contains("waypoint")) {
        RCLCPP_ERROR(node_->get_logger(), "Failed to parse goal ");
        return false;
      }

      Json waypoint = goal["waypoint"];

      geographic_msgs::msg::GeoPoint geopoint;

      if (waypoint.contains("latitude")) geopoint.latitude = (double) waypoint["latitude"]; else failed_to_parse = true;
      if (waypoint.contains("longitude")) geopoint.longitude = (double) waypoint["longitude"]; else failed_to_parse = true;
      if (waypoint.contains("target-depth")) {
        goal_depth_.data = (double) waypoint["target-depth"]; 
        geopoint.altitude = -goal_depth_.data;
      } else failed_to_parse = true;
      if (waypoint.contains("min-altitude")) goal_altitude_.data = (double) waypoint["min-altitude"]; else failed_to_parse = true;
      if (waypoint.contains("rpm")) goal_rpm_.data = (double) waypoint["rpm"]; else failed_to_parse = true;
      if (waypoint.contains("timeout")) goal_timeout_ = (int) waypoint["timeout"]; else failed_to_parse = true;
      if (waypoint.contains("tolerance")) goal_tolerance_ = (double) waypoint["tolerance"]; else goal_tolerance_ = 10;

      if(failed_to_parse) {
        RCLCPP_ERROR(node_->get_logger(), "Failed to parse goal ");
        return false;
      }

      if(goal_depth_.data > limits_max_depth) {
        RCLCPP_ERROR(node_->get_logger(), "Goal not allowed. Max depth too deep");
        return false;
      }

      if(goal_timeout_ < 0 || goal_timeout_ > limits_max_timeout_secs) {
        RCLCPP_ERROR(node_->get_logger(), "Timeout too large");
        return false;
      }

      if(goal_altitude_.data < limits_min_altitude ) {
        RCLCPP_WARN(node_->get_logger(), "Min altitude too small. Changing to minimum allowed");
        goal_altitude_.data = limits_min_altitude;
      }

      if(goal_rpm_.data > limits_max_thruster_rpm) {
        RCLCPP_WARN(node_->get_logger(), "Target Rpm too high. limiting to max allowed");
        goal_rpm_.data = limits_max_thruster_rpm;
      }

    
      geodesy::UTMPoint point;
      geodesy::fromMsg(geopoint, point);

      
      std::string frame_id =
          "utm_" + std::to_string(static_cast<int>(point.zone)) + "_" + std::string(1, point.band);

      RCLCPP_INFO_STREAM(node_->get_logger(), "Converted WP to utm point: " << point);
      
      geometry_msgs::msg::PointStamped point_in;
      point_in.header.frame_id = frame_id;
      point_in.header.stamp = rclcpp::Time(0);
      point_in.point.x = point.easting;
      point_in.point.y = point.northing;
      point_in.point.z = point.altitude;

      goal_ = tf_buffer_->transform(point_in, target_frame_, tf2::durationFromSec(1.0));

    } catch (const tf2::TransformException& ex) {
        RCLCPP_WARN(node_->get_logger(), "Could not transform to %s: %s",
          target_frame_.c_str(), ex.what());
        return false;
    }

    return true;
  }

  bool on_cancel_received() {
    feedback_ = "IDLE";
    return true;
  }

  void prepare_loop() {
    feedback_ = "IDLE";
    action_start_time_ = node_->get_clock()->now();
  }

  LoopStatus loop_inner() {
    std::lock_guard<std::mutex> lock(mutex_); //Prevent feedback from updating while checking timeouts

    rclcpp::Time now = node_->get_clock()->now();
    rclcpp::Duration runtime = now - action_start_time_;

    //Check for feedback timeout
    if(now - feedback_odom_received_time_ > rclcpp::Duration::from_seconds(5)) {
      RCLCPP_ERROR(node_->get_logger(), "No position feedback for 5s. Aborting ");
      feedback_ = "FAILURE";
      return LoopStatus::FAILURE;
    }

    //Check action timeout
    if(runtime > rclcpp::Duration::from_seconds(goal_timeout_)) {
      RCLCPP_ERROR(node_->get_logger(), "Action timeout reached ");
      feedback_ = "FAILURE";
      return LoopStatus::FAILURE;
    }

    //Check distance to goal
    double dx = goal_.point.x - robot_position_.pose.pose.position.x;
    double dy = goal_.point.y - robot_position_.pose.pose.position.y;
    double d = sqrt(dx*dx + dy*dy);

    if(d < goal_tolerance_) {
      RCLCPP_INFO(node_->get_logger(), "Success goal reached");
      feedback_ = "DONE";
      return LoopStatus::SUCCESS;
    }

    if(d > limits_max_waypoint_dist) {
      RCLCPP_INFO(node_->get_logger(), "Goal too far away");
      feedback_ = "ERROR";
      return LoopStatus::FAILURE;
    }

    feedback_ = "Distance to goal: " + 
                std::to_string((int)d) + "m" + 
                " total runtime: " + std::to_string((int) runtime.seconds()) + "s";
    
    //Publish setpoints
    setpoint_wp_pub_->publish(goal_);
    setpoint_depth_pub_->publish(goal_depth_);
    setpoint_altitude_pub_->publish(goal_altitude_);
    setpoint_rpm_pub_->publish(goal_rpm_);

    return LoopStatus::RUNNING;
  }

  std::string feedback() const {
    RCLCPP_INFO(node_->get_logger(), "%s", feedback_.c_str());
    return feedback_; 
  }

   void odom_fb_sub_cb(const nav_msgs::msg::Odometry::SharedPtr msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    feedback_odom_received_time_ = node_->get_clock()->now();
    robot_position_ = *msg;
    //Update target frame to the same as feedback
    target_frame_ = robot_position_.header.frame_id;
  }


  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;
  std::mutex mutex_; //Only one thread is allowed to access variables at a time

  rclcpp::Publisher<geometry_msgs::msg::PointStamped>::SharedPtr setpoint_wp_pub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr setpoint_depth_pub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr setpoint_altitude_pub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr setpoint_rpm_pub_;

  rclcpp::Time feedback_odom_received_time_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr feedback_odom_sub_;

  nav_msgs::msg::Odometry robot_position_;
  geometry_msgs::msg::PointStamped goal_;
  std_msgs::msg::Float32 goal_depth_;
  std_msgs::msg::Float32 goal_altitude_;
  std_msgs::msg::Float32 goal_rpm_;
  float goal_tolerance_;
  int goal_timeout_;
  std::string target_frame_ = "lolo/odom";

  rclcpp::Time action_start_time_;
  double limits_max_waypoint_dist;
  double limits_max_thruster_rpm;
  double limits_max_depth;
  double limits_min_altitude;
  double limits_max_timeout_secs;

  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  std::string goal_json_;
  std::string feedback_ = "IDLE";
};

}  // namespace 

int main(int argc, char** argv) {
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("lolo_auv_depth_move_to");
  auto action = std::make_shared<auv_depth_move_to::AUVDepthMoveTo>(node);

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);

  smarc_action_base_cpp::spin_with_graceful_shutdown(
      executor, [&action]() { action->request_shutdown(); });

  executor.remove_node(node);
  action.reset();
  node.reset();

  rclcpp::shutdown();
  return 0;
}
