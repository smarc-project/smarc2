# SAM Diving Controller

All the things you need to make SAM dive and follow waypoints.

Listens to the BT for waypoints and follows them. It chooses between active,
i.e. using the thrusters, and static diving, i.e. using LCG amd VBS based on
the distance to the waypoint.

## Launch Files

We have two launch files:

### actionserver.launch

Called by the sam\_bringup.sh script. This listens to the BT for waypoints

### setpoint\_topic.launch

If you want to test things without the BT, call this and provide your own
setpoints.

Both launch files call Node.py, which takes care of the rest.


## sam\_diving\_controller

### ActionClientNode.py

If you want to test something and provide your own waypoint, that's the way to go.

### ActionServerDiveSub.py

Inherits from DiveSub and the SMARCActionServer, but allows you to interface
with the BT action server instead. The action implemented is a
`auv-depth-move-to` action which requires a positive desired depth, rpm, and
the waypoint from the GUI.

### ConveniencePub.py

Defines control convenience topics and publishes to them. That is:
    - current state
    - current control reference
    - current control error
    - current control input
    - current waypoint
All are published under /conv/ to make it easier to read them out afterwards.

### DiveSub.py

Reads out all robot states and provides the `get/set` methods for the
controller.

### DiveController.py

This files contains all controller classes available. The I/O interface can
change between them, depending on their respective needs. All classes inherit
from `DiveControllerInterace` which provides all common functions. The control
happens in the update function of the respective controller. Right now we have
the following controller classes:

#### DiveControllerPID

Basic PID controller for waypoint following. Distinguishes between static and
dynamic diving and uses either VBS/LCG for static diving or thrust-vectoring
for dynamic diving. All parameters are specified in
sam\_diving\_controller\_config.yaml. Each PID gain, min, max, and neutral
actuator values as well as emergency actuator values.

#### DepthJoyControllerPID

This is a smaller version of the `DiveControllerPID` which we use for keeping
depth when using the joystick for teleop. It keeps the desired depth and pitch,
but allows the operator to maneuver the AUV.

#### DiveControllerMPC

This implements a MPC for waypoint following.

### IDivePub.py

Interface for the DivePub. Defines the mission states enum.

### Node.py

Runs the different MVC nodes plus a convenience node for extra rostopics. This
node loads all required parameters.

Requires the following parameter:
    - pub\_rate: rate of the publisher node
    - controller\_rate: rate of the controller node
    - sub\_rate: rate of the subscriber node
    - convenience\_rate: rate of the convenience node

These are set in sam\_diving\_controller\_config.yaml.

### ParamUtils.py

Reads out all parameters for the DivingModel.py

### SAMDivePub.py

Publishes all actuator commands. Contains the corresponding set methods.
Requires the following SamTopics:
    - VBS\_CMD\_TOPIC
    - LCG\_CMG\_TOPIC
    - THRUSTER1\_CMD\_TOPIC
    - THRUSTER2\_CMD\_TOPIC
    - THRUST\_VECTOR\_CMD\_TOPIC

### SetpointNode.py

If you need to publihs a setpoint.

## config

Contains the config file for this package

## rviz

Sample rviz layout to follow the vehicle and visualize the waypoints.

## plotjuggler

Sample plotjuggler layout to analyse rosbags.


