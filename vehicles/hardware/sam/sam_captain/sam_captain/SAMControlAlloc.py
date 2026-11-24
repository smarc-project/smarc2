"""Map the effort requested by SAMSimpleController to actuator commands."""

from math import ceil, floor

from sam_captain.control_type import ActuatorCmd, RequestedEffort


class SAMControlAlloc:
    def __init__(self, cap) -> None:
        # Unity starting values; confirm the active scene's signed gains/trim.
        # Efforts: X forward [N], Z down [N], M nose-up [N m], near level.
        # TODO: move this to a config file
        defaults = {
            'front_gain': 0.005,
            'back_gain': 0.005,
            'reverse_multiplier': 0.6,
            'vbs_gain': 997.0 * 9.81 * 0.00025 / 100.0,
            'lcg_gain': -2.7 * 9.81 * 0.00057,
            'vbs_trim': 50.0,
            'lcg_trim': 50.0,
            'heave_offset': 0.0,
            'pitch_offset': 0.0,
            'rpm_min': -400,
            'rpm_max': 800,
            'vbs_min': 0.0,
            'vbs_max': 100.0,
            'lcg_min': 0.0,
            'lcg_max': 100.0,
        }
        for name, default in defaults.items():
            parameter = f'allocation_{name}'
            if not cap.has_parameter(parameter):
                cap.declare_parameter(parameter, default)
            setattr(self, name, cap.get_parameter(parameter).value)

    def allocate(self, requested: RequestedEffort) -> ActuatorCmd:
        reverse_factor = self.reverse_multiplier if requested.surge < 0 else 1.0
        rpm = requested.surge / ((self.front_gain + self.back_gain) * reverse_factor)
        vbs = self.vbs_trim + (requested.heave - self.heave_offset) / self.vbs_gain
        lcg = self.lcg_trim + (requested.pitch - self.pitch_offset) / self.lcg_gain

        rpm = max(ceil(self.rpm_min), min(floor(self.rpm_max), round(rpm)))
        vbs = max(self.vbs_min, min(self.vbs_max, vbs))
        lcg = max(self.lcg_min, min(self.lcg_max, lcg))
        return ActuatorCmd(rpm_front=rpm, rpm_back=rpm, thrust_vect=0.0,
                           vbs=vbs, lcg=lcg)

    def neutral(self) -> ActuatorCmd:
        """
        Stop thrusters and command bounded trims, ignoring effort offsets.
        Trim commands do not necessarily produce zero net force or moment.
        """
        return ActuatorCmd(
            rpm_front=0,
            rpm_back=0,
            thrust_vect=0.0,
            vbs=max(self.vbs_min, min(self.vbs_max, self.vbs_trim)),
            lcg=max(self.lcg_min, min(self.lcg_max, self.lcg_trim)),
        )