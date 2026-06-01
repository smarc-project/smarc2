#include "smarc_action_base_cpp/gentler_action_server.hpp"

#include <chrono>
#include <exception>
#include <utility>

namespace smarc_action_base_cpp {

GentlerActionServer::GentlerActionServer(
    rclcpp::Node::SharedPtr node, const std::string &action_name,
    OnGoalReceived on_goal_received, OnCancelReceived on_cancel_received,
    PrepareLoop prepare_loop, LoopInner loop_inner, GiveFeedback give_feedback,
    const Config &config)
    : node_(std::move(node)),
      action_name_(action_name),
      config_(config),
      on_goal_received_(std::move(on_goal_received)),
      on_cancel_received_(std::move(on_cancel_received)),
      prepare_loop_(std::move(prepare_loop)),
      loop_inner_(std::move(loop_inner)),
      give_feedback_(std::move(give_feedback)) {
  parsed_action_name_ = construct_parsed_action_name();

  // TODO: how do we get the heartbeat_topic from SmarcTopics?
  heartbeat_pub_ = node_->create_publisher<std_msgs::msg::String>(
      config_.heartbeat_topic, 5);
  heartbeat_timer_ = node_->create_wall_timer(
      std::chrono::duration<double>(config_.heartbeat_period_s),
      std::bind(&GentlerActionServer::publish_heartbeat, this));

  action_server_ = rclcpp_action::create_server<BaseAction>(
      node_, action_name_,
      std::bind(&GentlerActionServer::handle_goal, this, std::placeholders::_1,
                std::placeholders::_2),
      std::bind(&GentlerActionServer::handle_cancel, this,
                std::placeholders::_1),
      std::bind(&GentlerActionServer::handle_accepted, this,
                std::placeholders::_1));
}

GentlerActionServer::~GentlerActionServer() { request_shutdown(); }

std::string GentlerActionServer::action_name() const { return action_name_; }

std::string GentlerActionServer::parsed_action_name() const {
  return parsed_action_name_;
}

void GentlerActionServer::request_shutdown() {
  stop_requested_.store(true);

  if (heartbeat_timer_) {
    heartbeat_timer_->cancel();
  }

  std::shared_ptr<GoalHandle> goal_handle;
  {
    std::lock_guard<std::mutex> lock(goal_mutex_);
    goal_handle = active_goal_handle_;
    active_goal_handle_.reset();
  }

  if (goal_handle && goal_handle->is_active() && rclcpp::ok()) {
    auto result = std::make_shared<BaseAction::Result>();
    result->success = false;
    try {
      goal_handle->abort(result);
      RCLCPP_INFO(node_->get_logger(),
                  "Goal for <%s> aborted due to server shutdown.",
                  action_name_.c_str());
    } catch (const std::exception &error) {
      RCLCPP_WARN(node_->get_logger(),
                  "Could not abort goal for <%s> during shutdown: %s",
                  action_name_.c_str(), error.what());
    }
  }

  stop_execution_thread();
}

rclcpp_action::GoalResponse GentlerActionServer::handle_goal(
    const rclcpp_action::GoalUUID &uuid,
    std::shared_ptr<const BaseAction::Goal> goal) {
  (void)uuid;

  if (stop_requested_.load()) {
    return rclcpp_action::GoalResponse::REJECT;
  }

  // Preemtive check.
  if (!config_.preempt_active_goal) {
    std::lock_guard<std::mutex> lock(goal_mutex_);
    if (active_goal_handle_ && active_goal_handle_->is_active()) {
      RCLCPP_WARN(node_->get_logger(),
                  "Rejecting goal for <%s>; another goal is active.",
                  action_name_.c_str());
      return rclcpp_action::GoalResponse::REJECT;
    }
  }

  // Null goal pointer check.
  if (!goal) {
    RCLCPP_ERROR(node_->get_logger(), "Rejecting null goal for <%s>.",
                 action_name_.c_str());
    return rclcpp_action::GoalResponse::REJECT;
  }

  // Goal JSON check.
  try {
    const auto goal_json = Json::parse(goal->goal.data);
    // Using user-provided OnGoalReceived function.
    if (on_goal_received_(goal_json)) {
      return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    RCLCPP_INFO(node_->get_logger(), "User callback rejected goal for <%s>.",
                action_name_.c_str());
  } catch (const Json::parse_error &error) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Rejecting goal for <%s>; JSON parse error: %s",
                 action_name_.c_str(), error.what());
  } catch (const std::exception &error) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Rejecting goal for <%s>; callback threw: %s",
                 action_name_.c_str(), error.what());
  } catch (...) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Rejecting goal for <%s>; callback threw unknown exception.",
                 action_name_.c_str());
  }

  return rclcpp_action::GoalResponse::REJECT;
}

