import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/schni2zle/colcon_ws/src/install/basic_go_to_waypoint'
