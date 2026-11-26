"""The vehicle's health as the officer reads it, and the officer's own. No rclpy.

Both use the vehicle health values in ``Topics`` (``VEHICLE_HEALTH_*``).
"""

from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING

from smarc_msgs.msg import Topics

from waraps_officer.level1 import fresh
from waraps_officer.tasks import ExecutingTask, WaraPSTaskStates

if TYPE_CHECKING:
    from smarc_action_base.smarc_action_base import SMARCActionClient

STOPPING_STATES = (WaraPSTaskStates.ABORTED, WaraPSTaskStates.ENOUGH, WaraPSTaskStates.PAUSED)


def health_is_ready(value: int | None, stamp_s: float | None, now_s: float, timeout_s: float) -> bool:
    return value == Topics.VEHICLE_HEALTH_READY and fresh(stamp_s, now_s, timeout_s)


def officer_health(
    tasks: list[ExecutingTask],
    running_states: Collection[SMARCActionClient.States],
    cancelling: SMARCActionClient.States,
) -> int:
    """The officer's own health, using the vehicle health values.

    ERROR: a server refused a cancel and the action is still running.
    WAITING: a cancel was asked and has not been answered.
    READY: neither. A task that is simply running is READY.
    """
    if any(task.cancel_refused for task in tasks):
        return Topics.VEHICLE_HEALTH_ERROR
    for task in tasks:
        state = task.client.state
        if state is cancelling or (task.status in STOPPING_STATES and state in running_states):
            return Topics.VEHICLE_HEALTH_WAITING
    return Topics.VEHICLE_HEALTH_READY


def health_label(value: int | None, is_fresh: bool) -> str:
    """The word that goes into an abort's feedback text."""
    if not is_fresh:
        return 'silent'
    if value == Topics.VEHICLE_HEALTH_READY:
        return 'READY'
    if value == Topics.VEHICLE_HEALTH_WAITING:
        return 'WAITING'
    if value == Topics.VEHICLE_HEALTH_ERROR:
        return 'ERROR'
    return str(value)
