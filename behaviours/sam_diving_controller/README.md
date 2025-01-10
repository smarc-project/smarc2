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

### ActionServerDiveController.py

Inherits from DiveController.py, but allows you to interface with the BT action
server instead.

### ConvenienceView.py

Defines control convenience topics and publishes to them. That is:
    - current state
    - current control reference
    - current control error
    - current control input
    - current waypoint
All are published under /conv/ to make it easier to read them out afterwards.

### DiveController.py

Reads out all robot states. This is a MVC Controller, not a control theory
controller!

### DivingModel.py

This is the actual control, currently running several PIDs. All parameters are
specified in sam\_diving\_controller\_config.yaml. Each PID gain, min, max, and
neutral actuator values as well as emergency actuator values.

### IDiveView.py

Interface for the DiveView. Defines the mission states enum.

### Node.py

Runs the different MVC nodes plus a convenience node for extra rostopics. 

Requires the following parameter:
    - view\_rate: rate of the view node
    - model\_rate: rate of the model node
    - controller\_rate: rate of the controller node
    - convenience\_rate: rate of the convenience node

These are set in sam\_diving\_controller\_config.yaml.

### ParamUtils.py

Reads out all parameters for the DivingModel.py

### SAMDiveView.py

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


