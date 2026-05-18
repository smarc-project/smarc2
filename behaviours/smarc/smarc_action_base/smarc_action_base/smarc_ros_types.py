from typing import Protocol


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
