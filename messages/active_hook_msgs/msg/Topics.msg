# Used by active_hook_captain.
# Launched under the 'ActiveHook' namespace -- all names defined here
# must be relative, they must NOT start with '/'.

# joystick chain
string JOY_TOPIC='joy'                                            # sensor_msgs/msg/Joy - raw PS5 controller input

# motion command
string AUTONOMY_CMD_VEL_TOPIC='cmd_vel'                           # geometry_msgs/msg/Twist - velocity commands for autonomous tasks

# mavros / ArduSub bridge
string MAVROS_MANUAL_CONTROL_TOPIC='mavros/manual_control/send'   # mavros_msgs/msg/ManualControl
string MAVROS_STATE_TOPIC='mavros/state'                          # mavros_msgs/msg/State
string MAVROS_ARMING_SRV='mavros/cmd/arming'                      # mavros_msgs/srv/CommandBool
string MAVROS_SET_MODE_SRV='mavros/set_mode'                      # mavros_msgs/srv/SetMode
string MAVROS_IMU_TOPIC='mavros/imu/data'                         # sensor_msgs/msg/Imu

# imu_to_odom output
string ATTITUDE_TOPIC='attitude'                                  # geometry_msgs/msg/Vector3 - roll/pitch/yaw in degrees
string ODOM_TOPIC='odom'                                          # nav_msgs/msg/Odometry - attitude-only odometry (no position source)
