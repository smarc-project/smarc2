/* file: evolo_target_intercept.cpp
 * description: 
 * license: MIT
 */
#include <memory>
#include <string>

#include "evolo_msgs/msg/prox_ops_backend_status.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"
#include "std_msgs/msg/string.hpp"

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

    // TODO: We should find out a way to add the evolo_msgs/Topics names in here
    // to avoid hard-coding them.
    backend_command_pub_ =
        node_->create_publisher<std_msgs::msg::String>("backend/command", 10);

    ctrl_twist_pub_ = node_->create_publisher<geometry_msgs::msg::TwistStamped>(
        "ctrl/twist_planned", 10);

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
  }

  void request_shutdown() {
    publish_backend_command("STOP", "action_server_shutdown");
    action_server_.request_shutdown();
  }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  bool on_goal_received(const Json& goal) {
    goal_json_ = goal.dump();
    RCLCPP_INFO(node_->get_logger(), "Received intercept goal: %s",
                goal_json_.c_str());
    return true;
  }

  bool on_cancel_received() {
    publish_backend_command("STOP", "action_cancelled");
    return true;
  }

  void prepare_loop() { publish_backend_command("START", "action_started"); }

  LoopStatus loop_inner() {
    if (!last_status_) {
      feedback_ = "WAITING_FOR_BACKEND_STATUS";
      return LoopStatus::RUNNING;
    }

    const auto& status = *last_status_;
    feedback_ = status.status_text.empty() ? "BACKEND_STATUS_RECEIVED"
                                           : status.status_text;

    if (status.health == evolo_msgs::msg::ProxOpsBackendStatus::HEALTH_ERROR) {
      publish_backend_command("STOP", "backend_health_error");
      return LoopStatus::FAILURE;
    }

    if (status.intercept_success) {
      publish_backend_command("STOP", "intercept_success");
      return LoopStatus::SUCCESS;
    }

    if (status.plan_available && last_candidate_path_ && last_backend_twist_) {
      ctrl_twist_pub_->publish(*last_backend_twist_);
      feedback_ = "FORWARDING_BACKEND_TWIST";
    }

    return LoopStatus::RUNNING;
  }

  std::string feedback() const { return feedback_; }

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

  void publish_backend_command(const std::string& command,
                               const std::string& reason) {
    std_msgs::msg::String msg;
    msg.data =
        "{\"command\":\"" + command + "\",\"reason\":\"" + reason + "\"}";
    backend_command_pub_->publish(msg);
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr backend_command_pub_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr
      ctrl_twist_pub_;
  rclcpp::Subscription<evolo_msgs::msg::ProxOpsBackendStatus>::SharedPtr
      backend_status_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr target_state_sub_;
  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr candidate_path_sub_;
  rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr
      backend_twist_sub_;

  evolo_msgs::msg::ProxOpsBackendStatus::SharedPtr last_status_;
  nav_msgs::msg::Odometry::SharedPtr last_target_state_;
  nav_msgs::msg::Path::SharedPtr last_candidate_path_;
  geometry_msgs::msg::TwistStamped::SharedPtr last_backend_twist_;

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
