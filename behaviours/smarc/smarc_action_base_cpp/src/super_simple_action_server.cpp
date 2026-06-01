/* file: super_simple_action_server.cpp
 * description: Again, pretty much a copy of the SuperSimpleActionServer.py
 * that lives under smarc2/examples. Here we showcase how to use the c++
 * GentlerActionServer the same way it was done in the python example.
 * */
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
// This one is very important for handling server shutdowns gracefully!!
#include "smarc_action_base_cpp/graceful_shutdown.hpp"

namespace smarc_action_base_cpp {

class SuperSimpleAction {
 public:
  explicit SuperSimpleAction(rclcpp::Node::SharedPtr node)
      : node_(std::move(node)),
        action_server_(node_, "super_simple_cpp",
                       std::bind(&SuperSimpleAction::on_goal_received, this,
                                 std::placeholders::_1),
                       std::bind(&SuperSimpleAction::on_cancel_received, this),
                       std::bind(&SuperSimpleAction::prepare_loop, this),
                       std::bind(&SuperSimpleAction::loop_inner, this),
                       std::bind(&SuperSimpleAction::give_feedback, this),
                       GentlerActionServer::Config(/*loop_frequency_hz*/ 5.0)) {
  }

  void request_shutdown() { action_server_.request_shutdown(); }

 private:
  using LoopStatus = GentlerActionServer::LoopStatus;
  using Json = GentlerActionServer::Json;

  bool on_goal_received(const Json& goal) {
    RCLCPP_INFO(node_->get_logger(), "Received goal: %s", goal.dump().c_str());
    loop_max_ = goal.value("loop_max", 25);
    return loop_max_ > 0;
  }

  bool on_cancel_received() {
    RCLCPP_INFO(node_->get_logger(), "Received cancel request.");
    return true;
  }

  void prepare_loop() {
    RCLCPP_INFO(node_->get_logger(), "Preparing loop.");
    looped_for_ = 0;
  }

  LoopStatus loop_inner() {
    ++looped_for_;
    if (looped_for_ >= loop_max_) {
      RCLCPP_INFO(node_->get_logger(), "Reached %d/%d iterations.", looped_for_,
                  loop_max_);
      return LoopStatus::SUCCESS;
    }
    return LoopStatus::RUNNING;
  }

  std::string give_feedback() {
    return "Action is in progress: " + std::to_string(looped_for_) + "/" +
           std::to_string(loop_max_);
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;
  int looped_for_ = 0;
  int loop_max_ = 25;
};

}  // namespace smarc_action_base_cpp

int main(int argc, char** argv) {
  // Option to disable ROS' shutdown.
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();

  // Init node with disabled shutdown. 
  rclcpp::init(argc, argv, init_options);
  // Take control of SIGINT and SIGTERM.
  smarc_action_base_cpp::install_signal_handlers();

  //--These are probably the only few lines you'll need to change in the main.--
  auto node = rclcpp::Node::make_shared("super_simple_action_server_cpp");
  auto action =
      std::make_shared<smarc_action_base_cpp::SuperSimpleAction>(node);
  //----------------------------------------------------------------------------
  
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);

  // Make sure to always use our spin + shutdown routine. 
  smarc_action_base_cpp::spin_with_graceful_shutdown(
      executor, [&action]() { action->request_shutdown(); });

  executor.remove_node(node);
  action.reset();
  node.reset();

  rclcpp::shutdown();
  return 0;
}
