#!/usr/bin/python3

# Dirty dirty workaround to how ROS2 installs things
# while also allowing running this file from the command line
# without ROS-stuff.
try:
    from .sam_view import SAMView # for ROS2
    from .geometry.vector2 import vec2_directed_angle
except:
    from sam_view import SAMView # for terminal running
    from geometry.vector2 import vec2_directed_angle

import numpy as np

class PIDControl:
    """
    From:  https://github.com/DoernerD/Python_Control/blob/main/src/PID_control.py
    To simplify the PIDModel by using this.
    """
    def __init__(self, Kp=1.0, Ki=0.1, Kd=2.0):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self.reset()

    def get_control(self, x, x_ref, dt:float):
        """
        Returns the control input to the system given its current state x, its desired state x_ref
        and the time since last update dt in seconds.
        x and x_ref should be arithmetic-able objects like ndarrays or single floats
        """
        self._error_prev = self._error
        self._error = x_ref - x
        self._integral = self._integral + self._error*dt
        self._derivative = (self._error - self._error_prev)/dt

        u = self._Kp*self._error + self._Ki*self._integral + self._Kd*self._derivative

        return u, self._error

    def reset(self):
        self._error = 0.0
        self._integral = 0.0
        self._derivative = 0.0
        self._error_prev = 0.0


class PIDModel:
    """
    A simple PID heading and thrust controller intended for SAM
    to demonstrate a clean example
    """
    def __init__(self,
                 init_posi=[0.0,0.0],
                 init_yaw=0,
                 max_rpm=1000.0,
                 max_thrust_angle=0.15):
        self._posi = np.array(init_posi)
        self._yaw = float(init_yaw)
        self._max_rpm = float(max_rpm)
        self._max_thrust_angle = float(max_thrust_angle)

        self._wp = None

        self._yaw_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0)
        self._thrust_pid = PIDControl(Kp=1.0, Ki=0.1, Kd=2.0)


    def set_pose(self, posi, yaw:float):
        """
        Set the estimated pose of the vehicle.
        posi=[x,y] in meters.
        yaw in radians, CCW from the x axis
        """
        self._posi = np.array(posi)
        self._yaw = float(yaw)


    def set_waypoint(self, wp):
        """
        Set the goal waypoint to reach in absolute coordinates, in the same
        frame of reference as the vehicle pose.
        """
        self._wp = np.array(wp)
        # Also reset the pid controllers since they shouldn't retain
        # any errors from a past WP
        self._yaw_pid.reset()
        self._thrust_pid.reset()


    def _signed_normalize_u(self, val, max):
        return np.sign(val) * min([np.abs(val), max])


    def compute_control_action(self, dt:float):
        """
        Returns the desired horizontal thruster angle in radians and thrust in RPMs 
        according to simple PID heading and thrust control towards the set waypoint.

        This is not a good controller! Do not use this on the real things, ever!
        The point is not this controller, it is how its structured as a code object.
        Someone that actually knows how to control things should write something 
        that works instead of this ;)
        """
        if(self._wp is None): return 0,0

        # The vector towards the WP from Position
        position_error = self._wp - self._posi
        
        # Make a normalized vector out of the yaw angle
        yaw_vector = np.array([np.cos(self._yaw), np.sin(self._yaw)])
        
        # Difference between the error vector and our current yaw vector
        # This is a signed angle in radians between -pi, pi
        yaw_error = vec2_directed_angle(yaw_vector, position_error)
        # Similarly, distance to point for thrusting 
        distance_error = np.linalg.norm(position_error)

        # Since angles are weird to work with, we have computed
        # our own error, and give that as the "current state" to the PID
        # with the "target state" at 0, since if error=0 we good.
        # This way, the PID object need not have separate handling of angles!
        yaw_u,_ = self._yaw_pid.get_control(yaw_error, 0, dt)
        # PID gives a unitless control input, we need radians
        # normalize to -pi,pi
        # also swap it around because of the trick we pulled above, we want the control
        # inputs to be positive when it is "forward"
        yaw_u *= -1
        yaw_rads = self._signed_normalize_u(yaw_u, self._max_thrust_angle)
        
        # Similary, since we separated the yaw and thrust controls,
        # we should just tell the PID to 0-out the distance error.
        thrust_u,_ = self._thrust_pid.get_control(distance_error, 0, dt)
        thrust_u *= -1
        # also normalize the thrust to some useful RPMs
        thrust_rpms = self._signed_normalize_u(thrust_u, self._max_rpm)

        return yaw_rads, thrust_rpms






if __name__ == "__main__":
    # these are not required by the class above, just for testing
    # see sam_view.py for comments on how main works in ros2 now
    import rclpy, sys

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SAMViewTestNode")

    view = SAMView(node)

    model = PIDModel()

    # just a simple waypoint dead-ahead
    # model.set_waypoint([0,10])

    loop_rate = 10
    rate = node.create_rate(loop_rate)

    # This will spam more-or-less the same stuff because the vehicle never moves according to control
    # there is no simulation happening here!
    while(rclpy.ok()):
        yaw_u, thrust_u = model.compute_control_action(1/loop_rate)
        node.get_logger().info(f"yaw_u = {yaw_u},   thrust_u = {thrust_u}")
        view.set_control_inputs(thruster_horizontal_radians= yaw_u,
                                rpm = thrust_u)
        view.update()

        rclpy.spin_once(node)
        rate.sleep() 
