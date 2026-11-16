# TODO: simple SAM controller
# pitch-depth control
# velocity control
from sam_diving_controller.controllers.PIDControl import PIDControl
from sam_captain.control_type import ControlState, ActuatorCmd

class SAMSimpleController:
    """Run SAM's PIDs and allocate their requested effort to actuator commands."""

    def __init__(self, cap) -> None:
        self.cap = cap
        # TODO: Import SAMControlAlloc from .SAMControlAlloc and create one
        # self.alloc = SAMControlAlloc(cap), owned by this controller.
        # TODO: independent PID instances
        # TODO: surge pid
        self.surge_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        # TODO: depth pid
        self.depth_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        # TODO: pitch pid
        self.pitch_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0)
        pass

    def update(self):
        """Compute PID efforts, allocate them, and return ActuatorCmd to captain."""
        # TODO: Get current state, desired state and dt from captain's interface.
        # Define that interface before adding calls to cap.
        # TODO: Run the three PIDs in this controller:
        # surge PID -> X [N], depth PID -> Z [N], pitch PID -> M [N m].
        # Configure their gains/limits in effort units; the present placeholders
        # and the diving controller's actuator-unit tuning need conversion.
        # TODO: Import RequestedEffort from .control_type and finish with:
        # requested = RequestedEffort(surge=X, heave=Z, pitch=M)
        # return self.alloc.allocate(requested)
        # Captain calls only controller.update() and publishes its ActuatorCmd;
        # the controller owns the call to allocate().
        pass

    def reset(self):
        """Resets PID"""
        self.surge_pid.reset()
        self.depth_pid.reset()
        self.pitch_pid.reset()

