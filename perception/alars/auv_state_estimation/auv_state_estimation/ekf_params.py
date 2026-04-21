from dji_msgs.msg import Links, Topics

PARAMS = [
    ("topics.input_polygon", Topics.ESTIMATED_AUV_OBB_TOPIC),
    ("topics.input_auv_head", Topics.ESTIMATED_AUV_HEAD_TOPIC),
    ("topics.output_topic", "rviz/estimated_pose"),
    ("topics.linear_velocity", "/M350/wrapper/psdk_ros2/velocity_ground_fused"),
    ("topics.angular_velocity", "/M350/wrapper/psdk_ros2/angular_rate_ground_fused"),
    ("topics.ekf_status", "/alars_auv_ekf/status"),

    ("frames.map", Links.MAP),
    ("frames.output_link", Links.ESTIMATED_AUV),
    ("frames.camera", Links.GIMBAL_OPTICAL_FRAME),

    ("camera_info", ""),

    ("z_water", 0.0),
    ("n_air", 1.0),
    ("n_water", 1.0),

    # note that these are dimensions of the AUV in the measurement model (OBB), not necessarily the true dimensions of the AUV.
    ("obb.length_m", 1.3), # auv length in meters, may need to be adjusted
    ("obb.width_m", 0.16), # auv width in meters, may need to be adjusted

    ("alpha_line_pixels", 40.0), # pixels along the alpha direction to compute the front and back rays for yaw estimation in initialization

    ("sigma_a", 0.01), # m/s^2, could split up into x, y
    ("sigma_z_process", 1.0), # m/s^2, only z as waves mostly affect depth
    ("sigma_yaw_process", 3.0), # deg/s
    ("sigma_pitch_acc_deg", 15.0), # deg/s^2, only for pitch as waves mostly affect pitch

    # measurement noise stddev (pixels)
    ("R_u", 10.0), 
    ("R_v", 10.0),
    ("R_alpha_deg", 5.0),
    ("R_len", 200.0),
    ("R_wid", 40.0),

    # dynamic measurement noise stddev (pixels)
    # increases with distance from image center
    ("R_dyn.center_gain_u", 50.0), 
    ("R_dyn.center_gain_v", 50.0),
    ("R_dyn.center_gain_alpha_deg", 10.0),
    ("R_dyn.center_gain_len", 10.0),
    ("R_dyn.center_gain_wid", 10.0),

    # increases with drone speed
    ("R_dyn.speed_gain_u", 50.0),
    ("R_dyn.speed_gain_v", 50.0),
    ("R_dyn.speed_gain_alpha_deg", 10.0),
    ("R_dyn.speed_gain_len", 60.0),
    ("R_dyn.speed_gain_wid", 30.0),

    # drone pose noise
    ("R_pose_x", 0.03),
    ("R_pose_y", 0.03),
    ("R_pose_z", 0.03),
    ("R_pose_r", 1.0),
    ("R_pose_p", 1.0),
    ("R_pose_yaw", 3.0),

    # dynamic measurement noise update rate (s)
    ("R_dyn_dt", 0.5),

    ("init_z_needed", 5),
    ("init_pos_max_spread", 2.0),
    ("init_yaw_max_spread", 0.7),
    ("init_z_max_spread", 2.0),
    ("init_min_depth", 0.2),
    ("init_max_depth", 8.0),
    ("init_depth_steps", 40),

    ("gating.prob", 0.99),

    ("logger_info.enable", True),

    # jacobian epsilons for numerical differentiation
    ("jacobian.eps_state_pos", 1e-3),
    ("jacobian.eps_state_yaw", 1e-3),
    ("jacobian.eps_state_vel", 1e-3),
    ("jacobian.eps_pose_pos", 1e-3),
    ("jacobian.eps_pose_ang", 1e-3),

    # "surface", "depth", "pitch", "depth9d"
    ("motion_model", "depth9d"),
]