# active_hook

	Will update readme very soon.

	ps5 commands -> twist msgs ->ActiveHook/mavros/manual_control/send


## Control scheme
	
	left stick y -> linear.x
	left stick x -> angular.z (yaw)
	right stick x -> angular.x (roll)
	right stick y -> angular.y (pitch)
	r2-l2 -> linear.z

	due to private reasons we don't have linear.y
	

## Build & run

    	colcon build --packages-select active_hook
    	source install/setup.bash
    	ros2 launch active_hook active_hook_captain.launch.py


