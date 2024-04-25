=======================
SMARC AUV ROS Interface
=======================
.. image:: https://github.com/smarc-project/smarc_msgs/workflows/CI/badge.svg?branch=noetic-devel
    :target: https://github.com/smarc-project/smarc_msgs/actions
    :alt: GitHub Actions status
.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
    :alt: License

.. contents:: Table of Contents
   :depth: 2

Background
==========

The aim of the SMARC ROS interface is to define a common interface that can be implemented across a range of AUVs. This enables the implementation of a shared set of components on top of these interfaces. It is not the goal of this document to define those components, although that is also part of the SMARC ROS system.

To give some examples, our goal is to share at least the following components:

* Controllers, when actuation is the same
* Planner interface (behavior tree in our case)
* Mission planning interface (Neptus in our case)
* Sensor interfaces, enabling shared inspection tools
* GUI

It should be noted that the interface defined here might only be a subset of the full interface on the vehicle ROS system. Reasons for adding more (non-standard) interfaces might be differentiated actuators, which can not be shared across vehicles, or that some vehicle provides more sensors or other sources of information.

The general philosophy of this document is that we need to test out interfaces on at least one vehicle before proposing to integrate them
in  this standard interface. If a new interface is needed, and has been tested, open a `pull request <https://github.com/smarc-project/smarc_msgs/compare>`_
with the proposed changes!

Preliminaries
=============

This section discusses the division of the interfaces into namespaces and repos.

Namespaces
----------

We will refer to the global vehicle namespace as ``/vehicle``. On the vehicles, this is replaced by the name of the vehicle, and may be e.g. ``/sam`` or ``/lolo``. All topics on the vehicles should be under this namespace. The rationale for this is mainly that we can then run multiple vehicle systems within one simulator session, without topic names colliding.

* ``/vehicle/core`` -  contains the sensors and actuators that are always available on the vehicle, also when no controllers or other higher-level functionality is running. It also includes basic control interfaces such as abort functionality, see `Core interface`_
* ``/vehicle/ctrl`` - contains topics and nodes relating to actuator controllers (e.g. depth, heading, altitude control), see `Controller interfaces`_
* ``/vehicle/dr`` - contains interfaces related to dead reckoning, see `Dead reckoning`_
* ``/vehicle/payload`` - contains sensors and actuators that are not always available on all versions of all vehicles, such as sidescan, multi-beam, cameras etc., see `Payloads`_

The rationale for dividing everything into high-level namespaces is that this makes it easier to debug the system with ROS tools. For example, the rqt_graph presents a visual overview of topics and tools organized by namespaces, and allows collapsing the ones we are not interested in. This allows debugging of the subparts, rather than the whole system.

Repos
-----

This document defines interfaces based on messages in the standard ROS package repositories, and the `smarc_msgs repo <https://github.com/smarc-project/smarc_msgs>`_. Any vehicle-specific messages (outside the scope of this document) should be defined in separate packages. The rationale for this division is that the smarc_msgs repo together with this document (or future versions thereof) might be used as a specification of the shared interface.

Units
-----

The following rules of thumbs holds for all interfaces:

* Always SI units unless otherwise specified
* All distances and positions are in meters (m) unless otherwise specified
* All angles except lat/lon and compass heading are reported in radians (rad).
* Latitude/longitude coordinates are in degrees (deg)
* compass heading is reported in degrees (deg)
* All speeds are in meters per second (m/s)
* All temperatures are in degrees celsius (deg C)
* Conductivity is reported as milli-Siemens per centimeter (mS/cm)
* Percentages are in the range ``[0, 1]``
* Depth is always distance below water surface
* Altitude in the case of control refers to distance above sea floor but may otherwise refer to upwards distance in coordinate system
* All coordinate systems are right-handed (see `TF`_ for more information)

As discussed in the `TF`_ section, we are using ENU coordinate systems. As this includes angles,
the "heading" of the vehicle is reported as yaw (right-handed rotation z-axis pointing upwards).

Parameters
==========

