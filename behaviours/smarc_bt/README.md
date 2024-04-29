# SMaRC Behaviour Tree(BT)

This package contains the BT used for the SMaRC vehicles (Mainly SAM and LoLo).

The main structure of the BT looks something like this (as of 2024-04-29): 
```
[-] S_Root [x]
     --> C_VehicleSensorsWorking [o]
     --> A_Heartbeat [o]
     --> A_ProcessBTCommand [o] -- No command to process (queue empty)
     [o] F_Safety [o]
         /_/ P_Safety_Checks [o]
             --> C_NotAborted [o]
             --> C_ALTITUDE[0] gt MIN_ALTITUDE [o] -- gt(47.79, 2.00)
             --> C_DEPTH[0] lt MAX_DEPTH [o] -- lt(0.15, 10.00)
             -^- Not leaking [o] -- failure -> success
                 --> C_CheckVehicleSensorState(LEAK[0]) [x]
             --> C_MissionTimeoutOK [o] -- Mission==None
         --> A_Abort [-]
     [o] F_Run [x]
         --> C_CheckMissionPlanState(STOPPED) [x] -- Mission==None
         [-] S_Finalize_Mission [x]
             --> C_CheckMissionPlanState(COMPLETED) [x] -- Mission==None
             --> A_UpdateMissionPlan(complete) [-]
         [o] F_Mission [x]
             [-] S_Follow_WP_Plan [x]
                 --> C_CheckMissionPlanState(RUNNING) [x] -- Mission==None
                 --> A_ActionClient(ROSGotoWaypoint) [-]
                 --> A_UpdateMissionPlan(complete_current_wp) [-]
```
While the specific structure of the BT might be different, the symbolism used to display it will not be.

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
- mission
- vehicles

Components are defined in an entity-component pattern where for example a generic mission plan object is wrapped in a ROS-connected mission plan object, a generic vehicle object is wrapped in a ROS-connected vehicle object etc. 

Files are named to make these wrappers clear. Things prefixed `ros_` connect to ROS and usually sub/pub to topics. Things prefixed `i_` are empty objects that only define an interface that other objects concretify.

If a file does not have `ros_` prefix, it should not be importing anyting with `rclpy` in it and thus can be used by other packages without worry of dependencies.
A good example of this would be `vehicle.py`.


> Notice a lack of some non-ros version of things, like the `bt`, `bb_updater`, `mission_updater` and so on. Due to our need being ROS-specific, non-ros versions of these are not needed. Yet. But the structure of the package is such that it is possible.

### bt
- **ros_bt**: A concrete BT defined for an AUV such as SAM or LoLo. Takes as input generic objects such as an `IBBUpdater`, `IBBMissionUpdater` and `IActionClient` to allow a user to modify the data i/o without modifying the BT structure.
- **actions**:
All the action nodes used in the BT. Usually written as generically as possible to avoid repetition. For example `A_UpdateMissionPlan` takes as argument a function to call when ticked. `A_ActionClient` takes a generic `IActionClient` object to call its methods on when ticked etc.
- **conditions**: Same deal as actions, but for condition nodes.
- **common**: Some common base classes for actions and conditions to extend. Mostly for convenience.
- **bb_keys**: An enum to use when accessing blackboard variables across this package.
- **ros_bb_updater**: Implements the `IBBUpdater` interface as an object that creates ros parameters and continously updates the BB with their up to date values. Effectively allows parameters to be changed live in a generic way.


### mission
- **mission_plan**: A generic mission plan object that keeps track of its state and waypoints. Can take different kinds of waypoints as needed.
  - **ros_mission_plan**: Extends the generic mission plan with ROS connections.
- **waypoint**: Generic waypoint objects. 
  - **ros_waypoint**: Implements the underwater waypoint interface by exposing a `smarc_misison_msgs.msg::GotoWaypoint` message's fields.
- **ros_mission_updater**: Implements `IBBMissionUpdater` with ROS connections. 
- **ros_goto_waypoint**: Implements `IActionClient` with a ROS action client.

### vehicles
- **sensor**: Defines generic sensors with possibly multiple fields each. The sensor object keeps track of its update times and current values. Instead of defining different sensors individually, this way we can create new sensors on the fly as needed without changing much anywhere else.
- **vehicle**: Defines a generic vehicle state with a position, orientation, global position, global orientation, a battery and a list of sensors. The `IVehicleState` and `IVehicleStateContainer` interfaces are defined here too.
  - **ros_vehicle**: Wraps an `IVehicleState` object in ROS connections. 
    - **sam_auv**: Extends the `ROSVehicle` SAM-AUV specific topics and sensors.