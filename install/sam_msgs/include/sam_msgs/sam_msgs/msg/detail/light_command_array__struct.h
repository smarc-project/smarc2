// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/LightCommandArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'array'
#include "sam_msgs/msg/detail/light_command__struct.h"

/// Struct defined in msg/LightCommandArray in the package sam_msgs.
/**
  * Light command
 */
typedef struct sam_msgs__msg__LightCommandArray
{
  sam_msgs__msg__LightCommand__Sequence array;
} sam_msgs__msg__LightCommandArray;

// Struct for a sequence of sam_msgs__msg__LightCommandArray.
typedef struct sam_msgs__msg__LightCommandArray__Sequence
{
  sam_msgs__msg__LightCommandArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__LightCommandArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__STRUCT_H_
