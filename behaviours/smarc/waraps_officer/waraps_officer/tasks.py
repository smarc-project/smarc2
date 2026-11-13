"""WARA-PS task names and the officer's records. No rclpy."""

from dataclasses import dataclass


class WaraPSTaskStates:
    STARTED = 'started'
    RUNNING = 'running'
    PAUSED = 'paused'
    RESUMED = 'resumed'
    ENOUGH = 'enough'
    ABORTED = 'aborted'
    ERROR = 'error'
    FINISHED = 'finished'


class WaraPSCommandSignals:
    ABORT = '$abort'
    ENOUGH = '$enough'
    PAUSE = '$pause'
    CONTINUE = '$continue'


TASK_SIGNALS = (
    WaraPSCommandSignals.ABORT,
    WaraPSCommandSignals.ENOUGH,
    WaraPSCommandSignals.PAUSE,
    WaraPSCommandSignals.CONTINUE,
)


def waraps_task_name(ros_name: str) -> str:
    """The name WARA-PS uses for an action server.

    The heartbeat carries the ROS action name (``/sam0/move_to``). The GUI
    sends the last segment with underscores written as hyphens.
    """
    return ros_name.rstrip('/').split('/')[-1].replace('_', '-')


@dataclass(frozen=True)
class AvailableTask:
    name: str
    ros_name: str
    last_seen: float


@dataclass
class ExecutingTask:
    uuid: str
    name: str
    ros_name: str
    params: dict
    description: str
    status: str
    client: object
    com_uuid: str
    tst_uuid: str | None
    timeout_s: float | None
    stop_reason: str | None = None
    cancel_refused: bool = False
