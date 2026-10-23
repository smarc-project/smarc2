# sam_captain

ROS 2 interface node for SAM vehicle status. It translates battery, dead-reckoning,
DVL, UTM, and geofence inputs into the common SMARC navigation/status topics and
publishes vehicle health.

## Run

Build the package and source the workspace:

```bash
cd ~/smarc_ws
colcon build --packages-select sam_captain
source install/setup.bash
```

Testing, optional, but can be done with:

```bash
colcon test --packages-select sam_captain --event-handlers console_direct+
```

Then, to launch the node:

```bash
ros2 launch sam_captain sam_captain.launch.py
```

Note that the default launch arguments are:

- `robot_name:=sam`
- `use_sim_time:=false`

To launch this along with other nodes for sam:

```bash
cd ~/smarc_ws/src/smarc2/scripts/smarc_bringups/scripts
./sam_bringup.sh 
```

## TODO

- Declare and load node parameters from `config/sam_captain_params.yaml`.
- Make health thresholds and input freshness timeouts configurable.
- Review and document the vehicle-health policy, especially geofence handling.
