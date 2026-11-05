# smarc_georef_examples
Example nodes using [`smarc_georef_cpp`](../smarc_georef_cpp/README.md):
`scripts/georef_example_node.py` (Python) and `src/georef_example_node.cpp` (C++).

# Adding smarc_georef_cpp to your package
## C++
`package.xml`:
```xml
<depend>smarc_georef_cpp</depend>
```

`CMakeLists.txt`:
```cmake
find_package(smarc_georef_cpp REQUIRED)
target_link_libraries(my_node smarc_georef_cpp::smarc_georef_cpp)
```

Your node, with `GeorefUtils` as a member:
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

## Python
`package.xml`:
```xml
<exec_depend>smarc_georef_cpp</exec_depend>
<!-- only if you apply transforms with tf2_geometry_msgs, as in example 3 -->
<exec_depend>tf2_geometry_msgs</exec_depend>
```

Your node:
```python
from rclpy.node import Node
from smarc_georef_cpp import GeorefUtils, TransformException


class MyNode(Node):

    def __init__(self):
        super().__init__('my_node')
        # node=self copies this node's use_sim_time to the library
        self.georef = GeorefUtils(node=self)
```

# The examples
Once a second (on the node's clock, so in sim time with `use_sim_time`) both nodes run three
independent examples, each in its own function with hard coded inputs. Each catches
`TransformException` and logs `<n>. Not ready: <reason>` (at most every 5 s) until the frames it
needs have been received over tf.

1. **GeoPoint to vehicle frame** (`geopoint_to_vehicle_frame`): takes the GeoPoint (59.35, 18.07)
   and gets its position relative to the vehicle with
   `geopoint_to_point_stamped(geopoint, "lolo/base_link")`. Use this e.g. for a waypoint given in
   lat lon. Needs a `utm_{zone}_{band}` frame connected to `lolo/base_link`.
2. **Vehicle frame to GeoPoint** (`vehicle_frame_to_geopoint`): takes a point 10 m ahead of the
   vehicle in `lolo/base_link` and gets its lat lon with `point_stamped_to_geopoint(point)`. Use
   this e.g. to report a detection's position. Needs the same frames as example 1.
3. **Transform between two frames** (`base_link_to_odom_transform`): gets the transform from
   `lolo/base_link` to `lolo/odom`, i.e. the vehicle pose in `lolo/odom`, with
   `lookup_transform("lolo/odom", "lolo/base_link")`. This works for any two frames, not only
   utm ones. The Python node then transforms a point 10 m ahead of the vehicle into `lolo/odom`
   with `tf2_geometry_msgs.do_transform_point`, which shows how a Python node can use tf without a
   `TransformListener` of its own. Needs `lolo/odom` connected to `lolo/base_link`.

# Running
```
ros2 run smarc_georef_examples georef_example_node.py   # Python
ros2 run smarc_georef_examples georef_example_node      # C++

ros2 launch smarc_georef_examples georef_example_py.launch.py use_sim_time:=true
ros2 launch smarc_georef_examples georef_example_cpp.launch.py use_sim_time:=true
```
