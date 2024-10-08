// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_control_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'STATES'.
/**
  * Control topics
  *
  * States
  * Type: Odometry
 */
static const char * const smarc_control_msgs__msg__Topics__STATES = "core/odom_gt";

/// Constant 'DEPTH_SETPOINT'.
/**
  * Setpoints
  * Type: Float64
 */
static const char * const smarc_control_msgs__msg__Topics__DEPTH_SETPOINT = "ctrl/depth_setpoint";

/// Constant 'PITCH_SETPOINT'.
/**
  * Type: Float64
 */
static const char * const smarc_control_msgs__msg__Topics__PITCH_SETPOINT = "ctrl/pitch_setpoint";

/// Constant 'STATES_CONV'.
/**
  * Convenience Topics
  * Type: ControlState
 */
static const char * const smarc_control_msgs__msg__Topics__STATES_CONV = "ctrl/conv/states";

/// Constant 'REF_CONV'.
/**
  * Type: ControlReference
 */
static const char * const smarc_control_msgs__msg__Topics__REF_CONV = "ctrl/conv/ref";

/// Constant 'CONTROL_ERROR_CONV'.
/**
  * Type: ControlError
 */
static const char * const smarc_control_msgs__msg__Topics__CONTROL_ERROR_CONV = "ctrl/conv/error";

/// Constant 'CONTROL_INPUT_CONV'.
/**
  * Type: ControlInput
 */
static const char * const smarc_control_msgs__msg__Topics__CONTROL_INPUT_CONV = "ctrl/conv/control_input";

/// Constant 'WAYPOINT_CONV'.
/**
  * Type: PoseWithCovarianceStamped
 */
static const char * const smarc_control_msgs__msg__Topics__WAYPOINT_CONV = "ctrl/conv/waypoint";

/// Struct defined in msg/Topics in the package smarc_control_msgs.
/**
  * This is a file that defines all the topics for control.
  * The goal is to have one location that all cpp/py scripts
  * can easily access and thus avoid having 100 parameters for topics all
  * over the place, repeated for all subs/pubs...
  * It is assumed that the nodes will namespace as needed.
 */
typedef struct smarc_control_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} smarc_control_msgs__msg__Topics;

// Struct for a sequence of smarc_control_msgs__msg__Topics.
typedef struct smarc_control_msgs__msg__Topics__Sequence
{
  smarc_control_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_control_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
