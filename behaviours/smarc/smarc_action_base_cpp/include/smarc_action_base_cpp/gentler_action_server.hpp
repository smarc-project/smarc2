/* file: gentler_action_server.hpp
 * description: Pretty much a 1:1 translation of Ozer's GentlerActionServer from
 * python to cpp. We do not inherit from the SMARCActionServer, but instead
 * embedd the plumbing (and heartbeat-publishing) in a single cpp class, and use
 * the same API as its python counterpart to make sure it's compatible with
 * our behaviour tree.
 */
#ifndef SMARC_ACTION_BASE_CPP__GENTLER_ACTION_SERVER_HPP_
#define SMARC_ACTION_BASE_CPP__GENTLER_ACTION_SERVER_HPP_

#include <atomic>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <utility>

#include <nlohmann/json.hpp>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "smarc_msgs/action/base_action.hpp"
#include "std_msgs/msg/string.hpp"

namespace smarc_action_base_cpp {

class GentlerActionServer {
 public:
  using BaseAction = smarc_msgs::action::BaseAction;
  using GoalHandle = rclcpp_action::ServerGoalHandle<BaseAction>;
  using Json = nlohmann::json;

  enum class LoopStatus { RUNNING, SUCCESS, FAILURE };

  struct Config {
    explicit Config(double loop_frequency_hz = 5.0,
                    double heartbeat_period_s = 1.0,
                    std::string heartbeat_topic =
                        "waraps/action_server_heartbeat",
                    bool preempt_active_goal = true)
        : loop_frequency_hz(loop_frequency_hz),
          heartbeat_period_s(heartbeat_period_s),
          heartbeat_topic(std::move(heartbeat_topic)),
          preempt_active_goal(preempt_active_goal) {}

    double loop_frequency_hz;
    double heartbeat_period_s;
    std::string heartbeat_topic;
    bool preempt_active_goal;
  };

  using OnGoalReceived = std::function<bool(const Json &)>;
  using OnCancelReceived = std::function<bool()>;
  using PrepareLoop = std::function<void()>;
  using LoopInner = std::function<LoopStatus()>;
  using GiveFeedback = std::function<std::string()>;

  GentlerActionServer(rclcpp::Node::SharedPtr node,
                      const std::string &action_name,
                      OnGoalReceived on_goal_received,
                      OnCancelReceived on_cancel_received,
                      PrepareLoop prepare_loop, LoopInner loop_inner,
                      GiveFeedback give_feedback,
                      const Config &config = Config{});

  ~GentlerActionServer();

  // Copy and move guards.
  GentlerActionServer(const GentlerActionServer &) = delete;
  GentlerActionServer &operator=(const GentlerActionServer &) = delete;
  GentlerActionServer(GentlerActionServer &&) = delete;
  GentlerActionServer &operator=(GentlerActionServer &&) = delete;

  std::string action_name() const;
  std::string parsed_action_name() const;
  void request_shutdown();

 private:
  rclcpp_action::GoalResponse handle_goal(
      const rclcpp_action::GoalUUID &uuid,
      std::shared_ptr<const BaseAction::Goal> goal);

  rclcpp_action::CancelResponse handle_cancel(
      const std::shared_ptr<GoalHandle> goal_handle);

  void handle_accepted(const std::shared_ptr<GoalHandle> goal_handle);
  void execute(const std::shared_ptr<GoalHandle> goal_handle);
  // For WARA-PS BT compliance.
  void publish_heartbeat();

  std::string construct_parsed_action_name() const;
  void stop_execution_thread();

  rclcpp::Node::SharedPtr node_;
  std::string action_name_;
  std::string parsed_action_name_;
  Config config_;

  OnGoalReceived on_goal_received_;
  OnCancelReceived on_cancel_received_;
  PrepareLoop prepare_loop_;
  LoopInner loop_inner_;
  GiveFeedback give_feedback_;

  rclcpp_action::Server<BaseAction>::SharedPtr action_server_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr heartbeat_pub_;
  rclcpp::TimerBase::SharedPtr heartbeat_timer_;

  // For the plumbing and bookkeeping done in the SMARCActionServer.
  std::atomic_bool stop_requested_{false};
  mutable std::mutex goal_mutex_;
  std::shared_ptr<GoalHandle> active_goal_handle_;
  std::thread execution_thread_;
};

}  // namespace smarc_action_base_cpp

#endif  // SMARC_ACTION_BASE_CPP__GENTLER_ACTION_SERVER_HPP_
