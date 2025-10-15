from sam_diving_controller.IDivePub import ActuatorStates

from smarc_control_msgs.msg import ControlInput, ControlReference

class DiveControllerInterface:

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub =dive_sub
        self._dive_pub =dive_pub
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._input = None
        self._dive_mode = None
        self.waypoint = None

        self.param = param

    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def _logwarn(self, s):
        self._node.get_logger().warn(s)

    def _loginfo_once(self, s):
        self._node.get_logger().info(s, once=True)


    def _set_actuators_neutral(self):
        """
        Setting all actuators to neutral.
        """

        actuator_state = self._dive_pub.get_actuator_states()

        if actuator_state == ActuatorStates.ENGAGED:
            u_vbs_neutral = self.param['vbs_u_neutral']
            u_lcg_neutral = self.param['lcg_u_neutral']
            u_tv_hor_neutral = self.param['tv_u_neutral']
            u_tv_ver_neutral = self.param['tv_u_neutral']
            u_rpm_neutral = self.param['rpm_u_neutral']

            self._dive_pub.set_vbs(u_vbs_neutral)
            self._dive_pub.set_lcg(u_lcg_neutral)
            self._dive_pub.set_thrust_vector(u_tv_hor_neutral, -u_tv_ver_neutral)
            self._dive_pub.set_rpm(u_rpm_neutral, u_rpm_neutral)

            self._input = ControlInput()
            self._input.vbs = u_vbs_neutral
            self._input.lcg = u_lcg_neutral
            self._input.thrustervertical = u_tv_ver_neutral
            self._input.thrusterhorizontal = u_tv_hor_neutral
            self._input.thrusterrpm = float(u_rpm_neutral)

            self._dive_pub.set_actuator_states(ActuatorStates.NEUTRAL, "DC")


    def _set_actuators_emergency(self):
        """
        Setting all actuators to neutral.
        """

        u_vbs_emergency = self.param['vbs_u_emergency']
        u_lcg_emergency= self.param['lcg_u_emergency']
        u_tv_hor_emergency= self.param['tv_u_emergency']
        u_tv_ver_emergency= self.param['tv_u_emergency']
        u_rpm_emergency= self.param['rpm_u_emergency']

        self._dive_pub.set_vbs(u_vbs_emergency)
        self._dive_pub.set_lcg(u_lcg_emergency)
        self._dive_pub.set_thrust_vector(u_tv_hor_emergency, -u_tv_ver_emergency)
        self._dive_pub.set_rpm(u_rpm_emergency, u_rpm_emergency)

        self._input = ControlInput()
        self._input.vbs = u_vbs_emergency
        self._input.lcg = u_lcg_emergency
        self._input.thrustervertical = u_tv_ver_emergency
        self._input.thrusterhorizontal = u_tv_hor_emergency
        self._input.thrusterrpm = float(u_rpm_emergency)

    def get_wp(self):
        '''
        For the ConveniencePub
        '''
        if self.waypoint is None:
            return None

        return self.waypoint

    def get_state(self):
        '''
        For the ConveniencePub
        '''
        if self._current_state is None:
            return None

        #state = ControlState()
        #state.header.frame_id = self._current_state.header.frame_id
        #state.header.stamp = self._current_state.header.stamp
        #state.pose.x = self._current_state.pose.pose.position.x
        #state.pose.y = self._current_state.pose.pose.position.y
        #state.pose.z = self._current_state.pose.pose.position.z

        #rpy = euler_from_quaternion([
        #    self._current_state.pose.pose.orientation.x,
        #    self._current_state.pose.pose.orientation.y,
        #    self._current_state.pose.pose.orientation.z,
        #    self._current_state.pose.pose.orientation.w])

        #state.pose.roll = rpy[0]
        #state.pose.pitch = rpy[1]
        #state.pose.yaw = rpy[2]

        # TODO: Add the velocity

        return self._current_state

    def get_ref(self):
        return self._ref

    def get_error(self):
        return self._error

    def get_input(self):
        return self._input

    def get_dive_mode(self):
        return self._dive_mode
