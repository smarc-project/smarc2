# SMaRC2 4 ROS2 Workshop
This package is the final product of the workshop we held on 18 March 2024.

You can find the slides [here](/documentation/ROS2%20Workshop.md).

## What does it do?
`ros2 launch workshopfun do_science.launch` will run a simple Model View Controller example node that makes SAM thrust back and forth randomly. 
It has services and parameters that you can play with. 
You can also see how a yaml config can be used.

`ros2 launch workshopfun actionserver.launch` will run a simple action server and a client. The client will send a goal, and then _maybe_ cancel that goal. 
Ths action server here uses the same View object from `do_science`.
