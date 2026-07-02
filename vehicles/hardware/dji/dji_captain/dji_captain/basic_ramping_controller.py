import numpy as np


class BasicRampingController:
    """
    Velocity controller parameters
    Tuning: For large movements, k_pose will have essentially no impact on the startup. 
    r_sigma dominates in this range, with a larger r_sigma producing a smoother 
    start and a smaller r_sigma producing a faster start. 
    When stopping, both variables matter. A larger r_sigma will produce more overshoot in the target position.
    A smaller k_pose will cause this to behave more like a normal proportional controller, reducing overshoot by 
    making the deceleration happen over a greater distance. 
    A larger k_pose will decrease the time spent decelerating, which could either increase or decrease overshoot, 
    depending on how large it is. The best choice for these values is also dependent on max_speed and even more 
    so on JOY_PUB_PERIOD(in dji captain), so make sure to be very careful and retune after adjusting these.
    these are tested and liked for the real M350 as of writing this (Oct 1st, 2025)
    #proportional gain
    k_pose = .5 
    "gain" on previous output, between 0 and 1 
    (kind of, the "desired output" is multiplied by 1 - r_sigma and the previous output is multiplied by r_sigma).
    r_sigma = .9 
    So far, these also worked fine for the FC30 as well (Jul 1st, 2026)
    """
    def __init__(self,
                 max_speed: float = 10.0,
                 k_pose: float = 0.5,
                 r_sigma: float = 0.9,
                 position_error_epsilon: float = 0.1,
                 position_error_max: float = 100.0,
                 log_func=print):
        
        self.MAX_SPEED = max_speed
        self.K_POSE = k_pose
        self.R_SIGMA = r_sigma
        self.POS_ERR_EPS = position_error_epsilon
        self.POS_ERR_MAX = position_error_max
        self.log = log_func
        self._prev_vel_out : np.ndarray|None = None

    def cancel(self) -> None:
        self._prev_vel_out = None
        self.log("Controller cancelled, previous velocity output cleared.")

    def cmd_pos_err(self, e_forw: float, e_left: float, e_up: float) -> None|np.ndarray:
        if (abs(e_forw) < self.POS_ERR_EPS and\
            abs(e_left) < self.POS_ERR_EPS and\
            abs(e_up) < self.POS_ERR_EPS):
            self.log("Reached setpoint within epsilon on all axes.")
            self._prev_vel_out = None
            return None

        if np.linalg.norm([e_forw, e_left]) > self.POS_ERR_MAX:
            self.log(f"Setpoint is more than {self.POS_ERR_MAX}m away horizontally.")
            self._prev_vel_out = None
            return None
        
        if abs(e_up) > self.POS_ERR_MAX:
            self.log(f"Setpoint is more than {self.POS_ERR_MAX}m away vertically.")
            self._prev_vel_out = None
            return None

        speed_forward = self.K_POSE * e_forw
        speed_left = self.K_POSE * e_left
        speed_up = self.K_POSE * e_up

        return self.cmd_vel(speed_forward, speed_left, speed_up)

    def cmd_vel(self, speed_forward: float, speed_left: float, speed_up: float) -> np.ndarray:

        if (self._prev_vel_out is None):
            max_speed = 0.1
            self._prev_vel_out = np.array([0.0, 0.0, 0.0])
            self.log(f"No previous velocity output, using low initial max speed of {max_speed} m/s for smooth start.")
        else:
            max_speed = self.MAX_SPEED

        def limit_speed(vel_net: np.ndarray, max_speed: float) -> np.ndarray:
            vel_norm = np.linalg.norm(vel_net)
            if vel_norm > max_speed:
                vel_net = vel_net / vel_norm * max_speed
            return vel_net

        vel_err = np.array([speed_forward, speed_left, speed_up])
        vel_err = limit_speed(vel_err, max_speed)

        vel_net = (1 - self.R_SIGMA) * vel_err + self.R_SIGMA * self._prev_vel_out
        vel_net = limit_speed(vel_net, max_speed)
        
        self._prev_vel_out = vel_net
        return vel_net