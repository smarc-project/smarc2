# Floatsam External Equipment

Packages for the Floatsam USV platform.

## floatsam_topic_bridge

Topic bridge node that converts Floatsam-specific topics (from simulator or real hardware) to standard SMaRC topics.

### Features

- **Switch between simulation and real hardware** via `use_sim` parameter
- **Configurable via YAML files** for easy topic mapping updates
- **Converts all sensor data** to standard SMaRC format:
  - GPS → `smarc/latlon`
  - IMU → `smarc/heading`
  - Depth pressure → `smarc/depth`
  - Odometry → `smarc/odom`, `smarc/course`, `smarc/speed`
  - Battery → `smarc/battery_percent`
  - Leak sensor → `floatsam/leak_status`

### Usage

**Simulation mode (default):**
```bash
ros2 launch floatsam_topic_bridge floatsam_bridge.launch.py use_sim:=true
```

**Real hardware mode:**
```bash
ros2 launch floatsam_topic_bridge floatsam_bridge.launch.py use_sim:=false
```

⚠️ **Note:** Before using real hardware mode, update [config/real_topics.yaml](floatsam_topic_bridge/config/real_topics.yaml) with actual hardware topic names!

### Configuration Files

- **[sim_topics.yaml](floatsam_topic_bridge/config/sim_topics.yaml)** - Simulator topic mappings (ready to use)
- **[real_topics.yaml](floatsam_topic_bridge/config/real_topics.yaml)** - Real hardware topic mappings (⚠️ PLACEHOLDERS - must be updated!)

### Topics Published

All topics follow the standard defined in [smarc_msgs/msg/Topics.msg](/messages/smarc_msgs/msg/Topics.msg):

- `smarc/latlon` (geographic_msgs/GeoPoint)
- `smarc/heading` (std_msgs/Float32)
- `smarc/depth` (std_msgs/Float32)
- `smarc/odom` (nav_msgs/Odometry)
- `smarc/course` (std_msgs/Float32)
- `smarc/speed` (std_msgs/Float32)
- `smarc/battery_percent` (std_msgs/Float32)
- `floatsam/leak_status` (std_msgs/Bool)
