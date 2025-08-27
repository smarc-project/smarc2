# GeoFence Checker Service

This ROS 2 package provides a service node that checks whether a given geographic point (latitude and longitude) lies within a predefined geofence polygon.

## Overview

The `GeoFenceCheckerService` is a ROS 2 node that reads a geofence polygon from a YAML configuration file and provides a service endpoint for validating if a `GeoPoint` lies within that polygon. It uses a ray-casting algorithm for point-in-polygon determination.

## Features

* Reads geofence polygon coordinates from a YAML file
* Provides a ROS 2 service to check whether a `GeoPoint` is inside the geofence

## Dependencies

* `rclpy`
* `geographic_msgs`
* `smarc_mission_msgs`
* `ament_index_python`
* `yaml`

## Geofence YAML File Format

The YAML file should define a list of latitude-longitude pairs under the `geofence` key:

```yaml
geofence:
  - [59.0, 10.0]
  - [59.1, 10.0]
  - [59.1, 10.1]
  - [59.0, 10.1]
```

This defines a rectangular polygon in geographic coordinates.

## Usage

### Run the Service

```bash
ros2 run geofence_checker geofence_checker_service
```

You can override parameters using ROS 2 parameter files or command-line arguments:

```bash
ros2 run geofence_checker geofence_checker_service --ros-args -p geofence_file:=asko.yaml -p verbose:=true
```

## Service Definition

### Service Name

Defined by `MissionTopics.GEOFENCE_CHECKER_SERVICE`

### .srv File Definition

```
# GeoFenceChecker.srv

# Request
geographic_msgs/msg/GeoPoint geopoint

---

# Response
bool valid
```

### Request

```python
GeoFenceChecker.Request:
  geopoint:
    latitude: float
    longitude: float
```

### Response

```python
GeoFenceChecker.Response:
  valid: bool  # True if inside geofence
```
