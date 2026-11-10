# smarc_action_base
# How do I use this?

That question is better answered by `behaviours/go_to_geopoint` than in this README. Unless you intend to make additions to the abstract base classes it is recommended to review the implementation shown there to understand how to use `smarc_action_base`.

## GentlerActionServer and GentlerActionClient

Both sides of `smarc_msgs/action/BaseAction` (goal: JSON string, feedback: string, result: bool) without subclassing anything.

`GentlerActionServer` takes your callbacks (`on_goal_received`, `on_cancel_received`, `prepare_loop`, `loop_inner`, `give_feedback`) and runs the goal loop for you. See `behaviours/evolo/evolo_deploy_at` for a server.

`GentlerActionClient` is the client you poll from your own loop:

```python
from smarc_action_base.gentler_action_client import GentlerActionClient

client = GentlerActionClient(node, 'move_to', timeout_s=120.0)

if client.server_alive() and client.send(json.dumps({'lat': 59.3, 'lon': 18.1})):
    report = client.poll()
    while report.running:
        node.get_logger().info(report.feedback)
        ...                       # spin, sleep, whatever your loop does
        report = client.poll()
    print(report.succeeded, report.state, report.elapsed_s, report.timed_out)

client.get_ready()                # forget this goal, allow the next send()
```

- `server_alive()` waits once for the server and moves the client to `READY` or `DISCONNECTED`.
- `send()` only works from `READY` and returns `False` otherwise.
- `cancel()` asks the server to stop. A cancel sent before the server has answered the goal request is kept and sent once the goal is accepted.
- `poll()` returns a `ClientReport` (`state`, `feedback`, `elapsed_s`, `timed_out`). With `timeout_s` set, `poll()` cancels the goal client-side when the server takes longer than that.
- `GentlerActionClient.RUNNING_STATES` and `GentlerActionClient.FAILURE_STATES` are the two sets of states a loop cares about; `GentlerActionClient.States.DONE` is the only success. One import covers all of it.

`A_ActionClient` in `bt_action_client_action.py` wraps this client as a py_trees behaviour for the trees that still use one.

Tests live in `tests/` and run against a real server on a private `ROS_DOMAIN_ID`: `python3 -m pytest` from this directory, or `colcon test --packages-select smarc_action_base`.

# Library that enforces ROS2 action-client interfaces be implemented using Python Abstract Base Class.
The library intends to abstract and simplify the registering of callbacks and hide some of the async complexity from the user. 

## Abstractions
### Action Type
This is a simple wrapper around ROS2 action type. It enables type based access to empty `Goal`, `Feedback`, `Result` with type hinting which should enable faster development.

    - ROS type will be validated on instantiation with clarifying message added onto ROS's error message

Additionally, ROS type error messages with Action Types were improved to help the user understand that they are passing in the incorrect ROS type.

### ActionXXX Types
These are completely hollow types to appease the type linter in Python. They all technically inherit from `Protocol` and `Msg` but it is safe to ignore these unless there are issues with type hints.

## Method
Async callback functions are wrapped in a simplified decorator like pattern preventing user callbacks from being called directly. Instead they are called through a nested function that enables `Future`'s to be unpacked and abstracted away from the user. Example of this is shown below:

```python

    def _wrap_result_callback(self, future: Future):
        """Simplifies result response callback extracting values from future."""
        result: ActionType.Result = future.result().result
        status: GoalStatus = future.result().status
        self.result_callback(result, status)
```

Additionally type hints have been added to improve LSP integration for all downstream and prevent large amounts of doc searching.

When necessary values are extracted and saved in private variables to store for usage later which may require duplicate checking of values and conditionals. An example of this is extracting goal handles before the user checks if the goal is accepted.

```python
    def _wrap_goal_response_callback(self, future: Future):
        """Simplifies goal response callback extracting values from future."""
        self._goal_handle = future.result()
        if self._goal_handle.accepted:
            self._get_result()
        # calling inheritors function
        self.goal_response_callback(self._goal_handle)
```

# Useful Docs

These examples are very useful in seeing how ROS recommends doing this stuff.
- [Link for Action Client Examples](https://github.com/ros2/examples/tree/master/rclpy/actions/minimal_action_client/examples_rclpy_minimal_action_client)
- [Link for Action Server Examples](https://github.com/ros2/examples/tree/humble/rclpy/actions/minimal_action_server/examples_rclpy_minimal_action_server)

CancelGoal Relevant Docs:

-[CancelGoal Underlying Message](https://docs.ros2.org/foxy/api/action_msgs/srv/CancelGoal.html) 
