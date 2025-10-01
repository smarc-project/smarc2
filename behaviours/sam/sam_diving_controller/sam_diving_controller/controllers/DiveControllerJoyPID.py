from sam_diving_controller.DiveController import PIDControl
from sam_diving_controller.controllers.DiveControllerInterface import DiveControllerInterface

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference

from smarc_modelling.control.control import *


class DiveControllerJoyPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub
        self._dt = rate
        self.param = param

        super().__init__(self._node, self._dive_pub, self._dive_sub, self.param, self._dt)

        self._depth_vbs_pid = PIDControl(Kp=self.param['vbs_pid_kp'],
                                         Ki=self.param['vbs_pid_ki'],
                                         Kd=self.param['vbs_pid_kd'],
                                         Kaw=self.param['vbs_pid_kaw'],
                                         u_neutral=self.param['vbs_u_neutral'],
                                         u_min=self.param['vbs_u_min'],
                                         u_max=self.param['vbs_u_max'])
        self._pitch_lcg_pid = PIDControl(Kp=self.param['lcg_pid_kp'],
                                         Ki=self.param['lcg_pid_ki'],
                                         Kd=self.param['lcg_pid_kd'],
                                         Kaw=self.param['lcg_pid_kaw'],
                                         u_neutral=self.param['lcg_u_neutral'],
                                         u_min=self.param['lcg_u_min'],
                                         u_max=self.param['lcg_u_max'])
        self._pitch_tv_pid = PIDControl(Kp=self.param['tv_pid_kp'],
                                        Ki=self.param['tv_pid_ki'],
                                        Kd=self.param['tv_pid_kd'],
                                        Kaw=self.param['tv_pid_kaw'],
                                        u_neutral=self.param['tv_u_neutral'],
                                        u_min=self.param['tv_u_min'],
                                        u_max=self.param['tv_u_max'])

        self._loginfo("Dive Controller created")

    def update(self):
        """
        This is where all the magic happens.
        """
        # Get setpoints
        depth_setpoint = self._dive_sub.get_joy_depth_setpoint()
        pitch_setpoint = self._dive_sub.get_joy_pitch_setpoint()

        # Get current states
        current_depth = self._dive_sub.get_sensor_depth()
        current_pitch = self._dive_sub.get_sensor_pitch()

        if depth_setpoint is None:
            self._loginfo_once("No depth setpoint received")
            return

        if pitch_setpoint is None:
            self._loginfo("No pitch setpoint yet")
            return

        if current_depth is None:
            self._loginfo("No depth measurement yet")
            return

        if current_pitch is None:
            self._loginfo("No pitch measurement yet")
            return

        # Sketchy minus signs...
        depth_setpoint *= -1.0
        current_depth *= -1.0

        # This is due to the fact that we want to move the LCG forward when
        # having a negative real pitch error.

        # FIXME: This probably shouldn't be there now. The IMU is fixed
        pitch_setpoint *= -1.0
        current_pitch *= -1.0

        # Choose active vs. static diving based on dive pitch angle
        # s = f"Control States:\n"
        # s += f"Depth: {current_depth}, Pitch: {current_pitch}\n"
        # s += f"SP depth: {depth_setpoint}, pitch: {pitch_setpoint}\n"
        # s += f"Errors: depth: {depth_error}, pitch: {pitch_error}\n"
        # s += f"VBS: {u_vbs}, LCG: {u_lcg}, tv: {u_tv_ver}\n"
        # s += f"[-----]"
        # self._loginfo(s)

        self._loginfo(f"Joy Update: Begin Control Loop")

        depth_error = depth_setpoint - current_depth

        if np.abs(depth_error) <= 0.5:
            self._loginfo("Active Diving")

            u_vbs_raw = self.param['vbs_u_neutral']
            u_lcg_raw = self.param['lcg_u_neutral']
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_ver, pitch_error, u_tv_ver_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            self._loginfo("Static Diving")
            u_tv_ver_raw = self.param['tv_u_neutral']
            u_tv_ver = u_tv_ver_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

        s = f"Control States:\n"
        s += f"Depth: {current_depth:.3f}, Pitch: {current_pitch:.3f}\n"
        s += f"SP depth: {depth_setpoint}, pitch: {pitch_setpoint}\n"
        s += f"Errors: depth: {depth_error:.3f}, pitch: {pitch_error:.3f}\n"
        s += f"VBS: {u_vbs:.3f}, LCG: {u_lcg:.3f}, tv: {u_tv_ver:.3f}\n"
        s += f"[-----]"
        self._loginfo(s)

        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_stern(u_tv_ver)  # FIXME: Check if you need a sign or not.

        # Convenience Topics
        self._ref = ControlReference()
        self._ref.z = depth_setpoint
        self._ref.pitch = pitch_setpoint

        self._error = ControlError()
        self._error.z = depth_error
        self._error.pitch = pitch_error

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_tv_ver

        return
