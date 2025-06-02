# WASP Behaviour Tree(BT)
This package is an evolution of the `smarc_bt` package. It is a behaviour tree (BT) implementation for SMaRC AUVs, now compatible with the WARA-PS Agent API specs.

Our tasks have evolved from ros messages to an MQTT-driven API, and the BT has been adapted to work with this new paradigm. The BT is designed to be modular and extensible, allowing for easy addition of new actions and conditions as needed.

## Components
This package is mainly split into three components:
- bt
- vehicles (general setup for vehicle states, particularly a generic vehicle state and a generic sensor object)
- waraps (the wrapper for the WARA-PS Agent API)

## Usage
Your best friend when trying to understand how to use this package is the `smarc2/scripts/smarc_bringups/scripts/quad_bringup.sh` script. It tells you exactly which launch files to investigate and duplicate, and which parameters to change to get the desired behaviour.

## Dependencies
The proper functioning of this setup depends on the following packages:
- `str_json_mqtt_bridge` (inside utilities)
- `smarc2_msgs` (inside messages, mainly used for common topic definitions for smarc vehicles)


## ROS Topics Needed
- Everything under `/robot_name/smarc2/` namespace, which is the main namespace for vehicle-agnostic topics.
- Action Servers need to publish their "heartbeat" to the WARA_PS_ACTION_SERVER_HB_TOPIC for the tasks to show up as available on the MQTT agent.


## ROS Topics Produced
- Everything under `/robot_name/waraps/` namespace, which is the main namespace for WARA-PS Agent API topics. These topics are piped through the MQTT bridge to the desired MQTT broker.

## Disclaimer
This package is under active development and may change significantly in the very near future. It is recommended to keep an eye on the repository for updates and changes. Feel free to contact the maintainers if you have any questions or suggestions.