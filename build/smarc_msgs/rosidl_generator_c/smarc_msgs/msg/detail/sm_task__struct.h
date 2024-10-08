// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/SMTask.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'max_duration'
#include "builtin_interfaces/msg/detail/duration__struct.h"
// Member 'action_topic'
// Member 'action_arguments'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/SMTask in the package smarc_msgs.
/**
  * This holds the id of the task
 */
typedef struct smarc_msgs__msg__SMTask
{
  uint64_t task_id;
  /// Termination condition WP: X. Set to zero if not used
  double x;
  /// Termination condition WP: Y. Set to zero if not used
  double y;
  /// Termination condition WP: depth. Set to zero if not used
  double depth;
  /// Termination condition WP: altitude. Set to zero if not used
  double altitude;
  /// Termination condition WP: Yaw. Set to zero if not used
  double theta;
  /// Termination condition: maximum duration of the task. Set to zero if not used
  builtin_interfaces__msg__Duration max_duration;
  /// Action server topic
  rosidl_runtime_c__String action_topic;
  /// Additional arguments to the action server call
  rosidl_runtime_c__String action_arguments;
} smarc_msgs__msg__SMTask;

// Struct for a sequence of smarc_msgs__msg__SMTask.
typedef struct smarc_msgs__msg__SMTask__Sequence
{
  smarc_msgs__msg__SMTask * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__SMTask__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_H_
