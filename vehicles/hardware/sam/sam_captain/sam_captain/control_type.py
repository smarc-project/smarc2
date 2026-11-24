"""ROS-independent values exchanged by SAM's control components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlState:
    """Measured body surge speed, depth positive down, and nose-up pitch."""

    surge_m_s: float
    depth_m: float
    pitch_rad: float


@dataclass(frozen=True)
class ControlReference:
    """Desired state using ControlState conventions; disabled by default."""

    surge_m_s: float
    depth_m: float
    pitch_rad: float
    enabled: bool = False


@dataclass(frozen=True)
class ActuatorCmd:
    """Allocated RPM, vector angle [rad], and VBS/LCG percentage points."""

    rpm_front: int
    rpm_back: int
    thrust_vect: float  # Zero for the initial decoupled allocator.
    vbs: float  # 0--100 percentage points.
    lcg: float  # 0--100 percentage points.


@dataclass(frozen=True)
class RequestedEffort:
    """Requested X/Z/M using the initial allocator's near-level convention."""

    surge: float  # X [N], positive forward.
    heave: float  # Z [N], positive down.
    pitch: float  # M [N m], positive nose-up.
