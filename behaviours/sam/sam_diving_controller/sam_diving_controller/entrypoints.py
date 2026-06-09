# my_pkg/entrypoints.py
from __future__ import annotations

from .dive_runner import Components, Rates, run_mode

from .ParamUtils import DivingModelParam
from .DiveSub import DiveSub
from .DivePub import DivePub
# Unused, analyticalsamsim imports smarc_modelling as a
# pure py package, which is a PITA when using PID?
# from .SimPub import SimPub
# from .AnalyticalSAMSim import AnalyticalSAMSim
from .ConveniencePub import ConveniencePub

from .controllers.DiveControllerPID import DiveControllerPID

from .controllers.DiveControllerJoyPID import DiveControllerJoyPID

from .ActionServerDiveSub import DiveActionServerSub, HydropointServer, MPCPathServer, PIDPathServer
from smarc_action_base.smarc_action_base import ActionType
from smarc_msgs.action import BaseAction
from smarc_msgs.msg import Topics as SMaRCTopics


# --- Builders (wire-up per mode) ---

def _build_main(node, rates: Rates) -> Components:

    dive_pub = DivePub(node)
    dive_sub = DiveSub(node, dive_pub)

    dive_controller = DiveControllerMPC(node, dive_pub, dive_sub, rates.dive_controller)
    # dive_controller = DiveControllerPID(node, dive_pub, dive_sub, rates.dive_controller)

    return Components(dive_pub=dive_pub, dive_controller=dive_controller, dive_sub=dive_sub)


def _build_joy_depth(node, rates: Rates) -> Components:

    param = DivingModelParam(node).get_param()
    dive_sub = DiveSub(node, param)
    dive_pub = DivePub(node, dive_sub, param)
    dive_controller = DiveControllerJoyPID(node, dive_pub, dive_sub, param, rates.dive_controller)

    return Components(
        dive_pub=dive_pub,
        dive_controller=dive_controller,
        dive_sub=dive_sub,
        dive_pub_update=dive_pub.joy_update,  # <- special case handled cleanly
    )


#def _build_sim_sam(node, rates: Rates) -> Components:
#
#    param = DivingModelParam(node).get_param()
#    action_type = ActionType(BaseAction)
#    heartbeat_topic = SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC
#
#    dive_sub = HydropointServer(node, "go_to_hydropoint", action_type, param, heartbeat_topic)
#    dive_pub = SimPub(node, dive_sub, param)
#    dive_controller = AnalyticalSAMSim(node, dive_pub, dive_sub, param, rates.dive_controller)
#    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)
#
#    return Components(dive_pub=dive_pub, dive_controller=dive_controller,
#                      dive_sub=dive_sub, convenience_pub=convenience_pub)
#

def _build_pid_wp_following(node, rates: Rates) -> Components:

    param = DivingModelParam(node).get_param()
    action_type = ActionType(BaseAction)
    heartbeat_topic = SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC

    dive_sub = DiveActionServerSub(node, "auv_depth_move_to", action_type, param, heartbeat_topic)
    dive_pub = DivePub(node, dive_sub, param)
    dive_controller = DiveControllerPID(node, dive_pub, dive_sub, param, rates.dive_controller)
    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    return Components(
        dive_pub=dive_pub,
        dive_controller=dive_controller,
        dive_sub=dive_sub,
        convenience_pub=convenience_pub,
    )

def _build_pid_trajectory_tracking(node, rates: Rates) -> Components:
    param = DivingModelParam(node).get_param()
    action_type = ActionType(BaseAction)
    heartbeat_topic = SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC

    dive_sub = PIDPathServer(node, "auv_trajectory_tracking", action_type, param)
    dive_pub = DivePub(node, dive_sub, param)
    dive_controller = DiveControllerPID(node, dive_pub, dive_sub, param, rates.dive_controller)
    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    return Components(dive_pub=dive_pub, dive_controller=dive_controller,
                      dive_sub=dive_sub, convenience_pub=convenience_pub)

def _build_mpc_wp_following(node, rates: Rates) -> Components:

    param = DivingModelParam(node).get_param()
    action_type = ActionType(BaseAction)
    heartbeat_topic = SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC

    dive_sub = HydropointServer(node, "go_to_hydropoint", action_type, param, heartbeat_topic)
    dive_pub = DivePub(node, dive_sub, param)
    dive_controller = DiveControllerMPC(node, dive_pub, dive_sub, param,
                                        ref_is_trajectory=False,
                                        rate=rates.dive_controller,)
    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    return Components(
        dive_pub=dive_pub,
        dive_controller=dive_controller,
        dive_sub=dive_sub,
        convenience_pub=convenience_pub,
    )


def _build_mpc_trajectory_tracking(node, rates: Rates) -> Components:

    param = DivingModelParam(node).get_param()
    action_type = ActionType(BaseAction)

    dive_sub = MPCPathServer(node, "auv_trajectory_tracking", action_type, param)
    dive_pub = DivePub(node, dive_sub, param)
    dive_controller = DiveControllerMPC(
        node, dive_pub, dive_sub, param,
        ref_is_trajectory=True,
        rate=rates.dive_controller,
    )
    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    return Components(dive_pub=dive_pub, dive_controller=dive_controller,
                      dive_sub=dive_sub, convenience_pub=convenience_pub)


# --- Console-script entry points (module-level functions) ---
def main():
    run_mode(node_name="DivingNode", build=_build_main)

def joy_depth():
    run_mode(node_name="JoyDivingNode", build=_build_joy_depth)

#def sim_sam():
#    run_mode(node_name="ActionServerDivingNode", build=_build_sim_sam)

def pid_wp_following():
    run_mode(node_name="PidWpFollowingNode", 
             build=_build_pid_wp_following,
             log_banner="PID Waypoint Following")

def pid_trajectory_tracking():
    run_mode(node_name="PidTrajectoryTrackingNode",
             build=_build_pid_trajectory_tracking,
             log_banner="PID Trajectory Tracking")

def mpc_wp_following():
    from .controllers.DiveControllerMPC import DiveControllerMPC
    run_mode(node_name="MpcWpFollowingNode",
             build=_build_mpc_wp_following,
             log_banner="MPC Waypoint Following")

def mpc_trajectory_tracking():
    from .controllers.DiveControllerMPC import DiveControllerMPC
    run_mode(node_name="MpcTrajectoryTracking",
             build=_build_mpc_trajectory_tracking,
             log_banner="MPC Trajectory tracking")
