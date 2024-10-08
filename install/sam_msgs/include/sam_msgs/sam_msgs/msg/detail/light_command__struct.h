// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/LightCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'command'
#include "std_msgs/msg/detail/color_rgba__struct.h"

/// Struct defined in msg/LightCommand in the package sam_msgs.
/**
  * Light command
 */
typedef struct sam_msgs__msg__LightCommand
{
  uint16_t id;
  std_msgs__msg__ColorRGBA command;
} sam_msgs__msg__LightCommand;

// Struct for a sequence of sam_msgs__msg__LightCommand.
typedef struct sam_msgs__msg__LightCommand__Sequence
{
  sam_msgs__msg__LightCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__LightCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_H_
