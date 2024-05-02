# Dead reckoning

All dead reckoning topics and nodes reside within the ``/vehicle/dr`` namespace.
Note that the odometry topic may be used to construct the TF transformations.
In general, the TF tree will be used to construct the convenience topics:
latitude, longitude, depth, yaw, pitch and roll.

# Topics

- Dead reckoning odometry (poses, velocities and uncertainties) - ``nav_msgs/Odometry`` on topic ``/vehicle/dr/odom``
- Latitude longitude position - ``geographic_msgs/GeoPoint`` on ``/vehicle/dr/lat_lon``
- Estimated depth - ``std_msgs/Float64`` on ``/vehicle/dr/depth``
- Estimated yaw (ENU) - ``std_msgs/Float64`` on ``/vehicle/dr/yaw``
- Estimated pitch - ``std_msgs/Float64`` on ``/vehicle/dr/pitch``
- Estimated roll - ``std_msgs/Float64`` on ``/vehicle/dr/roll``
- Estimated compass heading (NED in degrees) - ``std_msgs/Float64`` on ``/vehicle/dr/compass_heading``