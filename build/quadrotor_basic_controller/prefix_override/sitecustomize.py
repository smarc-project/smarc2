import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jonat/ros2_ws/src/smarc2/install/quadrotor_basic_controller'
