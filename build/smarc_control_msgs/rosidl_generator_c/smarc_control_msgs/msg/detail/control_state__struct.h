// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_control_msgs:msg/ControlState.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
// Member 'vel'
#include "smarc_control_msgs/msg/detail/state__struct.h"

/// Struct defined in msg/ControlState in the package smarc_control_msgs.
typedef struct smarc_control_msgs__msg__ControlState
{
  smarc_control_msgs__msg__State pose;
  smarc_control_msgs__msg__State vel;
} smarc_control_msgs__msg__ControlState;

// Struct for a sequence of smarc_control_msgs__msg__ControlState.
typedef struct smarc_control_msgs__msg__ControlState__Sequence
{
  smarc_control_msgs__msg__ControlState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_control_msgs__msg__ControlState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_H_
