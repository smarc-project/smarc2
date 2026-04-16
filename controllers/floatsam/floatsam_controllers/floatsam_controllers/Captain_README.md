# FloatSam Captain Controller

The `Captain` node is the primary, integrated low-level controller for the FloatSam surface USV. **Crucially, this node serves as the central actuation hub used by all action servers in the system.** Action servers send their high-level navigational setpoints here, and the Captain translates them into safe, physical motor commands.

It operates using three cascaded PID controllers (yaw, yaw rate, and velocity) mixed into differential thrust commands for port and starboard thrusters. It includes a robust suite of safety checks, deadband management, rate limiting, and dynamic turn-in-place behavior to handle large heading errors safely.

## Dependencies

* **ROS 2** (Python)
* **Python Packages:** `numpy`, `json`
* **Custom Interfaces/Modules:** * `smarc_msgs.msg`, `smarc_control_msgs.msg`, `floatsam_msgs.msg`
  * `floatsam_controllers.pid`
  * `floatsam_controllers.geometry`
* **Standard ROS 2 Messages:** `std_msgs/Float32`, `std_msgs/String`, `std_msgs/Bool`

## Detailed Control Pipeline and Safety Checks

The `Captain` node runs a strict control loop at the configured `update_rate` (default 20 Hz). Every cycle, the data passes through the following sequence of calculations and safety checks:

### 1. Data Freshness and Timeout Checks
Before calculating any motor commands, the node verifies that the USV's sensors and action servers are actively communicating. 
* **The Check:** It compares the current system time against the timestamps of the last received measurements (yaw, yaw rate, velocity) and the last received setpoints. 
* **The Fallback:** If **any** of these inputs are older than 1.0 second, the node immediately aborts the control calculation, logs a warning, and publishes `0.0` RPM to both thrusters to prevent the USV from running away with stale data.

### 2. Cascaded Heading Control (Yaw $\rightarrow$ Yaw Rate)
If the data is fresh, the node calculates the heading error.
* It converts the current heading and the setpoint heading into 2D vectors and calculates the directed angle between them (handling standard $\pi$ to $-\pi$ wraparound issues automatically).
* The **Yaw PID** takes this heading error and outputs a desired *yaw rate*.
* The **Yaw Rate PID** then compares this desired rate against the measured yaw rate from the sensors, outputting a raw `yaw_actuation` value (in RPM).

### 3. Turn-in-Place vs. Forward Movement Logic
The node evaluates the heading error against the `yaw_threshold` to decide how to move.

* **Normal Movement:** If the absolute heading error is less than or equal to `yaw_threshold` (or if `move_on_place` is set to False), the **Velocity PID** runs normally. It compares the current speed to the setpoint speed and outputs a `velocity_rpm_setpoint`. The `yaw_actuation` is used exactly as computed.
* **Turn-in-Place:** If the heading error is strictly greater than `yaw_threshold` and `move_on_place` is True, the node forces the `velocity_rpm_setpoint` to `0.0`. It then overrides the standard yaw actuation using a custom turn-in-place function:
  * It calculates a strict magnitude: `max(abs(yaw_actuation), turn_in_place_min_rpm, turn_in_place_gain * error_magnitude)`.
  * **The Check:** This ensures the thrusters receive at least the `turn_in_place_min_rpm` to overcome the physical stiction of the water/motors, preventing the USV from stalling when trying to correct a large error.
  * It then applies the sign of the original yaw error to this magnitude to ensure it rotates the correct way without zero-crossing oscillation.

### 4. Differential Mixer
The computed forward velocity RPM and the rotational yaw RPM are mixed into raw left and right thruster commands:
* `thruster_port_raw = velocity_rpm_setpoint - yaw_correction`
* `thruster_strb_raw = velocity_rpm_setpoint + yaw_correction`

### 5. Delta RPM Rate Limiting (Mechanical Safety)
To prevent mechanical shock to the thrusters from sudden spikes in the PID outputs, the node applies a rate limiter.
* **The Check:** It compares the newly calculated raw RPM against the actual RPM commanded in the previous control cycle.
* If the difference exceeds `max_delta_rpm`, it caps the change. For example, if the previous command was 100 RPM, `max_delta_rpm` is 200, and the new raw command is 800 RPM, it will only output 300 RPM for this cycle, smoothing out the acceleration curve.

### 6. Saturation Check
Both thruster commands are strictly clamped between `-thruster_limit` and `+thruster_limit` (default $\pm 1000$ RPM) to protect the hardware from over-exertion.

### 7. RPM Deadband Check
* **The Check:** Finally, the node checks if the absolute value of the commanded RPM for either thruster falls below the `rpm_deadband` (default 50 RPM).
* If it does, the command is forced to `0.0`. This prevents the system from sending low PWM signals that consume power and generate heat but aren't strong enough to actually spin the propellers.

### 8. Output
The final, fully validated and safety-checked commands are published to `<THRUSTER_PORT_CMD>` and `<THRUSTER_STRB_CMD>`.

## Subscribed Topics
* `<CONTROL_YAW_TOPIC>` (`std_msgs/Float32`)
* `<CONTROL_YAW_RATE_TOPIC>` (`std_msgs/Float32`)
* `<CONTROL_SURGE_RATE_TOPIC>` (`std_msgs/Float32`)
* `<YAW_SETPOINT>` (`smarc_msgs/FloatStamped`)
* `<VELOCITY_SETPOINT>` (`smarc_msgs/FloatStamped`)
* `/<robot_name>/captain_parameters` (`std_msgs/String`): Accepts JSON strings to dynamically update PID gains.
* `move_on_place` (`std_msgs/Bool`): Toggles the turn-in-place behavior.

## Configurable Parameters
*(All limits, gains, deadbands, and thresholds mentioned above can be configured at launch via ROS 2 parameters. See the launch file for default values).*