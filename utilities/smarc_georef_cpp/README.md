# smarc_georef_cpp
Converts between lat lon and frames in the tf tree. Requires a top level tf frame named
`utm_{zone}_{band}`, e.g. `utm_33_V`, where x is easting and y is northing.

The library is C++ with Python bindings, since a tf listener in Python uses a lot of resources.

Example C++ and Python nodes are in [`smarc_georef_examples`](../smarc_georef_examples/README.md),
including how to depend on this package in `package.xml` and `CMakeLists.txt`.

# Usage in C++
`GeorefUtils` is not a node. Create it as a member of your node; the node must outlive it:

```cpp
#include "smarc_georef_cpp/georef_utils.hpp"

class MyNode : public rclcpp::Node
{
public:
  MyNode()
  : Node("my_node"), georef_(this) {}

private:
  GeorefUtils georef_;
};
```

```xml
<depend>smarc_georef_cpp</depend>
```

```cmake
find_package(smarc_georef_cpp REQUIRED)
target_link_libraries(my_node smarc_georef_cpp::smarc_georef_cpp)
```

It uses the node's clock (so `use_sim_time` works) and receives tf on its own background thread.

# Usage in Python
```python
from smarc_georef_cpp import GeorefUtils, TransformException

self.georef = GeorefUtils(node=self)
```

```xml
<exec_depend>smarc_georef_cpp</exec_depend>
```

The functions have the same names and arguments as in C++ and take and return normal rclpy
messages. The C++ side runs on its own internal rclcpp node and tf thread, so nothing needs to be
added to the rclpy executor. Your node's `use_sim_time` is copied to it at creation; other
parameters and launch remaps don't reach it (pass ROS arguments for it with `ros_args=` if needed).

# Functions
- `get_utm_frame()`: name of the utm frame, e.g. `utm_33_V`. Found in the tf tree on the first call
  and cached after that.
- `geopoint_to_point_stamped(geopoint, target_frame = "")`: lat lon -> utm easting/northing, with
  altitude copied to z, then transformed to `target_frame` (e.g. `lolo/base_link`). An empty
  `target_frame` returns the point in the utm frame. The zone is the utm frame in the tf tree
  when there is one, and the geopoint's own zone when there is not. A frame that appears later
  replaces that guess. (Example 1)
- `point_stamped_to_geopoint(point)`: a `PointStamped` in any frame -> lat lon, with z copied to
  altitude. Uses the timestamp in the point's header (zero means latest). (Example 2)
- `lookup_transform(target_frame, source_frame, timeout_sec = 0.0)`: the latest transform from
  `source_frame` to `target_frame`, waiting up to `timeout_sec`. (Example 3)
- `can_transform(target_frame, source_frame, timeout_sec = 0.0)`: whether that transform is
  available, waiting up to `timeout_sec`. Never throws.

`geopoint_to_point_stamped` uses the zone of the utm frame in the tree, also for a point in a
neighbouring zone. If the tree has no utm frame, it uses the geopoint's own zone. That guess is
not kept: a frame that shows up later replaces it. Transforming into some other `target_frame`
still needs the utm frame in the tree.

`point_stamped_to_geopoint`, `get_utm_frame`, and `lookup_transform` throw
`tf2::TransformException` (`TransformException` in Python) if the frame or the transform is not
available. `can_transform` never throws. Right after startup this is normal until the frames have
been received over tf. Those calls don't wait; call `can_transform` with a timeout first.

These do not use the tf tree. In C++ they are in namespace `smarc_georef`. The Python names are the same.

- `convert_enu_pose_to_heading(enu_pose)`: compass heading in degrees, 0 north and 90 east,
  from the ENU yaw of the pose. Returns a `Float32`.
- `compute_course_from_two_poses(prev, current)`: course in degrees from the two positions.
  0 is +x and 90 is +y. Returns a `Float32`.
- `compute_speed_from_two_poses(prev, current)`: speed in metres per second from the two
  positions and their header stamps. A stamp that does not move forward gives 0. Returns a
  `Float32`.

## tf in Python without a tf listener
Get transforms with `lookup_transform` and apply them in Python with `tf2_geometry_msgs`
(`do_transform_point`, `do_transform_pose_stamped`, ...). This needs
`<exec_depend>tf2_geometry_msgs</exec_depend>`, but no `TransformListener`. See example 3 in the
Python example node.

# Adding functions
To expose a new C++ function to Python: add it to `GeorefUtils`, add a method to `PyGeorefUtils` in
`src/python_bindings.cpp` (return messages with `serialize(msg)`), bind it in `PYBIND11_MODULE`,
and add a wrapper in `smarc_georef_cpp/__init__.py` that calls `deserialize_message`.
