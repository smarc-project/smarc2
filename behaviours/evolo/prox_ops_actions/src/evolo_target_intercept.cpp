/* file: evolo_target_intercept.cpp
 * description: A meaningful description will be added here. 
 * license: MIT
 */
#include <memory>
#include <string>
#include <cmath>

#include "evolo_msgs/msg/prox_ops_backend_status.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"
#include "smarc_msgs/msg/geofence_polygons_stamped.hpp"
#include "smarc_msgs/msg/geofence_status_stamped.hpp"
#include "smarc_geofence_utils/geofence_path_checker.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"

namespace prox_ops_actions {

class EvoloTargetIntercept {
 public:
  explicit EvoloTargetIntercept(rclcpp::Node::SharedPtr node)
      : node_(std::move(node)),
        action_server_(
            node_, "evolo_target_intercept",
            std::bind(&EvoloTargetIntercept::on_goal_received, this,
                      std::placeholders::_1),
            std::bind(&EvoloTargetIntercept::on_cancel_received, this),
            std::bind(&EvoloTargetIntercept::prepare_loop, this),
            std::bind(&EvoloTargetIntercept::loop_inner, this),
            std::bind(&EvoloTargetIntercept::feedback, this),
            smarc_action_base_cpp::GentlerActionServer::Config(
                /*loop_frequency_hz=*/10.0)) {

    node_->declare_parameter("backend_status_max_age_s", 2.0);
    node_->declare_parameter("candidate_path_max_age_s", 2.0);
    node_->declare_parameter("backend_twist_max_age_s", 1.0);
    node_->declare_parameter("yaw_integration_time_s", 1.0);
    node_->declare_parameter("geofence_check_enabled", false);
    node_->declare_parameter("geofence_status_max_age_s", 2.0);
    node_->declare_parameter("geofence_polygons_max_age_s", 10.0);
    node_->declare_parameter("odom_max_age_s", 1.0);

    backend_status_max_age_s_ =
        node_->get_parameter("backend_status_max_age_s").as_double();
    candidate_path_max_age_s_ =
        node_->get_parameter("candidate_path_max_age_s").as_double();
    backend_twist_max_age_s_ =
        node_->get_parameter("backend_twist_max_age_s").as_double();
    yaw_integration_time_s_ =
        node_->get_parameter("yaw_integration_time_s").as_double();
    default_geofence_check_enabled_ =
        node_->get_parameter("geofence_check_enabled").as_bool();
    geofence_check_enabled_ = default_geofence_check_enabled_;
    geofence_status_max_age_s_ =
        node_->get_parameter("geofence_status_max_age_s").as_double();
    geofence_polygons_max_age_s_ =
        node_->get_parameter("geofence_polygons_max_age_s").as_double();
    odom_max_age_s_ =
        node_->get_parameter("odom_max_age_s").as_double();

    // TODO: We should find out a way to add the evolo_msgs/Topics names in here
    // to avoid hard-coding them.
    ctrl_odom_pub_ = node_->create_publisher<nav_msgs::msg::Odometry>(
        "ctrl/control_planned", 10);

    backend_status_sub_ =
        node_->create_subscription<evolo_msgs::msg::ProxOpsBackendStatus>(
            "backend/status", 10,
            std::bind(&EvoloTargetIntercept::backend_status_cb, this,
                      std::placeholders::_1));
    target_state_sub_ = node_->create_subscription<nav_msgs::msg::Odometry>(
        "backend/target_state", 10,
        std::bind(&EvoloTargetIntercept::target_state_cb, this,
                  std::placeholders::_1));
    candidate_path_sub_ = node_->create_subscription<nav_msgs::msg::Path>(
        "backend/candidate_path", 10,
        std::bind(&EvoloTargetIntercept::candidate_path_cb, this,
                  std::placeholders::_1));
    backend_twist_sub_ =
        node_->create_subscription<geometry_msgs::msg::TwistStamped>(
            "backend/twist_planned", 10,
            std::bind(&EvoloTargetIntercept::backend_twist_cb, this,
                      std::placeholders::_1));
    geofence_status_sub_ =
        node_->create_subscription<smarc_msgs::msg::GeofenceStatusStamped>(
            "smarc/geofence_status", 10,
            std::bind(&EvoloTargetIntercept::geofence_status_cb, this,
                      std::placeholders::_1));
    geofence_polygons_sub_ =
        node_->create_subscription<smarc_msgs::msg::GeofencePolygonsStamped>(
            "smarc/geofence_polygons", 10,
            std::bind(&EvoloTargetIntercept::geofence_polygons_cb, this,
                      std::placeholders::_1));
    odom_sub_ = node_->create_subscription<nav_msgs::msg::Odometry>(
        "smarc/odom", 10,
        std::bind(&EvoloTargetIntercept::odom_cb, this,
                  std::placeholders::_1));
  }

