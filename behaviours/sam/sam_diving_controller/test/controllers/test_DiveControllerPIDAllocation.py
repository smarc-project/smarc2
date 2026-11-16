from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Odometry

from sam_captain.SAMControlAlloc import RequestedEffort
from sam_diving_controller.IDivePub import ActuatorStates, MissionStates
from sam_diving_controller.ParamUtils import DivingModelParam
from sam_diving_controller.controllers.DiveControllerPID import DiveControllerPID


def make_controller(enabled=True, **overrides):
    values = {}
    node = Mock()
    node.declare_parameter.side_effect = lambda name, value: values.setdefault(name, value)

    def get_parameter(name):
        value = values[name]
        return SimpleNamespace(value=value, get_parameter_value=lambda: SimpleNamespace(
            double_value=value, integer_value=value))

    node.get_parameter.side_effect = get_parameter
    param = DivingModelParam(node).get_param()
    param.update(allocation_test_enabled=enabled, vbs_u_neutral=50.0,
                 vbs_pid_ki=0.0, vbs_pid_kd=0.0,
                 lcg_pid_ki=0.0, lcg_pid_kd=0.0)
    param.update(overrides)
    state = Odometry()
    state.pose.pose.position.z = -2.0
    waypoint = Pose()
    waypoint.position.z = -3.0
    waypoint.orientation.w = 1.0
    global_waypoint = PoseStamped()
    global_waypoint.pose = waypoint
    sub = Mock()
    sub.get_mission_state.return_value = MissionStates.RUNNING
    sub.has_waypoint.return_value = True
    sub.get_states.return_value = state
    sub.get_states_in_dr.return_value = state
    sub.get_depth_setpoint.return_value = -3.0
    sub.get_depth.return_value = -2.0
    sub.get_pitch_setpoint.return_value = 0.0
    sub.get_pitch.return_value = 0.0
    sub.get_heading_setpoint.return_value = 0.0
    sub.get_heading.return_value = 0.0
    sub.get_dive_pitch.return_value = 0.0
    sub.get_distance.return_value = 2.0
    sub.get_waypoint_in_odom.return_value = waypoint
    sub.get_waypoint.return_value = global_waypoint
    pub = Mock()
    pub.get_actuator_states.return_value = ActuatorStates.ENGAGED
    return DiveControllerPID(node, pub, sub, param), pub, sub


def test_static_bridge_preserves_pid_output_and_zeroes_propulsion():
    controller, pub, _ = make_controller()
    controller.update()
    # ENU z=-2 -> -3 is a positive-down depth error of +1 m.
    pub.set_vbs.assert_called_with(90.0)
    pub.set_lcg.assert_called_with(50.0)
    pub.set_rpm.assert_called_with(0, 0)
    pub.set_thrust_vector.assert_called_with(0.0, -0.0)
    assert controller.get_allocation_result().residual == RequestedEffort(0, 0, 0)
    assert controller.get_input().vbs == 90.0


def test_test_mode_does_not_switch_to_active_near_depth_target():
    controller, pub, sub = make_controller()
    sub.get_depth_setpoint.return_value = -2.1
    controller.update()
    assert controller.get_dive_mode() == 'Static Allocation Test'
    pub.set_rpm.assert_called_with(0, 0)
    assert pub.set_vbs.call_args.args[0] == pytest.approx(54.0)


def test_rate_limit_and_pid_tracking_use_applied_percent():
    controller, pub, _ = make_controller(allocation_vbs_rate=2.0)
    controller.update()
    pub.set_vbs.assert_called_with(50.2)
    result = controller.get_allocation_result()
    assert result.limited[1]
    assert result.residual.heave > 0
    # PID already accounts for its own saturation; add only the downstream loss.
    assert controller._depth_vbs_pid._anti_windup == pytest.approx((50.2 - 90) * 0.1)


@pytest.mark.parametrize('mission', [MissionStates.PAUSED, MissionStates.CANCELLED,
                                    MissionStates.COMPLETED, MissionStates.NONE,
                                    MissionStates.REJECTED])
def test_nonrunning_states_neutralize_and_reset(mission):
    controller, pub, sub = make_controller()
    controller.update()
    pub.reset_mock()
    sub.get_mission_state.return_value = mission
    controller.update()
    pub.set_rpm.assert_called_with(0, 0)
    pub.set_vbs.assert_called_with(50.0)
    assert controller.get_allocation_result() is None
    assert controller._depth_vbs_pid._integral == 0


def test_emergency_uses_existing_emergency_commands():
    controller, pub, sub = make_controller()
    sub.get_mission_state.return_value = MissionStates.EMERGENCY
    controller.update()
    pub.set_vbs.assert_called_with(0.0)
    pub.set_rpm.assert_called_with(0, 0)
    assert controller.get_allocation_result() is None


@pytest.mark.parametrize('missing', ['state', 'waypoint', 'invalid_depth'])
def test_missing_or_invalid_inputs_do_not_keep_old_commands(missing):
    controller, pub, sub = make_controller()
    if missing == 'state':
        sub.get_states.return_value = None
    elif missing == 'waypoint':
        sub.has_waypoint.return_value = False
    else:
        sub.get_depth.return_value = float('nan')
    controller.update()
    pub.set_vbs.assert_called_with(50.0)
    assert controller.get_allocation_result() is None


def test_disabled_mode_keeps_existing_active_diving():
    controller, pub, sub = make_controller(enabled=False)
    sub.get_depth_setpoint.return_value = -2.1
    controller.update()
    assert controller.get_dive_mode() == 'Active Diving'
    assert pub.set_rpm.call_args.args[0] > 0
    assert controller.get_allocation_result() is None
