/* file: graceful_shutdown.hpp
 * description: These are helper functions that allow us to take control of the
 * shutdown sequence for action servers developed with the GentlerActionServer 
 * in c++. Using ROS' shutdown lead to action clients hanging while canceling a
 * goal if the action server had crashed or was shutdown for any reason before
 * resolving a client's goal. The gist is the following:
 *  - catch SIGINT and SIGTERM signals.
 *  - trigger a flag for shutdown.
 *  - stop spinning the exec and exit the while rclcpp::ok loop.
 *  - send an ABORT to the client.
 *  - spin a bit more to make sure the client gets the abort.
 *  - shutdown gracefully.
 */
#ifndef SMARC_ACTION_BASE_CPP__GRACEFUL_SHUTDOWN_HPP_
#define SMARC_ACTION_BASE_CPP__GRACEFUL_SHUTDOWN_HPP_

#include <chrono>
#include <functional>

#include "rclcpp/rclcpp.hpp"

namespace smarc_action_base_cpp {

using ShutdownCallback = std::function<void()>;

rclcpp::InitOptions manual_signal_handling_init_options();
void install_signal_handlers();
void reset_signal_shutdown_request();
bool signal_shutdown_requested();

void spin_some_for(
    rclcpp::Executor &executor,
    std::chrono::milliseconds duration,
    std::chrono::milliseconds spin_period = std::chrono::milliseconds(100));

void spin_with_graceful_shutdown(
    rclcpp::Executor &executor,
    const ShutdownCallback &on_shutdown,
    std::chrono::milliseconds spin_period = std::chrono::milliseconds(100),
    std::chrono::milliseconds flush_duration = std::chrono::milliseconds(500));

}  // namespace smarc_action_base_cpp

#endif  // SMARC_ACTION_BASE_CPP__GRACEFUL_SHUTDOWN_HPP_
