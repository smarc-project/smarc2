// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_control_msgs:msg/ControlError.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ControlError in the package smarc_control_msgs.
typedef struct smarc_control_msgs__msg__ControlError
{
  double x;
  double y;
  double z;
  double roll;
  double pitch;
  double yaw;
  double heading;
  double distance;
} smarc_control_msgs__msg__ControlError;

// Struct for a sequence of smarc_control_msgs__msg__ControlError.
typedef struct smarc_control_msgs__msg__ControlError__Sequence
{
  smarc_control_msgs__msg__ControlError * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_control_msgs__msg__ControlError__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_H_
