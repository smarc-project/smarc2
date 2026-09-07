# Used by active_hook_captain.
# Launched under the 'ActiveHook' namespace -- all names defined here
# must be relative, they must NOT start with '/'.

# joystick chain
string JOY_TOPIC='joy'                                            # sensor_msgs/msg/Joy - raw PS5 controller input
string JOY_ROV_TOPIC='joy_rov'                                    # sensor_msgs/msg/Joy - with L2/R2 vertical axis added, feeds into teleop_twist_joy

# motion command
string AUTONOMY_CMD_VEL_TOPIC='rov/autonomy/cmd_vel'              # geometry_msgs/msg/Twist - velocity command from teleop

# mavros / ArduSub bridge
string MAVROS_MANUAL_CONTROL_TOPIC='mavros/manual_control/send'   # mavros_msgs/msg/ManualControl
string MAVROS_STATE_TOPIC='mavros/state'                          # mavros_msgs/msg/State
string MAVROS_ARMING_SRV='mavros/cmd/arming'                      # mavros_msgs/srv/CommandBool
string MAVROS_SET_MODE_SRV='mavros/set_mode'                      # mavros_msgs/srv/SetMode
