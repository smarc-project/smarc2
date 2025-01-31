LoLo Robot Description
======================
This robot description package for LoLo includes the latests (Nov 2021) measurements
and CAD model of LoLo. 

Launch Files
============
The package includes two different URDF models, one for general use on LoLo's
scientis and for visualization (RViz), and one for simulations with Gazebo 
(e.g. UUV Simulator).

LoLo's scientis should always run the 'lolo_description.launch' to set up the TF frames for
all the sensors.

upload_lolo_uuv.launch is included for reference and has not been modified to work with ROS2 or the thew simulator (Jan 2025)

Lolo control input
==================

Publish on these topics to set the fin angle or thrust.

* `/lolo/fins/0/input` - starboard rudder (both rudders are coupled on LoLo so must be equal)
* `/lolo/fins/1/input` - port rudder (both rudders are coupled on LoLo so must be equal)
* `/lolo/fins/2/input` - starboard elevon
* `/lolo/fins/3/input` - port elevon
* `/lolo/fins/4/input` - elevator
* `/lolo/thrusters/0/input` - startboard thruster
* `/lolo/thrusters/1/input` - port thruster

Lolo output values
==================

These topics give you the actual values achieved.

* `/lolo/fins/0/output` - starboard rudder (both rudders are coupled on LoLo so must be equal)
* `/lolo/fins/1/output` - port rudder (both rudders are coupled on LoLo so must be equal)
* `/lolo/fins/2/output` - starboard elevon
* `/lolo/fins/3/output` - port elevon
* `/lolo/fins/4/output` - elevator
* `/lolo/thrusters/0/output` - startboard thruster
* `/lolo/thrusters/1/output` - port thruster
