#!/usr/bin/python3

import numpy as np
import math

import tf2_geometry_msgs.tf2_geometry_msgs

from geometry_msgs.msg import PoseStamped, TransformStamped


class PIDControl:
    """
    From:  https://github.com/DoernerD/Python_Control/blob/main/src/PID_control.py
    To simplify the PIDModel by using this.
    """
    # TODO: Add anti-windup + saturations
    def __init__(self, Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._Kaw = Kaw

        # This also initializes all control variables
        self.reset()

    def get_control(self, x:float, x_ref:float, dt:float):
        """
        Returns the control input to the system given its current state x, its desired state x_ref
        and the time since last update dt in seconds.
        x and x_ref have to be 1 dimensional floats of the same quantity (e.g. current and desired
        heading angle)
        """
        self._error_prev = self._error
        self._error = x_ref - x
        self._integral = self._integral + self._error*dt
        self._derivative = (self._error - self._error_prev)/dt

        u = self._Kp*self._error + self._Ki*(self._integral - self._anti_windup) + self._Kd*self._derivative

        return u, self._error

    def reset(self):
        self._error = 0.0
        self._integral = 0.0
        self._anti_windup = 0.0
        self._derivative = 0.0
        self._error_prev = 0.0


class WaypointFollowing:

    def __init__(self, node, view, controller, rate=1/10):

        self._node = node
        self._controller = controller
        self._view = view
        self._dt = rate

        # FIXME: Are they defined in the view or somewhere s.t. we don't have to hardcode them here?
        self._u_tv_hor_min = -np.deg2rad(7)
        self._u_tv_hor_max = np.deg2rad(7)

        self._wp = None
        self._tf_base_link = None

        self._yaw_pid = PIDControl(Kp = 1.0, Ki = 0.0, Kd = 0.0, Kaw = 0.0)

        self._loginfo("WPF Controller created")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def update(self):
        """
        This is where all the magic happens.
        """
        # TODO: Add depth keeping controller as well.
        # TODO: Upgrade to dynamic diving
        self._wp = self._controller.get_waypoint()

        if self._wp is None:
            #self._loginfo("No waypoint received")
            return

        self._tf_base_link = self._controller.get_tf_base_link()

        if self._tf_base_link is None:
            self._loginfo("TF to base_link not yet available")
            return


#        if self._controller.get_mission_state() is None:
#            return
#        elif self._controller.get_mission_state() == "COMPLETED":
#            self._view.set_rpm(0)
#            self._view.set_thrust_vector(0.0, 0.0)
#            return
#        elif self._controller.get_mission_state() == "CANCELLED":
#            self._view.set_rpm(0)
#            self._view.set_thrust_vector(0.0, 0.0)
#            return

        mission_state = self._controller.get_mission_state()

        mission_state_str = f"WPF: {mission_state}"
        self._loginfo(mission_state_str)


        # TODO: Refactor the names
        # For heading, we don't need the state. 
        #x = self._controller.get_state()
        x_ref = self.transform_waypoint(self._wp)

        heading = self.get_heading(x_ref)
        heading_ref = 0.0

        distance = self.get_distance(x_ref)

        # NOTE: The - in the heading is due to the fact that the heading we calculate is already the error 
        # for a reference with 0. Usually we don't want this, here it's a special case.
        u_thrust_vector_horizontal, heading_error = self._yaw_pid.get_control(-heading, heading_ref, self._dt)

        u_tv_hor_lim = self.limit_control_action(u_thrust_vector_horizontal, self._u_tv_hor_min, self._u_tv_hor_max)

        u_rpm = self._controller.get_requested_rpm()

        # TODO: Compute anti windup here

        self._view.set_thrust_vector(-u_tv_hor_lim, 0.0) # FIXME: remove the - from u once the sim is updated. This is due to the old NED convention
        self._view.set_rpm(u_rpm)

        self._controller.set_distance_to_target(distance)

        if mission_state == "GOAL ACCEPTED"\
                and distance > self._controller.get_goal_tolerance():
            self._controller.set_mission_state("RUNNING")
            self._loginfo("WPF: mission state check")

        info_str = f"heading: {heading:.3f} distance: {distance:.3f} Thrust Vector: {-u_tv_hor_lim:.3f} RPM: {u_rpm:.3f}"
        self._loginfo(info_str)

        return


    def transform_waypoint(self, waypoint):

        goal_body = tf2_geometry_msgs.do_transform_pose(waypoint.pose, self._tf_base_link)

        return goal_body


    def get_heading(self, x_ref):

        heading = math.atan2(x_ref.position.y, x_ref.position.x)

        return heading


    def get_distance(self, x_ref):

        distance = math.sqrt(x_ref.position.x**2 + x_ref.position.y**2)

        return distance


    def limit_control_action(self, u, u_min, u_max):
        """
        Take the hardware constraints into account.
        """
        u_lim = None

        if u > u_max:
            u_lim = u_max
        elif u < u_min:
            u_lim = u_min
        else:
            u_lim = u

        return u_lim


# TODO: Write unit tests here that do one loop of everything

