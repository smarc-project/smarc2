# This file defines all the topics used on FloatSam USV

# FloatSam Abort
string FLOATSAM_ABORT = 'abort'

# PID controllers setpoints. All Float32s.
string YAW_SETPOINT = 'ctrl/yaw_setpoint'
string VELOCITY_SETPOINT = 'ctrl/velocity_setpoint'

# Real-time speed override (m/s) published by behaviours.py.
# When this is being published it overrides the speed in the action goal.
# The move_to_path action server subscribes to this topic.
string SPEED_OVERRIDE = 'ctrl/speed_override'

# Thruster commands. All Float32s (RPM).
string THRUSTER_PORT_CMD = 'actuators/thruster_port_cmd'
string THRUSTER_STRB_CMD = 'actuators/thruster_strb_cmd'

# Thruster feedback. All Float32s (RPM).
string THRUSTER_PORT_FB = 'actuators/thruster_port_fb'
string THRUSTER_STRB_FB = 'actuators/thruster_strb_fb'

#Loiter with Heading feedback
string LOITER_HEADING_FB = 'loiter_heading_fb'
