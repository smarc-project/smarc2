from typing import TypeVar,Protocol
from rclpy.type_support import check_for_type_support

class Msg(Protocol):
    """Generic Message Alias."""
    pass

class ActionResult(Msg, Protocol):
    """Action Type Result Message"""
    pass
    

class ActionFeedback(Msg, Protocol):
    """Action Type Feedback Message"""
    pass

class ActionGoal(Msg, Protocol):
    """Action Type Goal Message"""
    pass

class ActionType:
    """Wrapper around ROS Action Type to provide easy dot completion.

    Attributes:
        Result: empty result message
        Feedback: empty feedback message
        Goal: empty goal message
    """

    def __init__(self, action_type):
        self._action_type = action_type
        self.validate_type()

    def validate_type(self):
        """Evaluates whether provided action type is a valid ROS action type.

        Raises:
            AttributeError: Provides additional context to user to help debug ROS error.
        """
        try:
            check_for_type_support(self._action_type)
        except AttributeError as err:
            err_str = "Provided action_type is not a valid ROS action type.\n"
            err_str += "Action types generally should be of type `from some_interface.action import MyAction"
            raise AttributeError(err_str) from err


    @property
    def ros_type(self):
        """Underlying ROS type.

        Returns:
            action: ROS action type
        """
        return self._action_type

    @property
    def Result(self) -> ActionResult:
        """Empty results message."""
        return self._action_type.Result()

    @property
    def Feedback(self) -> ActionFeedback:
        """Empty feedback message."""
        return self._action_type.Feedback()

    @property
    def Goal(self) -> ActionGoal:
        """Empty goal message."""
        return self._action_type.Goal()


