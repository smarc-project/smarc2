#include "smarc_action_base_cpp/graceful_shutdown.hpp"

#include <csignal>

namespace smarc_action_base_cpp {
namespace {

volatile std::sig_atomic_t g_signal_shutdown_requested = 0;

void signal_handler(int)
{
  g_signal_shutdown_requested = 1;
}

}  // namespace

rclcpp::InitOptions manual_signal_handling_init_options()
{
  rclcpp::InitOptions init_options;
  init_options.shutdown_on_signal = false;
  return init_options;
}

void install_signal_handlers()
{
  reset_signal_shutdown_request();
  std::signal(SIGINT, signal_handler);
  std::signal(SIGTERM, signal_handler);
}

void reset_signal_shutdown_request()
{
  g_signal_shutdown_requested = 0;
}

bool signal_shutdown_requested()
{
  return g_signal_shutdown_requested != 0;
}

void spin_some_for(
    rclcpp::Executor &executor,
    std::chrono::milliseconds duration,
    std::chrono::milliseconds spin_period)
{
  const auto start = std::chrono::steady_clock::now();
  while (rclcpp::ok() && std::chrono::steady_clock::now() - start < duration) {
    executor.spin_some(spin_period);
  }
}

void spin_with_graceful_shutdown(
    rclcpp::Executor &executor,
    const ShutdownCallback &on_shutdown,
    std::chrono::milliseconds spin_period,
    std::chrono::milliseconds flush_duration)
{
  while (rclcpp::ok() && !signal_shutdown_requested()) {
    executor.spin_some(spin_period);
  }

  on_shutdown();
  spin_some_for(executor, flush_duration, spin_period);
}

}  // namespace smarc_action_base_cpp
