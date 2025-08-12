# WASP Behaviour Tree(BT)
This package is an evolution of the `smarc_bt` package. It is a behaviour tree (BT) implementation for SMaRC AUVs, now compatible with the WARA-PS Agent API specs.

Our tasks have evolved from ros messages to an MQTT-driven API, and the BT has been adapted to work with this new paradigm. The BT is designed to be modular and extensible, allowing for easy addition of new actions and conditions as needed.

## Components
This package is mainly split into three components:
- bt
- vehicles (general setup for vehicle states, particularly a generic vehicle state and a generic sensor object)
- waraps (the wrapper for the WARA-PS Agent API)

## Usage
Your best friend when trying to understand how to use this package is the `smarc2/scripts/smarc_bringups/scripts/lolo_bringup.sh` script. It tells you exactly which launch files to investigate and duplicate, and which parameters to change to get the desired behaviour.

## Dependencies
The proper functioning of this setup depends on the following packages:
- `str_json_mqtt_bridge` (inside utilities)
- `smarc_msgs` (inside messages, mainly used for common topic definitions for smarc vehicles)


## ROS Topics Needed
- Everything under `/robot_name/smarc/` namespace, which is the main namespace for vehicle-agnostic topics.
- Action Servers need to publish their "heartbeat" to the WARA_PS_ACTION_SERVER_HB_TOPIC for the tasks to show up as available on the MQTT agent.

**NOTE:** The WARA-PS agent will only report data to the MQTT broker if the SMaRC topics are being published by the vehicle. So remember to make a publisher that fills out the SMaRC topics.

### HEALTH TOPIC
The Behavior Tree has a health subtree that listens to the output of the vehicle health node on SMaRCTopics.VEHICLE_HEALTH_TOPIC. If you don't have a vehicle health node running, refer to the `smarc2/scripts/smarc_bringups/scripts/lolo_bringup.sh` script for a way to "fake" the vehicle health node. This is necessary for the behaviour tree to function properly, as it relies on the health status of the vehicle to make decisions. Not recommended on a real vehicle.


## ROS Topics Produced
- Everything under `/robot_name/waraps/` namespace, which is the main namespace for WARA-PS Agent API topics. These topics are piped through the MQTT bridge to the desired MQTT broker.

## Quick Start
To start the behaviour tree, you can use the `smarc2/scripts/smarc_bringups/scripts/quad_bringup.sh` or its equivalent for your specific vehicle. Remember to launch the `str_json_mqtt_bridge` first, as it is responsible for bridging the ROS topics to the MQTT topics.

If using the local MQTT broker settings (refer to the bringup), remember to spin up a locally hosted MQTT broker. You may need to install Mosquitto.
```bash
mosquitto -p 1889
```

Next, the launchfile for the behaviour tree will launch two separate nodes:
- `wasp_bt`: This node is responsible for running the behaviour tree.
- `waraps_vehicle`: This node is responsible for publushing data to ros topics namespaced under `/robot_name/waraps/`, which is the main namespace for WARA-PS Agent API topics.

Once you have the agent showing up on the MQTT broker, you can start sending tasks to it. Remember to launch the servers for each action you want to use in the behaviour tree. The action servers need to publish their "heartbeat" to the `WARA_PS_ACTION_SERVER_HB_TOPIC` for the tasks to show up as available on the MQTT agent, and for the behaviour tree to have subtrees for handling those tasks.

Remember to start all the servers you want clients for!

## Emergency Action and Reset
The Behaviour Tree expects an emergency action to be running under the `/robot_name/emergency_action` topic. This action is responsible for handling emergency situations, such as when the vehicle is in an unsafe state or needs to stop immediately. If not found, the behaviour tree default to "doing nothing" in case of an emergency.

In case an emergency is thrown but you manage to resolve it, you can reset the emergency state of the vehicle by calling the `/robot_name/reset_emergency` service. This will allow the behaviour tree to continue running without being stuck in an emergency state.

```bash
ros2 service call /$ROBOT_NAME/reset_emergency std_srvs/srv/Trigger
```

