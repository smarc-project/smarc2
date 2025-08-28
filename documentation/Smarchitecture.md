# SMaRChitecture
This document details the general structure that all vehicles that touch some part of the SMaRC project should follow.

#### General Idea
- We use ROS messages `xxx_msgs.msg/Topics.msg` and `xxx_msgs/Links.msg` as global shared dictionaries that define common strings in the context of `xxx`.
  - For example: `smarc_msgs/Topics.msg` contains topic names for vehicle-agnostic mid-level hardware abstraction.
  - Use these message definitions to avoid hard-coding topics and links in your nodes!
  - All `Topics` messages should include the message type expected as a comment next to the string.
  - These 
    - avoid the question of "what is the topic for...?"
    - allow self-discovery: "Is there a topic for...?"
    - keep the documentation in front of the people implementing things. No need to hunt a PDF to find out the message type of `smarc_msgs/Topics.msg::pos_latlon`

- All nodes/launch files take `robot_name` as a ROS param and append in front of topics/links as needed
  - No hard-coded `robot_names` for TF frames.
  - Use namespacing in launch files with the `robot_name` as the base.
  - _Everything_ that a launchfile/node pubs/subs must be under the same `robot_name`.

#### Low-level HAL
- **\<vehicle\>_topics** and **\<vehicle\>_links** ROS messages act as the "low-level" hardware abstraction
  - For example: `sam_msgs/Topics.msg` contains topics specific to the SAM vehicle, used by nodes that communicate internally for SAM.
  - These are vehicle-specific and can be custom types as needed.

#### Mid-level HAL
- `smarc_msgs/Topics.msg` and `smarc_action_base.gentler_action_server::GentlerActionServer` are the "mid-level", inside-the-vehicle hardware abstraction layer.
  - The topics should be kept as base types i.e no custom message types.
  - The main consumer of this layer is the **WaspBT**, which is vehicle-agnostic.
    - The `GentlerActionServer` has all the mechanisms to make a ROS action server easily, that can interact with the **WaspBT**.

#### High-level HAL
- [WARA-PS API](https://api-docs.waraps.org/#/agent_communication/agent_communication) is the "high-level", outside-the-vehicle level of abstraction.
	- **WaspBT** can act as a bridge between the vehicle and this layer (See SAM, LoLo, ALARS)
	- Vehicles can choose to implement the WARA-PS API directly from the hardware, without using the above levels. (See Evolo/Puffins)

#### Simulator
- The sim has a finger on every level:
	- Can mimic the hardware by publishing sensor data and listening to actuation signals at the **low-level**
	- Can mimic the in-vehicle ROS-stack by publishing into **SmarcTopics** directly, touching the **mid-level**
	- Can mimic the entire vehicle at a **high-level** by publishing into **WARA-PS API** directly
	- **C2** sees vehicles through the **WARA-PS API** only


## Graphical
Large images, zooming in recommended :)

### Without simulator
![nosim](/documentation/media/Smarchitecture_nosim.png)

### With simulator
The simulator is split into 3 separate nodes to avoid too many lines overlapping, but it is the same sim.

![withsim](/documentation/media/Smarchitecture_withsim.png)


## Example workflows:
- **Controller dev**
  - SIM -> GT state -> HAL-Low -> do-thing Action Server -> actuation -> SIM
- **DR/SLAM dev**
  - SIM -> drive around manually
  - SIM -> sensor data -> vehicle-nodes for DR  -> state -> estimate
  - SIM -> GT state
  - Compare estimate vs GT
- **BT dev**
  - SIM -> SmarcTopics -> state -> WaspBT ->  state+cmd -> WARA-PS API -> SIM and back
- **Real vehicle**
  - Vehicle -> Sensor data -> vehicle-nodes ->  
  	- SmarcTopics -> WaspBT -> WARA-PS API -> SIM(C2) -> cmd -> WARA-PS API -> WaspBT -> cmd ->
	- state -> HAL-Low -> state ->
  - *state and cmd from above lines* -> do-something-action-server (GentlerActionServer) -> actuation -> Vehicle