  void request_shutdown() {
    action_server_.request_shutdown();
  }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  bool on_goal_received(const Json& goal) {
    reset_backend_cache();
    goal_json_ = goal.dump();

    if (!parse_geofence_goal_override(goal)) {
      return false;
    }

    RCLCPP_INFO(node_->get_logger(),
                "Received intercept goal: %s. geofence_check_enabled=%s",
                goal_json_.c_str(),
                geofence_check_enabled_ ? "true" : "false");
    return true;
  }

  bool on_cancel_received() {
    reset_backend_cache();
    geofence_check_enabled_ = default_geofence_check_enabled_;
    return true;
  }

  void prepare_loop() {
    reset_backend_cache();
    action_start_time_ = node_->get_clock()->now();
    has_action_start_time_ = true;
  }

  LoopStatus loop_inner() {
    if (!msg_is_fresh(last_status_, backend_status_max_age_s_)) {
      feedback_ = "WAITING_FOR_BACKEND_STATUS";
      return LoopStatus::RUNNING;
    }

    if (!msg_is_fresh(last_odom_, odom_max_age_s_)) {
      feedback_ = "WAITING_FOR_ODOMETRY";
      return LoopStatus::RUNNING;
    }

    if (!odom_orientation_is_valid(*last_odom_)) {
      feedback_ = "ODOM_ORIENTATION_INVALID";
      return LoopStatus::RUNNING;
    }

    const auto& status = *last_status_;
    feedback_ = status.status_text.empty() ? "BACKEND_STATUS_RECEIVED"
                                           : status.status_text;

    // Return FAILURE if we've lost the target so the BT goes back to patrol.
    if (status.target_lost) {
      feedback_ = "BACKEND_LOST_THE_TARGET!";
      return LoopStatus::FAILURE;
    }

    if (status.plan_available) {
      if (!candidate_control_is_safe_to_forward()) {
        return LoopStatus::FAILURE;
      }
      // Compute the absolute yaw control setpoint here.
      ctrl_odom_pub_->publish(
          make_control_setpoint(*last_backend_twist_, *last_odom_));
      feedback_ = "FORWARDING_BACKEND_CONTROL";
    }

    return LoopStatus::RUNNING;
  }

  std::string feedback() const { return feedback_; }

  nav_msgs::msg::Odometry make_control_setpoint(
      const geometry_msgs::msg::TwistStamped& twist,
      const nav_msgs::msg::Odometry& odom) {
    const double current_yaw = yaw_from_quaternion(odom.pose.pose.orientation);
    const double delta_yaw = twist.twist.angular.z * yaw_integration_time_s_;
    const double target_yaw = wrap_to_pi(current_yaw + delta_yaw);

    nav_msgs::msg::Odometry control;
    control.header.stamp = node_->get_clock()->now();
    control.header.frame_id = odom.header.frame_id;
    control.child_frame_id = odom.child_frame_id;

    control.pose.pose = odom.pose.pose;
    control.pose.pose.orientation = quaternion_from_yaw(target_yaw);
    control.twist.twist.linear = twist.twist.linear;
    control.twist.twist.angular.z = 0.0;

    return control;
  }

  double yaw_from_quaternion(
      const geometry_msgs::msg::Quaternion& quaternion) const {
    const double siny_cosp =
        2.0 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y);
    const double cosy_cosp =
        1.0 - 2.0 * (quaternion.y * quaternion.y +
                     quaternion.z * quaternion.z);
    return std::atan2(siny_cosp, cosy_cosp);
  }

