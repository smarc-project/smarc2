# Utilities
Simple services that we can use to consolidate globally useful functions with.

## Dubins Planner
A simple dubins path planner made into a service node.

## SSS Viewer
A basic sidescan sonar viewing package to look at waterfalls.

## str_json_mqtt_bridge
ROS<->MQTT JSON Formatted string bridge. Mostly useful for waraps-related stuff.
Main usefulness is that this avoids the `{"data":...}` thing that happens with the `mqtt_bridge` when bridging `std_msgs::String`s.

## utm_latlon_converter
Package that provides python objects and ros services for conversions. Usually easiest to import straight and use without getting ROS involved.

## smarc_action_client
Library that enforces ROS2 action-client interfaces be implemented using Python Abstract Base Class.
The library intends to abstract and simplify the registering of callbacks and hide some of the async complexity from the user. 

