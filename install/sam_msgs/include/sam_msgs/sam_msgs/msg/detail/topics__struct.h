// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'VBS_CMD_TOPIC'.
/**
  * Actuator commands
 */
static const char * const sam_msgs__msg__Topics__VBS_CMD_TOPIC = "core/vbs_cmd";

/// Constant 'LCG_CMD_TOPIC'.
static const char * const sam_msgs__msg__Topics__LCG_CMD_TOPIC = "core/lcg_cmd";

/// Constant 'THRUSTER1_CMD_TOPIC'.
static const char * const sam_msgs__msg__Topics__THRUSTER1_CMD_TOPIC = "core/thruster1_cmd";

/// Constant 'THRUSTER2_CMD_TOPIC'.
static const char * const sam_msgs__msg__Topics__THRUSTER2_CMD_TOPIC = "core/thruster2_cmd";

/// Constant 'THRUST_VECTOR_CMD_TOPIC'.
static const char * const sam_msgs__msg__Topics__THRUST_VECTOR_CMD_TOPIC = "core/thrust_vector_cmd";

/// Constant 'DEPTH_TOPIC'.
static const char * const sam_msgs__msg__Topics__DEPTH_TOPIC = "core/depth20_pressure";

/// Constant 'DVL_TOPIC'.
static const char * const sam_msgs__msg__Topics__DVL_TOPIC = "core/dvl";

/// Constant 'LEAK_TOPIC'.
static const char * const sam_msgs__msg__Topics__LEAK_TOPIC = "core/leak";

/// Constant 'VBS_FB_TOPIC'.
static const char * const sam_msgs__msg__Topics__VBS_FB_TOPIC = "core/vbs_fb";

/// Constant 'LCG_FB_TOPIC'.
static const char * const sam_msgs__msg__Topics__LCG_FB_TOPIC = "core/lcg_fb";

/// Constant 'THRUSTER1_FB_TOPIC'.
static const char * const sam_msgs__msg__Topics__THRUSTER1_FB_TOPIC = "core/thruster1_fb";

/// Constant 'THRUSTER2_FB_TOPIC'.
static const char * const sam_msgs__msg__Topics__THRUSTER2_FB_TOPIC = "core/thruster2_fb";

/// Constant 'STIM_IMU_TOPIC'.
static const char * const sam_msgs__msg__Topics__STIM_IMU_TOPIC = "core/imu";

/// Constant 'SBG_IMU_TOPIC'.
static const char * const sam_msgs__msg__Topics__SBG_IMU_TOPIC = "core/sbg_imu";

/// Constant 'PRESS_DEPTH20_TOPIC'.
static const char * const sam_msgs__msg__Topics__PRESS_DEPTH20_TOPIC = "core/depth20_pressure";

/// Constant 'SIDESCAN_TOPIC'.
static const char * const sam_msgs__msg__Topics__SIDESCAN_TOPIC = "payload/sidescan";

/// Struct defined in msg/Topics in the package sam_msgs.
/**
  * This is a file that defines all the topics of sam.
  * The goal is to have one location that all cpp/py scripts
  * can easily access and thus avoid having 100 parameters for topics all
  * over the place, repeated for all subs/pubs...
  * It is assumed that the nodes will namespace as needed.
 */
typedef struct sam_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} sam_msgs__msg__Topics;

// Struct for a sequence of sam_msgs__msg__Topics.
typedef struct sam_msgs__msg__Topics__Sequence
{
  sam_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
