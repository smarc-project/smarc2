// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/BallastAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/BallastAngles in the package sam_msgs.
typedef struct sam_msgs__msg__BallastAngles
{
  float weight_1_offset_radians;
  float weight_2_offset_radians;
  std_msgs__msg__Header header;
} sam_msgs__msg__BallastAngles;

// Struct for a sequence of sam_msgs__msg__BallastAngles.
typedef struct sam_msgs__msg__BallastAngles__Sequence
{
  sam_msgs__msg__BallastAngles * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__BallastAngles__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_H_