  geometry_msgs::msg::Quaternion quaternion_from_yaw(double yaw) const {
    geometry_msgs::msg::Quaternion quaternion;
    quaternion.x = 0.0;
    quaternion.y = 0.0;
    quaternion.z = std::sin(yaw * 0.5);
    quaternion.w = std::cos(yaw * 0.5);
    return quaternion;
  }

  double wrap_to_pi(double angle) const {
    return std::atan2(std::sin(angle), std::cos(angle));
  }

  bool odom_orientation_is_valid(const nav_msgs::msg::Odometry& odom) const {
    const auto& q = odom.pose.pose.orientation;
    const double norm_squared =
        q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w;
    return std::isfinite(q.x) && std::isfinite(q.y) && std::isfinite(q.z) &&
           std::isfinite(q.w) && norm_squared > 1e-12;
  }

  bool parse_geofence_goal_override(const Json& goal) {
    geofence_check_enabled_ = default_geofence_check_enabled_;

    if (!goal.contains("geofence_check_enabled")) {
      return true;
    }

    const auto& geofence_check_enabled = goal.at("geofence_check_enabled");
    if (!geofence_check_enabled.is_boolean()) {
      feedback_ = "INVALID_GEOFENCE_CHECK_ENABLED";
      RCLCPP_ERROR(
          node_->get_logger(),
          "Rejecting intercept goal; geofence_check_enabled must be boolean.");
      return false;
    }

    geofence_check_enabled_ = geofence_check_enabled.get<bool>();
    return true;
  }

  void backend_status_cb(
      const evolo_msgs::msg::ProxOpsBackendStatus::SharedPtr msg) {
    last_status_ = msg;
  }

  void target_state_cb(const nav_msgs::msg::Odometry::SharedPtr msg) {
    last_target_state_ = msg;
  }

  void candidate_path_cb(const nav_msgs::msg::Path::SharedPtr msg) {
    last_candidate_path_ = msg;
  }

  void backend_twist_cb(const geometry_msgs::msg::TwistStamped::SharedPtr msg) {
    last_backend_twist_ = msg;
  }

  void geofence_status_cb(
      const smarc_msgs::msg::GeofenceStatusStamped::SharedPtr msg) {
    last_geofence_status_ = msg;
  }

  void geofence_polygons_cb(
      const smarc_msgs::msg::GeofencePolygonsStamped::SharedPtr msg) {
    last_geofence_polygons_ = msg;
  }

  void odom_cb(const nav_msgs::msg::Odometry::SharedPtr msg) {
    last_odom_ = msg;
  }

  bool candidate_control_is_safe_to_forward() {
    // Freshness requirements.
    if (!msg_is_fresh(last_candidate_path_, candidate_path_max_age_s_)) {
      feedback_ = "CANDIDATE_PATH_STALE";
      return false;
    }

    if (!msg_is_fresh(last_backend_twist_, backend_twist_max_age_s_)) {
      feedback_ = "BACKEND_TWIST_STALE";
      return false;
    }

    // Syntax requirements.
    if (!candidate_path_is_valid(*last_candidate_path_)) {
      return false;
    }

    if (!backend_twist_is_valid(*last_backend_twist_)) {
      return false;
    }

    if (!candidate_path_is_geofence_safe(*last_candidate_path_)) {
      return false;
    }

    return true;
  }

  bool candidate_path_is_valid(const nav_msgs::msg::Path& path) {
    if (path.header.frame_id.empty()) {
      feedback_ = "CANDIDATE_PATH_MISSING_FRAME";
      return false;
    }

    if (path.poses.empty()) {
      feedback_ = "CANDIDATE_PATH_EMPTY";
      return false;
    }

    for (const auto& pose : path.poses) {
      if (!pose.header.frame_id.empty() &&
          pose.header.frame_id != path.header.frame_id) {
        feedback_ = "CANDIDATE_PATH_INCONSISTENT_FRAMES";
        return false;
      }
    }

    return true;
  }

  bool backend_twist_is_valid(const geometry_msgs::msg::TwistStamped& twist) {
    if (twist.header.frame_id.empty()) {
      feedback_ = "BACKEND_TWIST_MISSING_FRAME";
      return false;
    }

    return true;
  }

