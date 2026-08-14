# Validate Bag 

This directory contains the `validate_bag.py` script and the helper scripts `data_processing.py` and `plotting.py`, designed to visualize and manipulate extracted data from a ROS 2 bag for system identification. 


## Workflow

1. **Analyze Timestamps and Identify Mission Phases**: Visualize the drone's trajectory over the mission and identify phases of the mission by looking at `smarc/odom` or, ideally, `/M350/wrapper/psdk_ros2/flight_control_setpoint_FLUvelocity_yawrate`. 
   * **NOTE**: If the system identification is conducted using the Best Linear Approximation Method, the inputs must be periodic, and the mission must be divided into periods. 
   * Additionally, examine the plots related to timestamps to identify sections with missing data or high lag.
2. **Segment Data**: Segment the data according to the phases identified in the previous step. *(Make sure to update the `segments` bounds in the script to match your identified phases).*
3. **Process Data**: Each segment must be processed independently using the same parameters. The data processing pipeline is as follows:
    1. Relevant topics (such as Velocity Ground Fused) are rotated and converted to the FLU frame.
    2. Data is resampled and filtered onto a uniform time grid.