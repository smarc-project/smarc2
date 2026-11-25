"""Check silence in status-only mode and one-shot disengagement output."""

from unittest.mock import Mock

from rclpy.time import Time
from sam_msgs.msg import Topics as SamTopics

from sam_captain.SAMActuatorPublisher import SAMActuatorPublisher
from sam_captain.control_type import ActuatorCmd, ControlReference, ControlState
from sam_captain.sam_captain import SAMCaptain


def make_control_captain(enabled=True):
    captain = SAMCaptain.__new__(SAMCaptain)
    captain.control_output_enabled = enabled
    captain._controller = Mock()
    captain._actuator_publisher = Mock()
    captain._control_active = False
    captain.control_command = None
    captain.control_state = None
    captain.control_reference = None
    captain._last_control_time = Time(seconds=1)
    captain.get_clock = Mock()
    captain.get_clock.return_value.now.side_effect = [
        Time(nanoseconds=1_100_000_000 + i * 100_000_000) for i in range(10)
    ]
    captain._controller.alloc.neutral.return_value = ActuatorCmd(0, 0, 0, 50, 50)
    return captain


def activate(captain):
    captain.control_state = ControlState(0.0, 1.0, 0.0)
    captain.control_reference = ControlReference(0.2, 2.0, 0.1, enabled=True)
    captain._controller.update.return_value = ActuatorCmd(20, 20, 0, 60, 45)
    captain._control_callback()


def test_status_only_discards_cached_output_even_with_ready_inputs():
    captain = make_control_captain(enabled=False)
    captain.control_command = ActuatorCmd(100, 100, 0, 70, 40)
    activate(captain)
    captain._control_callback()

    assert captain.control_command is None
    assert captain._last_control_time is None
    captain._controller.update.assert_not_called()
    captain._actuator_publisher.publish.assert_not_called()


def test_enabled_captain_with_no_inputs_never_publishes_neutral():
    captain = make_control_captain()
    captain._control_callback()
    captain._control_callback()

    captain._controller.update.assert_not_called()
    captain._controller.reset.assert_not_called()
    captain._actuator_publisher.publish.assert_not_called()


def test_active_output_is_published_by_control_loop():
    captain = make_control_captain()
    activate(captain)

    captain._actuator_publisher.publish.assert_called_once_with(
        captain._controller.update.return_value
    )
    assert captain._control_active


def test_disable_neutralizes_once_then_stays_silent():
    captain = make_control_captain()
    activate(captain)
    captain.control_reference = ControlReference(0.2, 2.0, 0.1, enabled=False)

    captain._control_callback()
    captain._control_callback()

    assert captain._actuator_publisher.publish.call_count == 2
    assert captain._actuator_publisher.publish.call_args.args == (
        captain._controller.alloc.neutral.return_value,
    )
    captain._controller.reset.assert_called_once()
    assert captain.control_command is None
    assert not captain._control_active


def test_missing_state_disengages_and_new_inputs_can_resume():
    captain = make_control_captain()
    activate(captain)
    captain.control_state = None
    captain._control_callback()
    captain._control_callback()
    activate(captain)

    assert captain._actuator_publisher.publish.call_count == 3
    assert captain._controller.update.call_count == 2
    assert captain._control_active


def test_first_control_tick_is_silent():
    captain = make_control_captain()
    captain._last_control_time = None
    activate(captain)

    captain._controller.update.assert_not_called()
    captain._actuator_publisher.publish.assert_not_called()


def test_actuator_publisher_emits_one_command_without_a_timer():
    captain = Mock(control_output_enabled=True)
    outputs = [Mock() for _ in range(4)]
    captain.create_publisher.side_effect = outputs
    captain.get_clock.return_value.now.return_value = Time(seconds=2)
    publisher = SAMActuatorPublisher(captain)

    publisher.publish(ActuatorCmd(12, -8, 0, 55, 45))

    assert [call.args[1] for call in captain.create_publisher.call_args_list] == [
        SamTopics.VBS_CMD_TOPIC, SamTopics.LCG_CMD_TOPIC,
        SamTopics.THRUSTER1_CMD_TOPIC, SamTopics.THRUSTER2_CMD_TOPIC,
    ]
    assert outputs[0].publish.call_args.args[0].value == 55.0
    assert outputs[1].publish.call_args.args[0].value == 45.0
    assert outputs[0].publish.call_args.args[0].header.stamp.sec == 2
    assert outputs[2].publish.call_args.args[0].rpm == 12
    assert outputs[3].publish.call_args.args[0].rpm == -8
    captain.create_timer.assert_not_called()


def test_actuator_publisher_refuses_output_when_disabled():
    captain = Mock(control_output_enabled=False)
    outputs = [Mock() for _ in range(4)]
    captain.create_publisher.side_effect = outputs
    publisher = SAMActuatorPublisher(captain)
    publisher.publish(ActuatorCmd(12, 12, 0, 55, 45))

    for output in outputs:
        output.publish.assert_not_called()
