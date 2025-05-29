# WASP Behaviour Tree(BT)

This package is an evolution of the `smarc_bt` package. It is a behaviour tree (BT) implementation for SMaRC AUVs, now compatible with the WARA-PS Agent API specs.

# Everything below is outdated and should be removed or updated

Our tasks have evolved from ros messages to an MQTT-driven API, and the BT has been adapted to work with this new paradigm. The BT is designed to be modular and extensible, allowing for easy addition of new actions and conditions as needed.

Symbols on the left side:
- `[-]` Sequence node. We also prefix their names  nodes with `S_`. 
- `[o]` Fallback/Selector node. Names prefixed with `F_`.
- `-->` Actions or Conditions. Names prefixed with `A_` or `C_` respectively.
- `/_/` Paralel node. Prefixed with `P_`.
- `-^-` Decorator node. Can be many different kinds, so no specific naming scheme.

Symbols on the right side:
- `[-]` Node is not ticked
- `[o]` Node is returning Success
- `[x]` Node is returning Failure
- `[*]` Node is returning Running

In addition, each node can display an arbitrary string as a feedback message after  `--`. In the above example, the node `C_ALTITUDE[0] gt MIN_ALTITUDE [o]` is displaying `gt(47.49 2.00)` as a feedback message.

## Components
This package is mainly split into three components:
- bt
- vehicles (general setup for vehicle states, particularly a generic vehicle state and a generic sensor object)
- waraps (the wrapper for the WARA-PS Agent API)

## Usage
Your best friend when trying to understand how to use this package is the `smarc2/scripts/smarc_bringups/scripts/quad_bringup.sh` script. It tells you exactly which launch files to investigate, and what parameters to change to get the desired behaviour.

## Dependencies
The proper functioning of this setup depends on the following packages:
- `str_json_mqtt_bridge` (inside utilities)
- `smarc2_msgs` (inside messages, mainly used for common topic definitions for smarc vehicles)

