# TODO: simple SAM controller
# pitch-depth control
# velocity control
from sam_diving_controller.controllers.PIDControl import PIDControl
from sam_captain.SAMControlAlloc import SAMControlAlloc
from sam_captain.control_type import ControlState, ActuatorCmd, ControlReference, RequestedEffort

class SAMSimpleController:
    """Run SAM's PIDs and allocate their requested effort to actuator commands."""

    def __init__(self, cap) -> None:
        self.cap = cap
        # independent PID instances
        self.surge_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        self.depth_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        self.pitch_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        self.alloc = SAMControlAlloc(cap)

    def update(self):
        """
        Read the captain's inputs, compute X/Z/M, and return actuator commands.
        The captain supplies control_state, control_reference, and control_dt,
        and checks enable, input validity, freshness, and dt before calling.
        """
        state: ControlState = self.cap.control_state
        reference: ControlReference = self.cap.control_reference
        dt = self.cap.control_dt

        surge, _, _ = self.surge_pid.get_control(
            state.surge_m_s, reference.surge_m_s, dt)
        heave, _, _ = self.depth_pid.get_control(
            state.depth_m, reference.depth_m, dt)
        pitch, _, _ = self.pitch_pid.get_control(
            state.pitch_rad, reference.pitch_rad, dt)

        requested = RequestedEffort(surge=surge, heave=heave, pitch=pitch)
        return self.alloc.allocate(requested)

    def reset(self):
        """Resets PID"""
        self.surge_pid.reset()
        self.depth_pid.reset()
        self.pitch_pid.reset()

