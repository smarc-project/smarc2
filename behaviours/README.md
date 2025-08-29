# Behaviours
This folder contains the high-level behaviours that our robots can perform, as well as the behaviour tree implementation that coordinate them.

## wasp_bt
The BT that is used across SMaRC to command and interface with the vehicles. Acts as the top-level safety and mission execution layer.

## smarc_action_base
A wrapper around ROS2 Action server/client that hides away a lot of the asynchronous programming complexity from the end user. It enforces the implementation of callbacks through Python's Abstract Base Class decorators. This forces the user to implement all that is necessary from the outset for a action server/client.

**If you are writing an action server for the `wasp_bt`, check out `../examples/SuperSimpleActionServer.py` example that implements `gentler_action_server.py`.**

## GoToGeopoint
A baseline implementation of action server/client using ROS2 `smarc_action_base` client library. It is a good example to develop different implementation based on `smarc_action_base`. 
This is useful if the action client is not the wasp_bt.

## Vehicle-specific stuff
Should explain what they do in their own readmes.