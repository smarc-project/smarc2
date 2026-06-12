/* file: evolo_loiter_patrol.cpp
 * description: Evolo loiter/patrol action for prox-ops fallback.
 * license: MIT
 */
#include <array>
#include <chrono>
#include <memory>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "smarc_action_base_cpp/gentler_action_server.hpp"
#include "smarc_action_base_cpp/graceful_shutdown.hpp"
#include "smarc_msgs/action/base_action.hpp"

namespace prox_ops_actions {

class EvoloLoiterPatrol {
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
            smarc_action_base_cpp::GentlerActionServer::Config(10.0)) {
    node_->declare_parameter("move_to_action_name", "move_to");
    node_->declare_parameter("move_to_wait_timeout_s", 5.0);
    node_->declare_parameter("default_speed", "standard");

    move_to_action_name_ =
        node_->get_parameter("move_to_action_name").as_string();
    move_to_wait_timeout_s_ =
        node_->get_parameter("move_to_wait_timeout_s").as_double();
    default_speed_ = node_->get_parameter("default_speed").as_string();

    move_to_client_ =
        rclcpp_action::create_client<BaseAction>(node_, move_to_action_name_);
  }

  void request_shutdown() {
    cancel_active_move_to_goal();
    action_server_.request_shutdown();
  }

 private:
  using GentlerActionServer = smarc_action_base_cpp::GentlerActionServer;
  using Json = GentlerActionServer::Json;
  using LoopStatus = GentlerActionServer::LoopStatus;
  using BaseAction = smarc_msgs::action::BaseAction;
  using ClientGoalHandle = rclcpp_action::ClientGoalHandle<BaseAction>;

  enum class DelegateState {
    IDLE,
    WAITING_FOR_ACCEPTANCE,
    RUNNING,
    SUCCEEDED,
    FAILED,
    CANCELING,
  };

  bool on_goal_received(const Json& goal) {
    reset_patrol_state();
    goal_json_ = goal.dump();

    try {
      speed_ = parse_speed(goal);
      waypoints_[0] = parse_waypoint(goal, 0);
      waypoints_[1] = parse_waypoint(goal, 1);
    } catch (const std::exception& error) {
      RCLCPP_ERROR(node_->get_logger(), "Rejecting loiter/patrol goal; %s",
                   error.what());
      feedback_ = std::string("GOAL_REJECTED: ") + error.what();
      return false;
    }

    RCLCPP_INFO(node_->get_logger(), "Received loiter/patrol goal: %s",
                goal_json_.c_str());
    return true;
  }

  bool on_cancel_received() {
    cancel_active_move_to_goal();
    feedback_ = "CANCELLED";
    return true;
  }

  void prepare_loop() {
    reset_runtime_state();
    action_start_time_ = node_->get_clock()->now();
    feedback_ = "LOITER_PATROL_STARTING";
  }

  LoopStatus loop_inner() {
    // Wait for move_to server.
    if (!move_to_client_->action_server_is_ready()) {
      const auto waited_s =
          (node_->get_clock()->now() - action_start_time_).seconds();
      feedback_ = "WAITING_FOR_MOVE_TO_SERVER";
      if (waited_s > move_to_wait_timeout_s_) {
        feedback_ = "MOVE_TO_SERVER_UNAVAILABLE";
        return LoopStatus::FAILURE;
      }
      return LoopStatus::RUNNING;
    }

    // If the delegated move_to action has failed, send a FAILURE.
    const auto state = delegate_state();
    if (state == DelegateState::FAILED) {
      return LoopStatus::FAILURE;
    }

    // If the delegated move_to action succeeded, switch waypoint a-la-niklas.
    if (state == DelegateState::SUCCEEDED) {
      current_waypoint_index_ =
          (current_waypoint_index_ + 1) % waypoints_.size();
      set_delegate_state(DelegateState::IDLE);
    }

    // If the move_to server is idle, send the next goal.
    if (delegate_state() == DelegateState::IDLE) {
      send_current_move_to_goal();
    }

    feedback_ = "LOITER_PATROL_MOVING_TO_WP_" +
                std::to_string(current_waypoint_index_ + 1);
    return LoopStatus::RUNNING;
  }

  std::string feedback() const { return feedback_; }

