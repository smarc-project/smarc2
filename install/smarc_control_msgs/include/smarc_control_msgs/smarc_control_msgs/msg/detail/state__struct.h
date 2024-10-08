// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_control_msgs:msg/State.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__STRUCT_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/State in the package smarc_control_msgs.
typedef struct smarc_control_msgs__msg__State
{
  double x;
  double y;
  double z;
  double roll;
  double pitch;
  double yaw;
} smarc_control_msgs__msg__State;

// Struct for a sequence of smarc_control_msgs__msg__State.
typedef struct smarc_control_msgs__msg__State__Sequence
{
  smarc_control_msgs__msg__State * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_control_msgs__msg__State__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__STRUCT_H_