The UTM zone parameters are used in dead reckoning interfaces and the planning (Neptus and behavior tree) interfaces. We define the interactions with our coordinate system in the TF section. Note that UTM zone should never be automatically calculated from GPS position but instead by looking at these parameters. The rationale is that this enables us to cross UTM zones while keeping the coordinate system. The UTM zones are defined in such a way as too allowing use even outside the bounds.

* UTM Zone - ``int`` as ``/utm_zone``, should be set at startup, the UTM longitude zone to use throughout the mission
* UTM band - ``string`` as ``/utm_band``, should be set at startup, the UTM latitude band to use throughout the mission
* Maximum dive depth - ``double`` as ``/vehicle/max_dive_depth``, should be set at startup and be respected by controllers and mission execution (BT)
* Minimum altitude - ``double`` as ``/vehicle/min_altitude``, should be set at startup and be respected by controllers and mission execution (BT)
* Maximum pitch - ``double`` as ``/vehicle/max_pitch``, in either direction, should be set at startup and be respected by controllers and mission execution (BT)
* Maximum roll - ``double`` as ``/vehicle/max_roll``, in either direction,  should be set at startup and be respected by controllers and mission execution (BT)
* Maximum dive time (s) - ``int`` as ``/vehicle/max_roll``, in seconds, should be set at startup and be respected by mission execution (BT)
  
Topic interfaces
================

Core interface
--------------

**Core sensor interfaces**

The base set of sensors are all under the ``/vehicle/core`` namespace. They are all publishers.
All of these messages contain headers with timestamp and they should be filled out as well as possible.
Their `frame_id` should always be filled in with a valid frame in the TF tree that corresponds to the
sensor position on the vehicle. Note that both measurements both in NED and ENU coordinates can be
handled as long is care is taken to define the correct frame in the TF tree, see
the `TF`_ section for more details.

* IMU - ``sensor_msgs/Imu`` on ``/vehicle/core/imu``
* Pressure sensor - ``sensor_msgs/FluidPressure`` on ``/vehicle/core/pressure``
* GPS - ``sensor_msgs/NavSatFix`` on ``/vehicle/core/gps``
* Compass - ``sensor_msgs/MagneticField`` on ``/vehicle/core/compass``
* DVL - ``smarc_msgs/DVL`` on ``/vehicle/core/dvl`` (copied from ``uuv_sensor_ros_plugins_msgs/DVL``)
* DVL status - ``smarc_msgs/SensorStatus`` on ``/vehicle/core/dvl_status``, indicates status of DVL (for more info, see `Payloads`_)
* Leak - ``smarc_msgs/Leak`` on ``/vehicle/core/leak``
* Battery - ``sensor_msgs/BatteryState`` on ``/vehicle/core/battery``

We also define a service to turn on and off the DVL. If this is not possible, it should return false.

* Enable/disable DVL - ``std_srvs/SetBool`` on ``/vehicle/core/toggle_dvl`` - send true to turn on and false to turn off, returns true if successful

We propose including the definition from
`uuv_sensor_ros_plugins_msgs/DVL <https://github.com/uuvsimulator/uuv_simulator/blob/master/uuv_sensor_plugins/uuv_sensor_ros_plugins_msgs/msg/DVL.msg>`_
as a message within ``smarc_msgs`` in order to remove unnecessary dependencies.
Note that this definition is identical to the one in `cola2_msgs <https://bitbucket.org/iquarobotics/cola2_msgs/src/master/msg/DVL.msg>`_.

**Core actuator interface**

These are the first actuator interfaces that will be part of the common interface.
More will be added in the future, see `Near future extensions`_ for possible examples.

Commands (subscribed to by vehicle):

* Thruster RPM - ``smarc_msgs/ThrusterRPM`` on ``/vehicle/core/thruster{N}_cmd``, where N signifies the number of the thruster. Thrusters are numbered either left-to-right or front-to-back, or both, depending on the configuration. **NOTE:** Needs to be published at 10Hz to have effect.

Feedbacks (published by vehicle):