  void send_current_move_to_goal() {
    BaseAction::Goal goal;
    const Json move_to_goal = {
        {"speed", speed_},
        {"waypoint", waypoints_[current_waypoint_index_]},
    };
    goal.goal.data = move_to_goal.dump();
    const auto generation = delegate_generation();

    rclcpp_action::Client<BaseAction>::SendGoalOptions options;
    options.goal_response_callback =
        [this, generation](const ClientGoalHandle::SharedPtr& goal_handle) {
          // Make sure this callback is from the right move_to generation.
          if (generation != delegate_generation()) {
            return;
          }

          // null goal_handle means that move_to rejected the goal. 
          if (!goal_handle) {
            set_delegate_state(DelegateState::FAILED);
            feedback_ = "MOVE_TO_GOAL_REJECTED";
            return;
          }

          {
            std::lock_guard<std::mutex> lock(delegate_mutex_);
            active_move_to_goal_ = goal_handle;
            delegate_state_ = DelegateState::RUNNING;
          }
        };

    options.result_callback =
        [this, generation](const ClientGoalHandle::WrappedResult& result) {
          std::lock_guard<std::mutex> lock(delegate_mutex_);
          // Make sure this callback is from the right move_to generation.
          if (generation != delegate_generation_) {
            return;
          }

          // We're done regardless of the reason, so reset the goal.
          active_move_to_goal_.reset();

          if (delegate_state_ == DelegateState::CANCELING) {
            delegate_state_ = DelegateState::IDLE;
            return;
          }

          if (result.code == rclcpp_action::ResultCode::SUCCEEDED &&
              result.result && result.result->success) {
            delegate_state_ = DelegateState::SUCCEEDED;
            return;
          }

          delegate_state_ = DelegateState::FAILED;
          feedback_ = "MOVE_TO_GOAL_FAILED";
        };

    // Delegate the move_to goal.
    set_delegate_state(DelegateState::WAITING_FOR_ACCEPTANCE);
    move_to_client_->async_send_goal(goal, options);
    RCLCPP_INFO(node_->get_logger(), "Sent patrol move_to goal: %s",
                goal.goal.data.c_str());
  }

  void cancel_active_move_to_goal() {
    std::lock_guard<std::mutex> lock(delegate_mutex_);
    if (active_move_to_goal_) {
      move_to_client_->async_cancel_goal(active_move_to_goal_);
      active_move_to_goal_.reset();
    }
    delegate_state_ = DelegateState::CANCELING;
  }

  DelegateState delegate_state() const {
    std::lock_guard<std::mutex> lock(delegate_mutex_);
    return delegate_state_;
  }

  void set_delegate_state(DelegateState state) {
    std::lock_guard<std::mutex> lock(delegate_mutex_);
    delegate_state_ = state;
  }

  void reset_patrol_state() {
    cancel_active_move_to_goal();
    current_waypoint_index_ = 0;
    goal_json_.clear();
    feedback_ = "IDLE";
  }

  void reset_runtime_state() {
    std::lock_guard<std::mutex> lock(delegate_mutex_);
    // Increase the generation every time we reset.
    ++delegate_generation_;
    active_move_to_goal_.reset();
    delegate_state_ = DelegateState::IDLE;
    current_waypoint_index_ = 0;
  }

  std::size_t delegate_generation() const {
    std::lock_guard<std::mutex> lock(delegate_mutex_);
    return delegate_generation_;
  }

  std::string parse_speed(const Json& goal) const {
    if (!goal.contains("speed")) {
      return default_speed_;
    }

    if (goal["speed"].is_string()) {
      return goal["speed"].get<std::string>();
    }

    if (goal["speed"].is_number()) {
      std::ostringstream out;
      out << goal["speed"].get<double>();
      return out.str();
    }

    return default_speed_;
  }

  Json parse_waypoint(const Json& goal, std::size_t index) const {
    if (goal.contains("waypoints") && goal["waypoints"].is_array() &&
        goal["waypoints"].size() >= 2) {
      return normalize_waypoint(goal["waypoints"].at(index));
    }

    const auto key = index == 0 ? "loiter_1" : "loiter_2";
    if (goal.contains(key)) {
      return normalize_waypoint(goal.at(key));
    }

    throw std::runtime_error(
        "loiter_patrol goal needs waypoints[0:2] or loiter_1/loiter_2");
  }

  Json normalize_waypoint(const Json& waypoint) const {
    if (waypoint.is_object()) {
      if (!waypoint.contains("latitude") || !waypoint.contains("longitude")) {
        throw std::runtime_error(
            "waypoint object needs latitude and longitude");
      }
      return waypoint;
    }

    if (waypoint.is_array() && waypoint.size() >= 2) {
      return Json{
          {"latitude", waypoint.at(0).get<double>()},
          {"longitude", waypoint.at(1).get<double>()},
      };
    }

    throw std::runtime_error(
        "waypoint must be an object or [latitude, longitude]");
  }

  rclcpp::Node::SharedPtr node_;
  GentlerActionServer action_server_;
  rclcpp_action::Client<BaseAction>::SharedPtr move_to_client_;

  std::array<Json, 2> waypoints_;
  std::size_t current_waypoint_index_ = 0;
  std::string speed_;
  std::string default_speed_ = "standard";
  std::string move_to_action_name_ = "move_to";
  double move_to_wait_timeout_s_ = 5.0;

  rclcpp::Time action_start_time_;
  mutable std::mutex delegate_mutex_;
  ClientGoalHandle::SharedPtr active_move_to_goal_;
  DelegateState delegate_state_ = DelegateState::IDLE;
  std::size_t delegate_generation_ = 0;

  std::string goal_json_;
  std::string feedback_ = "IDLE";
};

}  // namespace prox_ops_actions

int main(int argc, char** argv) {
  auto init_options =
      smarc_action_base_cpp::manual_signal_handling_init_options();
  rclcpp::init(argc, argv, init_options);
  smarc_action_base_cpp::install_signal_handlers();

  auto node = rclcpp::Node::make_shared("evolo_loiter_patrol_node");
  auto action = std::make_shared<prox_ops_actions::EvoloLoiterPatrol>(node);

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