  bool candidate_path_is_geofence_safe(const nav_msgs::msg::Path& path) {
    if (!geofence_check_enabled_) {
      return true;
    }

    if (!geofence_status_is_fresh()) {
      feedback_ = "GEOFENCE_STATUS_STALE";
      return false;
    }

    if (last_geofence_status_->status !=
        smarc_msgs::msg::GeofenceStatusStamped::STATUS_INSIDE) {
      feedback_ = "GEOFENCE_STATUS_NOT_INSIDE";
      return false;
    }

    if (!msg_is_fresh(last_geofence_polygons_, geofence_polygons_max_age_s_)) {
      feedback_ = "GEOFENCE_POLYGONS_STALE";
      return false;
    }

    const auto result = smarc_geofence_utils::check_path_against_geofence(
        path, *last_geofence_polygons_);
    if (!result.safe) {
      feedback_ = result.feedback;
      return false;
    }

    return true;
  }

  template <typename MsgT>
  bool msg_is_fresh(const std::shared_ptr<MsgT>& msg, double max_age_s) const {
    if (!msg) {
      return false;
    }

    const rclcpp::Time stamp(msg->header.stamp,
                             node_->get_clock()->get_clock_type());
    if (stamp.nanoseconds() == 0) {
      return false;
    }

    if (has_action_start_time_ && stamp < action_start_time_) {
      return false;
    }

    const auto age_s = (node_->get_clock()->now() - stamp).seconds();
    return age_s >= 0.0 && age_s <= max_age_s;
  }

  bool geofence_status_is_fresh() const {
    if (!last_geofence_status_) {
      return false;
    }

    const rclcpp::Time stamp(last_geofence_status_->time,
                             node_->get_clock()->get_clock_type());
    if (stamp.nanoseconds() == 0) {
      return false;
    }

    const auto age_s = (node_->get_clock()->now() - stamp).seconds();
    return age_s >= 0.0 && age_s <= geofence_status_max_age_s_;
  }

  void reset_backend_cache() {
    last_status_.reset();
    last_target_state_.reset();
    last_candidate_path_.reset();
    last_backend_twist_.reset();
    last_geofence_status_.reset();
    last_geofence_polygons_.reset();
    last_odom_.reset();
    has_action_start_time_ = false;
    feedback_ = "IDLE";
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ctrl_odom_pub_;
  rclcpp::Subscription<evolo_msgs::msg::ProxOpsBackendStatus>::SharedPtr
      backend_status_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr target_state_sub_;
  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr candidate_path_sub_;
  rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr
      backend_twist_sub_;
  rclcpp::Subscription<smarc_msgs::msg::GeofenceStatusStamped>::SharedPtr
      geofence_status_sub_;
  rclcpp::Subscription<smarc_msgs::msg::GeofencePolygonsStamped>::SharedPtr
      geofence_polygons_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

  evolo_msgs::msg::ProxOpsBackendStatus::SharedPtr last_status_;
  nav_msgs::msg::Odometry::SharedPtr last_target_state_;
  nav_msgs::msg::Path::SharedPtr last_candidate_path_;
  geometry_msgs::msg::TwistStamped::SharedPtr last_backend_twist_;
  smarc_msgs::msg::GeofenceStatusStamped::SharedPtr last_geofence_status_;
  smarc_msgs::msg::GeofencePolygonsStamped::SharedPtr last_geofence_polygons_;
  nav_msgs::msg::Odometry::SharedPtr last_odom_;

  rclcpp::Time action_start_time_;
  bool has_action_start_time_ = false;
  double backend_status_max_age_s_ = 2.0;
  double candidate_path_max_age_s_ = 2.0;
  double backend_twist_max_age_s_ = 1.0;
  double yaw_integration_time_s_ = 1.0;
  bool default_geofence_check_enabled_ = false;
  bool geofence_check_enabled_ = false;
  double geofence_status_max_age_s_ = 2.0;
  double geofence_polygons_max_age_s_ = 10.0;
  double odom_max_age_s_ = 1.0;

  std::string goal_json_;
  std::string feedback_ = "IDLE";
};

}  // namespace prox_ops_actions

int main(int argc, char** argv) {
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("evolo_target_intercept_node");
  auto action = std::make_shared<prox_ops_actions::EvoloTargetIntercept>(node);

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