* Thruster feedback - ``smarc_msgs/ThrusterFeedback`` on ``/vehicle/core/thruster{N}_fb``

**Core system interfaces**

* Abort - ``std_msgs/Empty`` on ``/vehicle/core/abort``, aborts current mission, vehicle should surface by itself, with no more control from ROS system

Near future extensions
----------------------

There are also a few preliminary ideas about how to combine the VBS and centre of gravity control.
Basically, you would be able to set the buoyancy of the vehicle with the VBS command, and have the
TCG and LCG commands control physical or virtual masses moving around the vehicle (water being pumped
around the tanks in the case of Lolo). From initial discussions, it seems like both TCG and LCG should
be defined as a value centered around 0, possible positive or negative percentages.

**Publishers**

* VBS - ``smarc_msgs/PercentStamped`` on ``/vehicle/core/vbs_cmd``
* LCG - to be decided
* TCG - to be decided

**Subscribers**

* VBS feedback - ``smarc_msgs/PercentStamped`` on ``/vehicle/core/vbs_fb``
* LCG feedback - to be decided
* TCG feedback - to be decided

Controller interfaces
---------------------

All controllers reside in the ``/vehicle/ctrl`` namespace. The target of a control may
refer to either of heading, depth, altitude, speed, pitch or roll.
All controllers can be turned on or off by calling the ``/vehicle/ctrl/toggle_{target}_ctrl``
service with ``true`` or ``false`` respectively. If a command setpoint is sent to
``/vehicle/ctrl/{target}_setpoint`` when enabled, the controller tries to control,
otherwise not. Instead of implementing this interface, one can also implement the control
setpoint topic ``/vehicle/ctrl/{target}_setpoint_freq`` that requires publishing at 1hz
to control but has no service. One can then use the ``control_throttle_service`` to automatically
implement the actual interface, see `Controller implementation`_.

If two controllers that are conflicting are activated at the same time, the result
is currently undefined. The same holds for publishing to an actuator that is at the
same time controlled by a controller. In the first case, it is however recommended that
the controller activated second returns false upon request to activate.

**Basic controller topics**

If there are multiple controllers to control one target, they should generally all subscribe
to the same topic. However, only one should be enabled using the services (see next section)
at any given time.

* Heading - ``std_msgs/Float64`` on ``/vehicle/ctrl/yaw_setpoint``
* Depth - ``std_msgs/Float64`` on ``/vehicle/ctrl/depth_setpoint``
* Altitude - ``std_msgs/Float64`` on ``/vehicle/ctrl/altitude_setpoint``
* Speed - ``std_msgs/Float64`` on ``/vehicle/ctrl/speed_setpoint``
* Pitch - ``std_msgs/Float64`` on ``/vehicle/ctrl/pitch_setpoint``
* Roll - ``std_msgs/Float64`` on ``/vehicle/ctrl/roll_setpoint``

**Basic controller services**

If the vehicle implements any of the control targets above, they should
subscribe to the associated topic and offer the service below. If there are
multiple controllers for the same target, the additional ones may offer services
with other suitable names (within the ``/vehicle/ctrl`` namespace) in order to
be enabled or disabled.

* Toggle heading ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_heading_ctrl``
* Toggle depth ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_depth_ctrl``
* Toggle altitude ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_altitude_ctrl``
* Toggle speed ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_speed_ctrl``
* Toggle pitch ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_pitch_ctrl``
* Toggle roll ctrl - ``std_srvs/SetBool`` on ``/vehicle/ctrl/toggle_roll_ctrl``

If the controllers are implemented using the
``/vehicle/ctrl/{target}_setpoint_freq`` scheme (see `Controller implementation`_)
they may need to offer multiple freq topics, that are then mapped to the
same topic by the convenience node.

**Controller status topics**

We propose adding a new message `smarc_msgs/ControllerStatus <https://github.com/smarc-project/smarc_msgs/blob/interface/msg/ControllerStatus.msg>`_
that allows the controllers to announce that they can control a particular target.
It is also used to monitor which controller is controlling any given target at a
particular time. It is expected that all controllers that can control any of the
targets above publish to the following topics at 1hz, running or not:

* Heading - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/yaw_controller_status``
* Depth - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/depth_controller_status``
* Altitude - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/altitude_controller_status``
* Speed - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/speed_controller_status``
* Pitch - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/pitch_controller_status``
* Roll - ``smarc_msgs/ControllerStatus`` on ``/vehicle/ctrl/roll_controller_status``

Planners (advanced controllers)
-------------------------------

Planners are high-level components that may use several primitive controllers to achieve a task.
Examples may be navigation to a waypoint, or surveying a pipeline. Their interface is defined
using `actionlib actions <http://wiki.ros.org/actionlib>`_. The rationale for using actionlib is
that these are often long-running tasks. The higher-level decision making system (behavior tree)
therefore needs ability to monitor progress or cancel the task. actionlib provides an interface for
both of these things, together with convenience libraries in python and c++ to implement actions.

We propose adding the `smarc_msgs/GotoWaypoint <https://github.com/smarc-project/smarc_msgs/blob/noetic-devel/action/GotoWaypoint.action>`_
action to specify a waypoint to travel to. In addition to specifying navigation by depth or
altitude control, it also allows setting RPM or speed control. One can also disable all of
these if other controllers should be used for these targets. Note that the action definition is
future compatible in the sense that we can always add new fields in a source-compatible way.
The action definition is therefore purposefully kept minimal in this proposal.
Note that, at the moment, implementations only respect the xy position of the waypoint.
The z component and orientation might be used in the future.

**Actions**

* Go to waypoint - ``smarc_msgs/GotoWaypointAction`` on ``/vehicle/ctrl/goto_waypoint``

Dead reckoning
--------------

All dead reckoning topics and nodes reside within the ``/vehicle/dr`` namespace.
Note that the odometry topic may be used to construct the TF transformations.
In general, the TF tree will be used to construct the convenience topics:
latitude, longitude, depth, yaw, pitch and roll.

SEE dead_reckoning_msgs package

**Topics**

* Dead reckoning odometry (poses, velocities and uncertainties) - ``nav_msgs/Odometry`` on topic ``/vehicle/dr/odom``
* Latitude longitude position - ``geographic_msgs/GeoPoint`` on ``/vehicle/dr/lat_lon``
* Estimated depth - ``std_msgs/Float64`` on ``/vehicle/dr/depth``
* Estimated yaw (ENU) - ``std_msgs/Float64`` on ``/vehicle/dr/yaw``
* Estimated pitch - ``std_msgs/Float64`` on ``/vehicle/dr/pitch``
* Estimated roll - ``std_msgs/Float64`` on ``/vehicle/dr/roll``
* Estimated heading (NED) - ``std_msgs/Float64`` on ``/vehicle/dr/heading``

TF
--

The TF tree can be constructed from the ``/vehicle/dr/odom`` topic. If ``/vehicle/dr/odom`` is present, it is therefore not necessary to provide the TF tree, although some implementations provide both as one package. For frame naming, we follow `REP 105 <https://www.ros.org/reps/rep-0105.html>`_ wherever possible, except that
we define a utm frame instead of earth (see details below). Note that using REP 105 also means that positions are generally defined in ENU
coordinates, with ``x`` corresponding to easting, ``y`` to northing and ``z`` to height.

**Main frames**

* Shared UTM frame - ``utm``
* Shared local map frame - ``map``
* Vehicle odometry frame ``vehicle/odom``
* Vehicle origin frame ``vehicle/base_link``
* Frames for sensors, as referenced in the header stamp/frame_id messages. E.g. ``vehicle/imu_link``

The resulting TF tree has the structure ``utm -> map -> vehicle/odom -> vehicle/base_link -> vehicle/imu_link``. Note that ``imu_link`` can be exchanged for any other frame on the vehicle.

The ``utm -> vehicle/base_link`` is the most interesting transform as it provides the vehicle pose in the coordinate system of the local UTM zone. Which UTM zone this is referring to is given by the ``/utm_zone`` and ``/utm_band`` parameters, which are set at start-up.

