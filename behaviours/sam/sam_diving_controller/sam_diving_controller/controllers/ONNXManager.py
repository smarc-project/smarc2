#!/usr/bin/python3
import os

import numpy as np
import onnxruntime as ort
from ament_index_python import get_package_share_directory


class ONNXManager():
    """
    Simple ONNX inference session: https://onnxruntime.ai/docs/get-started/with-python.html
    Max values based on training configuration.
    If you are not sure what values were used for training, do not touch this.
    """

    def __init__(self,
                 model_resource: str = "DR_temp",
                 rpm_max: float = 1000,
                 aileron_angle_max: float = 0.2,
                 rudder_angle_max: float = 0.2,
                 vbs_max: float = 100,
                 lcg_max: float = 100,
                 ):
        # options = ort.SessionOptions()
        # options.use_deterministic_compute = True

        pkg_share = get_package_share_directory("sam_diving_controller")
        onnx_path = os.path.join(pkg_share, "resource", f"{model_resource}.onnx")

        self.onnx_inferenceSession = ort.InferenceSession(onnx_path,
                                                          # sess_options=options
                                                          )  # TODO: If non-determinisim cant be solved, might need to load it as a torch model

        self.rpm_max = rpm_max
        self.rudder_angle_max = rudder_angle_max
        self.aileron_angle_max = aileron_angle_max
        self.vbs_max = vbs_max
        self.lcg_max = lcg_max

    def get_control_scaled(self, x):
        return self.rescale_outputs(self.get_control(x))

    def get_control(self, x, prep_state_func=lambda x: x):
        """
        Inputs (1,27):
            x[0-3] = Orientation. Mocap frame. NED, Quaternion
            x[4-6] = Linear velocity. Body Frame, FLU, Vector3
            x[7-9] = Angular velocity. Body Frame, FLU, Vector3
            x[10-12] = Relative vector to waypoint. Body Frame, NED, Vector3
            x[13-16] = Relative orientation of waypoint w.r.p body. Body Frame, NED, Quaternion
            x[17-19] = Absolute position. Mocap frame, NED, Vector3
            x[20-24] = Previous/current "action" vector.
            x[25] = LCG feedback. Normalized to [0, 1] (Divide percentage by 100)
            x[26] = VBS feedback. Normalized to [0, 1] (Divide percentage by 100)

        Outputs:
            y[0] = rpm1 // rpm2
            y[1] = Aileron
            y[2] = Rudder
            y[3] = VBS
            y[4] = LCG
        """
        x = prep_state_func(x)
        controls = self.onnx_inferenceSession.run(["continuous_actions"], {'obs_0': x})
        return np.array(controls[0], dtype=np.float32).flatten()

    def prepare_state(self, state):
        odom_mocap_ned = state[0]
        odom_body_ned = state[1]
        waypoint = state[2]
        control = state[3]

        x = np.zeros((1, 27), dtype=np.float32)

        # x[0-3] = Orientation. Mocap frame. NED, Quaternion
        x[0, 0] = odom_mocap_ned.pose.pose.orientation.x
        x[0, 1] = odom_mocap_ned.pose.pose.orientation.y
        x[0, 2] = odom_mocap_ned.pose.pose.orientation.z
        x[0, 3] = odom_mocap_ned.pose.pose.orientation.w

        # x[4-6] = Linear velocity. Body Frame, FLU, Vector3
        x[0, 4] = 0
        x[0, 5] = 0
        x[0, 6] = 0

        # x[7-9] = Angular velocity. Body Frame, FLU, Vector3
        x[0, 7] = 0
        x[0, 8] = 0
        x[0, 9] = 0

        # x[10-12] = Relative vector to waypoint. Body Frame, NED, Vector3
        x[0, 10] = 0
        x[0, 11] = 0
        x[0, 12] = 0

        # x[13-16] = Relative orientation of waypoint w.r.p body. Body Frame, NED, Quaternion
        x[0, 13] = 0
        x[0, 14] = 0
        x[0, 15] = 0
        x[0, 16] = 0

        # x[17-19] = Absolute position. Mocap frame, NED, Vector3
        x[0, 17] = odom_mocap_ned.pose.pose.position.x
        x[0, 18] = odom_mocap_ned.pose.pose.position.y
        x[0, 19] = odom_mocap_ned.pose.pose.position.z

        # x[20-24] = Previous/current "action" vector.
        x[0, 20] = control['rpm1'] / 1000
        x[0, 21] = control['stern'] / 0.2
        x[0, 22] = control['rudder'] / 0.2
        x[0, 23] = ((control['vbs'] / 100) + 1) / 2
        x[0, 24] = ((control['lcg'] / 100) + 1) / 2

        # x[25] = LCG feedback. Normalized to [0, 1] (Divide percentage by 100)
        # x[26] = VBS feedback. Normalized to [0, 1] (Divide percentage by 100)
        x[0, 25] = control['lcg'] / 100  # Normalized differently, unfortunately
        x[0, 26] = control['vbs'] / 100

        return np.clip(x, -1, 1)

    def rescale_outputs(self, y):
        """
        Rescale NN outputs to values actually used by SAM.
        Note, this depends on how the NN was configured during training.
        Must be cross-referenced to the training configuration in Unity.
        """
        y = np.array(y, dtype=np.float32)

        y = np.clip(y, -1, 1)
        y[0] = y[0] * self.rpm_max
        y[1] = y[1] * self.aileron_angle_max
        y[2] = y[2] * self.rudder_angle_max
        y[3] = ((y[3] + 1) * 0.5) * self.vbs_max
        y[4] = ((y[4] + 1) * 0.5) * self.lcg_max
        return y
