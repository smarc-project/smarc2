/* file: evolo_target_inspect.cpp
 * description: Target inspection action for Evolo prox-ops BT.
 * license: MIT
 */
#include <memory>
#include <string>
#include <cmath>

#include "evolo_msgs/msg/prox_ops_backend_status.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"

namespace prox_ops_actions {

class EvoloTargetInspect {
 public:
  explicit EvoloTargetInspect(rclcpp::Node::SharedPtr node)
      : node_(std::move(node)),
        action_server_(
            node_, "evolo_target_inspect",
            std::bind(&EvoloTargetInspect::on_goal_received, this,
                      std::placeholders::_1),
            std::bind(&EvoloTargetInspect::on_cancel_received, this),
            std::bind(&EvoloTargetInspect::prepare_loop, this),
            std::bind(&EvoloTargetInspect::loop_inner, this),
            std::bind(&EvoloTargetInspect::feedback, this),
            smarc_action_base_cpp::GentlerActionServer::Config(10.0)) {
    node_->declare_parameter("backend_status_max_age_s", 2.0);
    node_->declare_parameter("candidate_path_max_age_s", 2.0);
    node_->declare_parameter("backend_control_max_age_s", 1.0);

    backend_status_max_age_s_ =
        node_->get_parameter("backend_status_max_age_s").as_double();
    candidate_path_max_age_s_ =
        node_->get_parameter("candidate_path_max_age_s").as_double();
    backend_control_max_age_s_ =
        node_->get_parameter("backend_control_max_age_s").as_double();

    ctrl_odom_pub_ = node_->create_publisher<nav_msgs::msg::Odometry>(
        "ctrl/control_planned", 10);

    backend_status_sub_ =
        node_->create_subscription<evolo_msgs::msg::ProxOpsBackendStatus>(
            "backend/status", 10,
            std::bind(&EvoloTargetInspect::backend_status_cb, this,
                      std::placeholders::_1));
    candidate_path_sub_ = node_->create_subscription<nav_msgs::msg::Path>(
        "backend/candidate_path", 10,
        std::bind(&EvoloTargetInspect::candidate_path_cb, this,
                  std::placeholders::_1));
    backend_control_sub_ =
        node_->create_subscription<nav_msgs::msg::Odometry>(
            "backend/control_planned", 10,
            std::bind(&EvoloTargetInspect::backend_control_cb, this,
                      std::placeholders::_1));
  }

  void request_shutdown() { action_server_.request_shutdown(); }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  bool on_goal_received(const Json& goal) {
    reset_backend_cache();
    goal_json_ = goal.dump();
    RCLCPP_INFO(node_->get_logger(), "Received target inspect goal: %s",
                goal_json_.c_str());
    return true;
  }

  bool on_cancel_received() {
    reset_backend_cache();
    return true;
  }

  void prepare_loop() {
    reset_backend_cache();
    action_start_time_ = node_->get_clock()->now();
    has_action_start_time_ = true;
  }

  LoopStatus loop_inner() {
    if (!msg_is_fresh(last_status_, backend_status_max_age_s_)) {
      // feedback_ = "BACKEND_STATUS_STALE!";
      feedback_ = "WAITING_FOR_BACKEND_STATUS";
      return LoopStatus::RUNNING;
    }

    const auto& status = *last_status_;
    feedback_ = status.status_text.empty() ? "BACKEND_STATUS_RECEIVED"
                                           : status.status_text;

    if (status.target_lost) {
      feedback_ = "BACKEND_LOST_THE_TARGET!";
      return LoopStatus::FAILURE;
    }

    if (status.plan_available) {
      if (!candidate_control_is_safe_to_forward()) {
        return LoopStatus::FAILURE;
      }

      ctrl_odom_pub_->publish(*last_backend_control_);
      feedback_ = "FORWARDING_BACKEND_CONTROL";
    }

    return LoopStatus::RUNNING;
  }

  std::string feedback() const { return feedback_; }

  void backend_status_cb(
      const evolo_msgs::msg::ProxOpsBackendStatus::SharedPtr msg) {
    last_status_ = msg;
  }

  void candidate_path_cb(const nav_msgs::msg::Path::SharedPtr msg) {
    last_candidate_path_ = msg;
  }

  void backend_control_cb(const nav_msgs::msg::Odometry::SharedPtr msg) {
    last_backend_control_ = msg;
  }

  bool candidate_control_is_safe_to_forward() {
    if (!msg_is_fresh(last_candidate_path_, candidate_path_max_age_s_)) {
      feedback_ = "CANDIDATE_PATH_STALE";
      return false;
    }

    if (!msg_is_fresh(last_backend_control_, backend_control_max_age_s_)) {
      feedback_ = "BACKEND_CONTROL_STALE";
      return false;
    }

    if (!candidate_path_is_valid(*last_candidate_path_)) {
      return false;
    }

    if (!backend_control_is_valid(*last_backend_control_)) {
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

  bool backend_control_is_valid(const nav_msgs::msg::Odometry& control) {
    if (control.header.frame_id.empty()) {
      feedback_ = "BACKEND_CONTROL_MISSING_FRAME";
      return false;
    }
    const auto& q = control.pose.pose.orientation;
    const double norm_sq =
        q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w;
    if (!std::isfinite(q.x) || !std::isfinite(q.y) ||
        !std::isfinite(q.z) || !std::isfinite(q.w) || norm_sq < 1e-12) {
      feedback_ = "BACKEND_CONTROL_INVALID_ORIENTATION";
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

  void reset_backend_cache() {
    last_status_.reset();
    last_candidate_path_.reset();
    last_backend_control_.reset();
    has_action_start_time_ = false;
    feedback_ = "IDLE";
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ctrl_odom_pub_;
  rclcpp::Subscription<evolo_msgs::msg::ProxOpsBackendStatus>::SharedPtr
      backend_status_sub_;
  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr candidate_path_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr backend_control_sub_;

  evolo_msgs::msg::ProxOpsBackendStatus::SharedPtr last_status_;
  nav_msgs::msg::Path::SharedPtr last_candidate_path_;
  nav_msgs::msg::Odometry::SharedPtr last_backend_control_;

  rclcpp::Time action_start_time_;
  bool has_action_start_time_ = false;
  double backend_status_max_age_s_ = 2.0;
  double candidate_path_max_age_s_ = 2.0;
  double backend_control_max_age_s_ = 1.0;

  std::string goal_json_;
  std::string feedback_ = "IDLE";
};

}  // namespace prox_ops_actions

int main(int argc, char** argv) {
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("evolo_target_inspect_node");
  auto action = std::make_shared<prox_ops_actions::EvoloTargetInspect>(node);

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