**NED Convenience frames**

These can be useful if we need to get poses in NED coordinates. It should not be used within the ROS system but only to relay information to other systems that used NED.

* UTM NED frame - ``utm_ned`` - rotated parent to ``utm`` that allos getting vehicle pose in NED coordinates

**A note on NED oriented sensors**

If sensors such as IMU or GYRO report measurements in a NED coordinate system, we can still use those measurements
as-is on the vehicle. However, we need to make sure that these sensors are added in a NED-rotated frame on the
vehicle (upside down etc.). They can then be used in any pre-existing features that rely on TF to get measurement poses.

Payloads
--------

These are all optional. They do not need to be published to fulfill the ROS interface specification, but if they are, the should be available in the form presented here.

**Payload sensor topics**

* Sidescan - ``smarc_msgs/SideScan`` on topic ``/vehicle/payload/sidescan``
* CTD - ``smarc_msgs/CTD`` on topic ``/vehicle/payload/ctd``

**Payload sensor services**

* Enable/disable sidescan - ``std_srvs/SetBool`` on ``/vehicle/payload/toggle_sidescan`` - send true to turn on and false to turn off, returns true if successful

**Payload sensor status topics**

We propose adding a new message `smarc_msgs/SensorStatus <https://github.com/smarc-project/smarc_msgs/blob/interface/msg/SensorStatus.msg>`_
that allows the sensor to announce it's current status, i.e. "active", "inactive" and "error".
It is expected that sensors with this feedback publish to the following topics at 1hz, active or not:

* Sidescan status - ``smarc_msgs/SensorStatus`` on ``/vehicle/payload/sidescan_status``, indicates status of sidescan

Tools aiding implementation
===========================

These tools are not part of the vehicle interface specification since they are not required to be implemented for each vehicle. Nodes already exist that implement them, you might expect them to be running on the system, and they may be used to implement the vehicle interface.

tf_lat_lon package
------------------
Apart from the services, the `tf_lat_lon package <https://github.com/smarc-project/smarc_navigation/tree/noetic-devel/tf_lat_lon>`_ also offers a c++ library for doing conversions between tf and latitude/longitude.

**Services (always there)**

We propose adding two new service types `smarc_msgs/LatLonToUTM <https://github.com/smarc-project/smarc_msgs/blob/interface/srv/LatLonToUTM.srv>`_
and `smarc_msgs/UTMToLatLon <https://github.com/smarc-project/smarc_msgs/blob/interface/srv/UTMToLatLon.srv>`_ to convert between latitude
longitude and UTM. Both these and the topic assume that the variables `/utm_zone` and `/utm_band` are set (see `Parameters`_)
and always use that UTM zone, regardless of the lat/lon position.

* Lat lon to UTM conversion - ``smarc_msgs/LatLonToUTM`` on ``/vehicle/dr/lat_lon_to_utm``
* UTM to lat lon conversion - ``smarc_msgs/UTMToLatLon`` on ``/vehicle/dr/utm_to_lat_lon``

**Topics** (if needed for `Dead reckoning`_ interface)

* Latitude longitude from TF - ``geographic_msgs/GeoPoint`` on ``/vehicle/dr/lat_lon``

Controller implementation
-------------------------

For each controller specified in the controller section, we may alternatively implement them to require setpoints at a certain frequency to keep going. In order to translate it to the interface above, we offer a node that repeats a setpoint at a certain frequency depending on if the service has been called to activate the controller. In the specification below, {target} may be either of heading, depth, altitude, speed, pitch or roll. Since they all take in std_msgs/Float64, we can just launch multiple instances of the same node, one for every controlled target.

**Nodes**

* control_throttle_service - offers service ``/vehicle/ctrl/toggle_{target}_ctrl`` to start and stop publishing to ``/vehicle/ctrl/{target}_setpoint_freq``. Listens to ``/vehicle/ctrl/{target}_setpoint`` and republishes at a set frequency if started
