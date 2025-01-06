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

### Node.py

Runs the different MVC nodes plus a convenience node for extra rostopics. 

Requires the following parameter:
    - view\_rate: rate of the view node
    - model\_rate: rate of the model node
    - controller\_rate: rate of the controller node
    - convenience\_rate: rate of the convenience node

### SAMDiveView.py

Publishes all actuator commands. Contains the corresponding set methods.

### DiveController.py

Reads out all robot states. This is a MVC Controller, not a control theory controller!

### DivingModel.py

This is the actual control, currently running several PIDs.

### ActionServerDiveController.py

Inherits from DiveController.py, but allows you to interface with the BT action server instead.
