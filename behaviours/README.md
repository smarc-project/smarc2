# Behaviours
This folder contains the high-level behaviours that our robots can perform, as well as the behaviour tree implementation that coordinate them.

## List of behaviours

### GoToWaypoint
Move to a given lat,lon.

### EmergencySurface
Do whatever is needed to reach the surface.

## Behaviour tree
The BT that runs the show. 

TODO: Picture of BT etc.

## GoToGeopoint
Implementation of action server/client using ROS2 `smarc_action_base` client library. It is a good example to develop different implementation bases on `smarc_action_base`. More information can be found in the README for the package.

## smarc_action_base
A wrapper around ROS2 Action server/client that hides away a lot of the asynchronous programming complexity from the end user. It enforces the implementation of callbacks through Python's Abstract Base Class decorators. This forces the user to implement all that is necessary from the outset for a action server/client.