rclcpp_action::CancelResponse GentlerActionServer::handle_cancel(
    const std::shared_ptr<GoalHandle> goal_handle) {
  (void)goal_handle;

  if (stop_requested_.load()) {
    return rclcpp_action::CancelResponse::REJECT;
  }

  try {
    // Using user-provided OnCancelReceived function.
    return on_cancel_received_() ? rclcpp_action::CancelResponse::ACCEPT
                                 : rclcpp_action::CancelResponse::REJECT;
  } catch (const std::exception &error) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Rejecting cancel for <%s>; callback threw: %s",
                 action_name_.c_str(), error.what());
  } catch (...) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Rejecting cancel for <%s>; callback threw unknown exception.",
                 action_name_.c_str());
  }

  return rclcpp_action::CancelResponse::REJECT;
}

void GentlerActionServer::handle_accepted(
    const std::shared_ptr<GoalHandle> goal_handle) {
  if (stop_requested_.load()) {
    return;
  }

  {
    std::lock_guard<std::mutex> lock(goal_mutex_);
    active_goal_handle_ = goal_handle;
  }

  // TODO: This might block if a running inner_loop with a prior goal does not
  // exit preemtively, but still gives us clear lifetime management (in
  // comparison with the tutorial's implementation).
  stop_execution_thread();
  execution_thread_ =
      std::thread(&GentlerActionServer::execute, this, goal_handle);
}

/* This is where the magic happens. We're locking the goal_mutex everytime we
 * need to read/compare/reset the active_goal_handle to ensure that no other
 * thread is sweeping the rug underneath us. The logic below follows:
 *  1. Check if the goal was preempted.
 *  2. Check if the goal was canceled.
 * if the above passed, then we run the user-defined InnerLoop:
 *  3. If the loop_status says the loop is running, then business as usual and
 *     continue (while).
 *  4. If the loop_status says that we've succeeded, report whether the goal was
 *     accomplished or not, reset the goal, and return.
 */
void GentlerActionServer::execute(
    const std::shared_ptr<GoalHandle> goal_handle) {
  auto result = std::make_shared<BaseAction::Result>();

  try {
    // User-specified PrepareLoop.
    prepare_loop_();

    rclcpp::Rate rate(config_.loop_frequency_hz);

    while (rclcpp::ok()) {
      if (stop_requested_.load()) {
        return;
      }

      {
        std::lock_guard<std::mutex> lock(goal_mutex_);
        if (active_goal_handle_ != goal_handle) {
          if (stop_requested_.load()) {
            return;
          }
          result->success = false;
          if (goal_handle->is_active()) {
            goal_handle->abort(result);
          }
          RCLCPP_INFO(node_->get_logger(), "Goal for <%s> was preempted.",
                      action_name_.c_str());
          return;
        }
      }

      if (goal_handle->is_canceling()) {
        result->success = false;
        goal_handle->canceled(result);
        {
          std::lock_guard<std::mutex> lock(goal_mutex_);
          if (active_goal_handle_ == goal_handle) {
            active_goal_handle_.reset();
          }
        }
        RCLCPP_INFO(node_->get_logger(), "Goal for <%s> was canceled.",
                    action_name_.c_str());
        return;
      }

      // If no need to tamper with the goal, run the user-specified InnerLoop.
      const auto loop_status = loop_inner_();
      if (stop_requested_.load()) {
        return;
      }

      if (loop_status == LoopStatus::RUNNING) {
        auto feedback = std::make_shared<BaseAction::Feedback>();
        feedback->feedback.data = give_feedback_();
        goal_handle->publish_feedback(feedback);
        rate.sleep();
        continue;
      }

      result->success = loop_status == LoopStatus::SUCCESS;
      if (result->success) {
        goal_handle->succeed(result);
        RCLCPP_INFO(node_->get_logger(), "Goal for <%s> succeeded.",
                    action_name_.c_str());
      } else {
        goal_handle->abort(result);
        RCLCPP_INFO(node_->get_logger(), "Goal for <%s> failed.",
                    action_name_.c_str());
      }
      {
        std::lock_guard<std::mutex> lock(goal_mutex_);
        if (active_goal_handle_ == goal_handle) {
          active_goal_handle_.reset();
        }
      }
      return;
    }
  } catch (const std::exception &error) {
    RCLCPP_ERROR(node_->get_logger(), "Goal for <%s> aborted; exception: %s",
                 action_name_.c_str(), error.what());
  } catch (...) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Goal for <%s> aborted; unknown exception.",
                 action_name_.c_str());
  }

  result->success = false;
  if (goal_handle->is_active()) {
    goal_handle->abort(result);
  }
  {
    std::lock_guard<std::mutex> lock(goal_mutex_);
    if (active_goal_handle_ == goal_handle) {
      active_goal_handle_.reset();
    }
  }
}

void GentlerActionServer::publish_heartbeat() {
  if (stop_requested_.load()) {
    return;
  }

  std_msgs::msg::String msg;
  msg.data = parsed_action_name_;
  heartbeat_pub_->publish(msg);
}

std::string GentlerActionServer::construct_parsed_action_name() const {
  std::string ns = node_->get_namespace();
  if (ns == "/") {
    ns.clear();
  }
  return ns + "/" + action_name_;
}

void GentlerActionServer::stop_execution_thread() {
  if (execution_thread_.joinable()) {
    execution_thread_.join();
  }
}

}  // namespace smarc_action_base_cpp
