#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"

namespace smarc_basic_cpp {

class WaitAction {
 public:
  explicit WaitAction(rclcpp::Node::SharedPtr node)
      : node_(std::move(node)),
        action_server_(
            node_, "smarc_wait",
            std::bind(&WaitAction::on_goal_received, this,
                      std::placeholders::_1),
            std::bind(&WaitAction::on_cancel_received, this),
            std::bind(&WaitAction::prepare_loop, this),
            std::bind(&WaitAction::loop_inner, this),
            std::bind(&WaitAction::feedback, this),
            smarc_action_base_cpp::GentlerActionServer::Config(20.0)) {
    reset();
  }

  void request_shutdown() { action_server_.request_shutdown(); }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  void reset() {
    started_waiting_ = rclcpp::Time(0, 0, node_->get_clock()->get_clock_type());
    has_started_waiting_ = false;
    timeout_s_ = 0.0;
    has_timeout_ = false;
  }

  bool on_goal_received(const Json& goal) {
    try {
      timeout_s_ = goal.at("timeout").get<double>();
      has_timeout_ = true;
      return timeout_s_ >= 0.0;
    } catch (const std::exception& error) {
      RCLCPP_ERROR(node_->get_logger(), "Error parsing timeout: %s",
                   error.what());
      return false;
    }
  }

  bool on_cancel_received() {
    reset();
    return true;
  }

  void prepare_loop() {
    started_waiting_ = node_->get_clock()->now();
    has_started_waiting_ = true;
    RCLCPP_INFO(node_->get_logger(), "Started waiting for %.2f seconds",
                timeout_s_);
  }

  double elapsed_time() const {
    if (!has_started_waiting_) {
      return -1.0;
    }

    return (node_->get_clock()->now() - started_waiting_).seconds();
  }

  LoopStatus loop_inner() {
    if (!has_started_waiting_ || !has_timeout_) {
      return LoopStatus::FAILURE;
    }

    if (elapsed_time() >= timeout_s_) {
      RCLCPP_INFO(node_->get_logger(), "Finished waiting.");
      return LoopStatus::SUCCESS;
    }

    RCLCPP_DEBUG(node_->get_logger(),
                 "Waiting... Elapsed time: %.2f seconds / %.2f seconds",
                 elapsed_time(), timeout_s_);
    return LoopStatus::RUNNING;
  }

  std::string feedback() const {
    if (!has_started_waiting_ || !has_timeout_) {
      return "Not started";
    }

    return "Elapsed time: " + std::to_string(elapsed_time()) + " seconds / " +
           std::to_string(timeout_s_) + " seconds";
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;
  rclcpp::Time started_waiting_;
  bool has_started_waiting_ = false;
  double timeout_s_ = 0.0;
  bool has_timeout_ = false;
};

}  // namespace smarc_basic_cpp

int main(int argc, char** argv) {
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("wait_action_node_cpp");
  auto wait_action = std::make_shared<smarc_basic_cpp::WaitAction>(node);

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);

  smarc_action_base_cpp::spin_with_graceful_shutdown(
      executor, [&wait_action]() { wait_action->request_shutdown(); });

  executor.remove_node(node);
  wait_action.reset();
  node.reset();

  rclcpp::shutdown();
  return 0;
}
