# SMARC Geofence Utils

Reusable C++ geofence/path validation helpers.

Current API:

```text
check_path_against_geofence(nav_msgs/Path, smarc_msgs/GeofencePolygonsStamped)
```

The checker expects both messages to already be in the same Cartesian frame. It
does not transform frames or own geofence lifecycle. `smarc_basic/geofence_node`
remains the source of geofence status and map-frame polygons.

The path is accepted only if:

```text
- path frame matches geofence polygon frame
- at least one geofence polygon is defined
- every path point is inside at least one geofence polygon
- no path point is inside an island polygon
- every path segment is contained by at least one geofence polygon
- no path segment crosses an island boundary
```

TODO: Add a thin ROS service wrapper around this library for tools, mission
validation, Python clients, and debugging. Control-loop users should prefer
calling the library directly to avoid service latency and availability coupling.
