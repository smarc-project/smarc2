# smarc_action_base
Library that enforces ROS2 action-client interfaces be implemented using Python Abstract Base Class.
The library intends to abstract and simplify the registering of callbacks and hide some of the async complexity from the user. 

## Abstractions
### Action Type
This is a simple wrapper around ROS2 action type. It enables type based access to empty `Goal`, `Feedback`, `Result` with type hinting which should enable faster development.

    - ROS type will be validated on instantiation with clarifying message added onto ROS's error message

## Method
Async callback functions are wrapped in a simplified decorator like pattern preventing user callbacks from being called directly. Instead they are called through a nested function that enables `Future`'s to be unpacked and abstracted away from the user. Example of this is shown below:
```python

    def _wrap_result_callback(self, future: Future):
        """Simplifies result response callback extracting values from future."""
        result: ActionType.Result = future.result().result
        status: GoalStatus = future.result().status
        self.result_callback(result, status)
```

Additionally type hints have been added to hopefully improve LSP integration for all downstream and prevent large amounts of doc searching.
