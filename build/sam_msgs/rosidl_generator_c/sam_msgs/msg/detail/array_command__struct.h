// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/ArrayCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'commands'
#include "sam_msgs/msg/detail/command__struct.h"

/// Struct defined in msg/ArrayCommand in the package sam_msgs.
/**
  * Actuator commands.
  * The system supports up to 256 actuators; up to 15 of them can be commanded with one message.
 */
typedef struct sam_msgs__msg__ArrayCommand
{
  sam_msgs__msg__Command__Sequence commands;
} sam_msgs__msg__ArrayCommand;

// Struct for a sequence of sam_msgs__msg__ArrayCommand.
typedef struct sam_msgs__msg__ArrayCommand__Sequence
{
  sam_msgs__msg__ArrayCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__ArrayCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_H_
