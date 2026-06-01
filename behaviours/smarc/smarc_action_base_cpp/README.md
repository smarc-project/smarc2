# smarc_action_base_cpp
# How do I use this?

That question is better answered by `src/super_simple_action_server.cpp` than in this README. Unless you intend to make additions to the C++ action server helpers it is recommended to review the implementation shown there to understand how to use `smarc_action_base_cpp`.

# Library that enforces ROS2 action-server interfaces be implemented using a C++ GentlerActionServer.
The library intends to abstract and simplify the registering of callbacks and hide some of the async complexity from the user.

The C++ API mirrors the Python `GentlerActionServer` pattern:

```cpp
GentlerActionServer(
  node,
  "my_action_name",
  on_goal_received,
  on_cancel_received,
  prepare_loop,
  loop_inner,
  give_feedback,
  GentlerActionServer::Config(5.0));
```

## Abstractions
### GentlerActionServer
This is a simple wrapper around `smarc_msgs::action::BaseAction`. It accepts the same JSON-in-a-string goal format used by the Python behaviours, calls user-provided callbacks, publishes feedback, and reports success or failure.

The user-provided callbacks are:

```cpp
bool on_goal_received(const nlohmann::json & goal);
bool on_cancel_received();
void prepare_loop();
GentlerActionServer::LoopStatus loop_inner();
std::string give_feedback();
```

`LoopStatus` replaces the Python `True`, `False`, and `None` convention:

```cpp
LoopStatus::SUCCESS
LoopStatus::FAILURE
LoopStatus::RUNNING
```

Additionally, the action server publishes the WARA-PS heartbeat so the action can be discovered in the same way as the Python action servers.

### Graceful Shutdown
Action servers need a little ceremony when the server process is stopped while a goal is active. The helper in `graceful_shutdown.hpp` keeps ROS alive long enough to abort the active goal, flush the terminal action state, and then call `rclcpp::shutdown()`.

This is the recommended shape:

```cpp
auto init_options = smarc_action_base_cpp::manual_signal_handling_init_options();
rclcpp::init(argc, argv, init_options);
smarc_action_base_cpp::install_signal_handlers();

...

smarc_action_base_cpp::spin_with_graceful_shutdown(
    executor, [&action]() { action->request_shutdown(); });
```

## Method
Callback functions are wrapped in a simplified pattern preventing user callbacks from being called directly by ROS2 action plumbing. Instead they are called through `GentlerActionServer`, which parses the JSON goal, manages the active goal handle, publishes feedback, and translates `LoopStatus` into ROS2 action terminal states.

Example of this is shown below:

```cpp
LoopStatus loop_inner()
{
  ++looped_for_;
  if (looped_for_ >= loop_max_) {
    return LoopStatus::SUCCESS;
  }
  return LoopStatus::RUNNING;
}
```

Additionally the C++ action server owns its execution thread and exposes `request_shutdown()` so executables can abort an active goal cleanly before shutting the ROS context down.

When necessary values are extracted and saved in private variables to store for usage later which may require duplicate checking of values and conditionals. An example of this is extracting a value from the JSON goal before the loop starts:

```cpp
bool on_goal_received(const Json & goal)
{
  loop_max_ = goal.value("loop_max", 25);
  return loop_max_ > 0;
}
```

# Useful Docs

These examples are very useful in seeing how ROS recommends doing this stuff.
- [Link for Action Client Examples](https://github.com/ros2/examples/tree/master/rclcpp/actions/minimal_action_client)
- [Link for Action Server Examples](https://github.com/ros2/examples/tree/humble/rclcpp/actions/minimal_action_server)

CancelGoal Relevant Docs:

- [CancelGoal Underlying Message](https://docs.ros2.org/foxy/api/action_msgs/srv/CancelGoal.html)
