# ROS 2 Bag to Parquet Extractor

This script contains Python utilities designed to extract, flatten, and convert ROS 2 bag data (`.db3`) into columnar Parquet files. 

## Features 
* **Selective Extraction**: Reads a YAML configuration file to only extract the topics you explicitly need.
* **Automatic Message Flattening**: Recursively flattens nested ROS 2 message structures (e.g., arrays and sub-messages) into a single-level dictionary structure via prefixing.
* **Dual Timestamping**: Automatically extracts both the bag recording timestamp (`bag_timestamp_sec`) and the message header timestamp (`header_timestamp_sec`, if available).
* **Parquet Export**: Saves each topic as an independent, highly compressed `.parquet` file.
* **Extraction Summary**: Prints a detailed post-processing summary, including message counts, calculated publishing frequencies (Hz), and warnings for missing topics.

## Topic Selection
For the system identification conducted on the M350, the topics used were:
* `/M350/wrapper/psdk_ros2/velocity_ground_fused`: Used as the output of the system.
* `/M350/wrapper/psdk_ros2/flight_control_setpoint_FLUvelocity_yawrate`: Used as the input of the system.
* `/M350/wrapper/psdk_ros2/attitude`: Used to transform data from the ENU reference frame to FLU.

All the other topics in `config.yaml` were used to verify the consistency of the data in the bag. Data related to the motors might be used to identify a transfer matrix from `/M350/wrapper/psdk_ros2/flight_control_setpoint_FLUvelocity_yawrate` to the motors.