## Link to Demo Video
We have prepared a demonstration video showcasing the WASP Behaviour Tree in action. This video provides an overview of the system, its integration with the WARA-PS Agent API, and a walkthrough of the main features.

[![Watch the demo](https://img.youtube.com/vi/0_u3yiqz02/0.jpg)](https://play.kth.se/media/Shekhar+Devm+Upadhyay%27s+Personal+Meeting+Room/0_u3yiqz02)

You can watch the demo here:  
[Shekhar Devm Upadhyay's Personal Meeting Room (KTH Play)](https://play.kth.se/media/Shekhar+Devm+Upadhyay%27s+Personal+Meeting+Room/0_u3yiqz02)

We hope this helps you get started and provides valuable insights into the capabilities of this package!

## Behavior Tree Structure and Symbols

The behavior tree visualization uses specific symbols to represent different node types and their current states. Understanding these symbols will help you debug and monitor the BT execution.

### Current BT Structure
```
[-] S_Root [*]
    --> A_Heartbeat [o]
    [o] F_HandleEmergency [o]
        --> C_NoEmergencyAbortSignalDetected [o]
        --> A_ActionClient(emergency_action) [-]
    [o] F_Health_Handler [o]
        [-] S_Health_Status [x]
            --> C_HasHeardFromVehicleHealth [o] -- Vehicle health received.
            --> C_LastHealthy [o] -- Comms are fine. Vehicle health is up to date.
            --> C_VehicleHealthStatus [x]
        --> A_Abort [o] -- !! ABORTED !!
    [o] F_Task_Handler [*]
        [-] S_BreatheAfterAbort [x]
            --> C_AbortedPreviousTask [x] -- Previous task was not aborted
            --> A_TaskAbortedFlagReset [-]
        [-] S_auv-depth-move-to [x]
            --> C_TaskIs auv-depth-move-to [x] -- No tasks executing
            [o] F_StatusCheck [-]
                --> C_TaskStatus started [-]
                --> C_TaskStatus resumed [-]
                --> C_TaskStatus running [-]
            --> A_ActionClient(/sam/auv_depth_move_to) [-]
            --> A_ClearCurrentTask [-]
        --> A_Chilling [*] -- No mission, just chillin'...
```

### Node Type Symbols (Left Side)
- `[-]` **Sequence node** - Executes children in order, fails if any child fails. Names prefixed with `S_`
- `[o]` **Fallback/Selector node** - Tries children in order until one succeeds. Names prefixed with `F_`
- `-->` **Actions or Conditions** - Leaf nodes that perform actions or check conditions. Names prefixed with `A_` or `C_`
- `/_/` **Parallel node** - Executes multiple children simultaneously. Names prefixed with `P_`
- `-^-` **Decorator node** - Modifies child behavior (various types available)

### Execution State Symbols (Right Side)
- `[-]` **Not ticked** - Node hasn't been executed this cycle
- `[o]` **Success** - Node completed successfully
- `[x]` **Failure** - Node failed to complete
- `[*]` **Running** - Node is currently executing (for long-running actions)

### Feedback Messages
Each node can display feedback after `--`. For example:
- `C_HasHeardFromVehicleHealth [o] -- Vehicle health received.` shows health communication status
- `C_TaskIs auv-depth-move-to [x] -- No tasks executing` indicates no current task is running
- `A_Chilling [*] -- No mission, just chillin'...` shows the system is idle and waiting

This visualization helps you understand which parts of the behavior tree are active, succeeding, or failing during execution. In this example, the tree is currently running (`[*]`) with the `A_Chilling` action active since no tasks are executing.

## Disclaimer
This package is under active development and may change significantly in the very near future. It is recommended to keep an eye on the repository for updates and changes. Feel free to contact the maintainers if you have any questions or suggestions.

### Future Work
- [ ] Expanding/contracting the BT dynamically based on liveliness of action servers
- [ ] Parallelisation of tasks (currently we employ a queue mission structure)