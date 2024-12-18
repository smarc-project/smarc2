#!/usr/bin/python3
import numpy as np
import onnxruntime as ort


class ONNXManager():
    """
    Simple ONNX inference session: https://onnxruntime.ai/docs/get-started/with-python.html
    Max values based on training configuration.
    If you are not sure what values were used for training, do not touch this.
    """

    def __init__(self,
                 model_resource: str,
                 rpm_max: float = 1000,
                 vbs_max: float = 100,
                 aileron_angle_max: float = 0.2,
                 rudder_angle_max: float = 0.2,
                 lcg_max: float = 100,
                 ):
        self.onnx_inferenceSession = ort.InferenceSession(model_resource)  # TODO: If non-determinisim cant be solved, might need to load it as a torch model

        self.rpm_max = rpm_max
        self.rudder_angle_max = rudder_angle_max
        self.aileron_angle_max = aileron_angle_max
        self.vbs_max = vbs_max
        self.lcg_max = lcg_max

    def get_control_scaled(self, x):
        return self.rescale_outputs(self.get_control(x))

    def get_control(self, x, prep_state_func = lambda x: x):
        """
        Inputs (1,14):
            x[0-3] = Orientation quaternion
            x[4-6] = Linear velocity
            x[7-9] = Angular velocity
            x[10-12] = Relative vector to waypoint
            x[13] = Desired speed (magnitude of linear velocity vector)

        Outputs:
            y[0] = rpm1 // rpm2
            y[1] = VBS
            y[2] = Aileron
            y[3] = Rudder
            y[4] = LCG
        """
        x = prep_state_func(x)
        controls = self.onnx_inferenceSession.run(["continuous_actions"], {'obs_0': x})
        return np.array(controls[0], dtype=np.float32).flatten()

    def prepare_state(self, state):
        odometry = state[0]
        heading = state[1]

        x = np.zeros((1,14), dtype=np.float32)

        x[0, 0] = odometry.pose.pose.orientation.x
        x[0, 1] = odometry.pose.pose.orientation.y
        x[0, 2] = odometry.pose.pose.orientation.z
        x[0, 3] = odometry.pose.pose.orientation.w

        x[0, 4] = odometry.twist.twist.linear.x
        x[0, 5] = odometry.twist.twist.linear.y
        x[0, 6] = odometry.twist.twist.linear.z

        x[0, 7] = odometry.twist.twist.angular.x / 0.5
        x[0, 8] = odometry.twist.twist.angular.y / 0.5
        x[0, 9] = odometry.twist.twist.angular.z / 0.5

        x[0, 10] = heading.position.x
        x[0, 11] = heading.position.y
        x[0, 12] = heading.position.z

        x[0, 13] = state[2]
        return x

    def rescale_outputs(self, y):
        """
        Rescale outputs to values actually used by SAM during training.
        """
        y = np.array(y, dtype=np.float32)

        y = np.clip(y, -1, 1)
        y[0] = y[0] * self.rpm_max
        y[1] = ((y[1] + 1) * 0.5) * self.vbs_max
        y[2] = y[2] * self.aileron_angle_max
        y[3] = y[3] * self.rudder_angle_max
        y[4] = ((y[4] + 1) * 0.5) * self.vbs_max
        return y
