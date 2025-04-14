# smarc_action_base
# How do I use this?

That question is better answered by `behaviours/go_to_geopoint` than in this README. Unless you intend to make additions to the abstract base classes it is recommended to review the implementation shown there to understand how to use `smarc_action_base`.

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
