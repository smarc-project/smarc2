#include <chrono>
#include <memory>
#include <string>

#include "evolo_msgs/msg/prox_ops_backend_status.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

namespace prox_ops_actions {

class FakeProxOpsBackend : public rclcpp::Node {
 public:
  FakeProxOpsBackend()
      : Node("fake_prox_ops_backend") {
    declare_parameter("publish_frequency_hz", 10.0);
    declare_parameter("long_range_convergence_delay_s", 2.0);
    declare_parameter("success_delay_s", 8.0);
    declare_parameter("target_range_start_m", 100.0);
    declare_parameter("target_range_rate_mps", 5.0);
    declare_parameter("autostart", false);

    publish_frequency_hz_ = get_parameter("publish_frequency_hz").as_double();
    long_range_convergence_delay_s_ =
        get_parameter("long_range_convergence_delay_s").as_double();
    success_delay_s_ = get_parameter("success_delay_s").as_double();
    target_range_start_m_ = get_parameter("target_range_start_m").as_double();
    target_range_rate_mps_ = get_parameter("target_range_rate_mps").as_double();
    autostart_ = get_parameter("autostart").as_bool();

    status_pub_ =
        create_publisher<evolo_msgs::msg::ProxOpsBackendStatus>("backend/status", 10);
    path_pub_ = create_publisher<nav_msgs::msg::Path>("backend/candidate_path", 10);
    control_pub_ =
        create_publisher<nav_msgs::msg::Odometry>("backend/control_planned", 10);

    command_sub_ = create_subscription<std_msgs::msg::String>(
        "backend/command", 10,
        std::bind(&FakeProxOpsBackend::command_cb, this, std::placeholders::_1));

    timer_ = create_wall_timer(
        std::chrono::duration<double>(1.0 / publish_frequency_hz_),
        std::bind(&FakeProxOpsBackend::publish_backend_state, this));

    if (autostart_) {
      start_run();
    }

    RCLCPP_INFO(get_logger(), "Fake prox-ops backend started.");
  }

 private:
  enum class State {
    IDLE,
    RUNNING,
    STOPPED,
  };

  void command_cb(const std_msgs::msg::String::SharedPtr msg) {
    RCLCPP_INFO(get_logger(), "Received backend command: %s", msg->data.c_str());

    if (msg->data.find("\"START\"") != std::string::npos) {
      start_run();
      return;
    }

    if (msg->data.find("\"STOP\"") != std::string::npos) {
      state_ = State::STOPPED;
      has_run_start_time_ = false;
      return;
    }

    if (msg->data.find("\"RESET\"") != std::string::npos) {
      if (autostart_) {
        start_run();
      } else {
        state_ = State::IDLE;
        has_run_start_time_ = false;
      }
      return;
    }
  }

  void start_run() {
    state_ = State::RUNNING;
    run_start_time_ = now();
    has_run_start_time_ = true;
  }

  void publish_backend_state() {
    if (state_ != State::RUNNING || !has_run_start_time_) {
      publish_idle_status();
      return;
    }

    const auto elapsed_s = (now() - run_start_time_).seconds();
    const bool converged = elapsed_s >= long_range_convergence_delay_s_;
    const bool success = elapsed_s >= success_delay_s_;
    const double range_m =
        std::max(0.0, target_range_start_m_ - elapsed_s * target_range_rate_mps_);

    evolo_msgs::msg::ProxOpsBackendStatus status;
    status.header.stamp = now();
    status.header.frame_id = "map";
    status.mode = success
        ? evolo_msgs::msg::ProxOpsBackendStatus::MODE_INSPECT
        : (converged
            ? evolo_msgs::msg::ProxOpsBackendStatus::MODE_LONG_RANGE_INTERCEPT
            : evolo_msgs::msg::ProxOpsBackendStatus::MODE_WAITING_FOR_LONG_RANGE);
    status.health = evolo_msgs::msg::ProxOpsBackendStatus::HEALTH_OK;
    status.long_range_track_live = true;
    status.long_range_track_converged = converged;
    status.terminal_track_live = false;
    status.target_lost = false;
    status.plan_available = converged;
    status.target_intercepted = success;
    status.long_range_confidence = converged ? 0.95F : 0.4F;
    status.terminal_confidence = 0.0F;
    status.target_range_m = static_cast<float>(range_m);
    status.status_text = success ? "FAKE_SUCCESS"
                                 : (converged ? "FAKE_INTERCEPTING"
                                              : "FAKE_WAITING_FOR_CONVERGENCE");
    status_pub_->publish(status);

    if (status.plan_available) {
      publish_path_and_twist();
    }
  }

  void publish_idle_status() {
    evolo_msgs::msg::ProxOpsBackendStatus status;
    status.header.stamp = now();
    status.header.frame_id = "map";
    status.mode = state_ == State::STOPPED
        ? evolo_msgs::msg::ProxOpsBackendStatus::MODE_IDLE
        : evolo_msgs::msg::ProxOpsBackendStatus::MODE_UNKNOWN;
    status.health = evolo_msgs::msg::ProxOpsBackendStatus::HEALTH_OK;
    status.status_text = state_ == State::STOPPED ? "FAKE_STOPPED" : "FAKE_IDLE";
    status_pub_->publish(status);
  }

  void publish_path_and_twist() {
    nav_msgs::msg::Path path;
    path.header.stamp = now();
    path.header.frame_id = "map";

    for (int i = 0; i < 5; ++i) {
      geometry_msgs::msg::PoseStamped pose;
      pose.header = path.header;
      pose.pose.position.x = static_cast<double>(i) * 2.0;
      pose.pose.position.y = 0.0;
      pose.pose.position.z = 0.0;
      pose.pose.orientation.w = 1.0;
      path.poses.push_back(pose);
    }
    path_pub_->publish(path);

    nav_msgs::msg::Odometry control;
    control.header.stamp = now();
    control.header.frame_id = "map";
    control.child_frame_id = "base_link";
    // Fake backend has no real target heading — publish identity orientation.
    control.pose.pose.orientation.w = 1.0;
    control.twist.twist.linear.x = 0.5;
    control_pub_->publish(control);
  }

  State state_ = State::IDLE;
  rclcpp::Time run_start_time_;
  bool has_run_start_time_ = false;

  double publish_frequency_hz_ = 10.0;
  double long_range_convergence_delay_s_ = 2.0;
  double success_delay_s_ = 8.0;
  double target_range_start_m_ = 100.0;
  double target_range_rate_mps_ = 5.0;
  bool autostart_ = false;

  rclcpp::Publisher<evolo_msgs::msg::ProxOpsBackendStatus>::SharedPtr status_pub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr path_pub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr control_pub_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr command_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

}  // namespace prox_ops_actions

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<prox_ops_actions::FakeProxOpsBackend>());
  rclcpp::shutdown();
  return 0;
}
