# Dubins planner

This package provides a service under `smarc_mission_msgs.msg::Topics.DUBINS_SERVICE`.

Run with `ros2 run dubins_planner dubins_planner_service`.

You can see a sample plotted with `ros2 run dubins_planner dubins_planner_service_tester`.

It takes as input three things:
- A list of Pose2D for waypoints. X,Y in meters and Theta in angles, CCW from +x to +y.
- Step: A float for the distance between interpolated points
- Turning radius: The turning radius, in meters.

Returns:
- A list of Pose2D that includes the original waypoints in addition to the interpolated ones.
- A list of int indices that indicate WHICH of the waypoints in the output were in the original list of waypoints given as input.