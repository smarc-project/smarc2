/* file: evolo_loiter_patrol.cpp
 * description: Placeholder loiter/patrol action for Evolo prox-ops BT.
 * license: MIT
 */
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"

namespace prox_ops_actions
{

class EvoloLoiterPatrol
{
public:
  explicit EvoloLoiterPatrol(rclcpp::Node::SharedPtr node)
  : node_(std::move(node)),
    action_server_(
      node_, "evolo_loiter_patrol",
      std::bind(&EvoloLoiterPatrol::on_goal_received, this,
      std::placeholders::_1),
      std::bind(&EvoloLoiterPatrol::on_cancel_received, this),
      std::bind(&EvoloLoiterPatrol::prepare_loop, this),
      std::bind(&EvoloLoiterPatrol::loop_inner, this),
      std::bind(&EvoloLoiterPatrol::feedback, this),
      smarc_action_base_cpp::GentlerActionServer::Config(10.0)) {}

  void request_shutdown() {action_server_.request_shutdown();}

private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;

  bool on_goal_received(const Json & goal)
  {
    goal_json_ = goal.dump();
    RCLCPP_INFO(
      node_->get_logger(), "Received loiter/patrol goal: %s",
      goal_json_.c_str());
    return true;
  }

  bool on_cancel_received()
  {
    feedback_ = "CANCELLED";
    return true;
  }

  void prepare_loop()
  {
    feedback_ = "LOITER_PATROL_PLACEHOLDER_RUNNING";
    RCLCPP_WARN_ONCE(
      node_->get_logger(),
      "evolo_loiter_patrol is a placeholder and does not command Evolo yet.");
  }

  LoopStatus loop_inner()
  {
    // TODO: Implement real foiling loiter/patrol by delegating to Evolo motion
    // actions or by publishing an appropriate safe patrol command stream.
    return LoopStatus::RUNNING;
  }

  std::string feedback() const {return feedback_;}

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;
  std::string goal_json_;
  std::string feedback_ = "IDLE";
};

}  // namespace prox_ops_actions

int main(int argc, char ** argv)
{
  auto init_options =
    smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("evolo_loiter_patrol_node");
  auto action = std::make_shared<prox_ops_actions::EvoloLoiterPatrol>(node);

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);

  smarc_action_base_cpp::spin_with_graceful_shutdown(
    executor, [&action]() {action->request_shutdown();});

  executor.remove_node(node);
  action.reset();
  node.reset();

  rclcpp::shutdown();
  return 0;
}
