// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_control_msgs:msg/ControlReference.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__STRUCT_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ControlReference in the package smarc_control_msgs.
typedef struct smarc_control_msgs__msg__ControlReference
{
  double x;
  double y;
  double z;
  double roll;
  double pitch;
  double yaw;
} smarc_control_msgs__msg__ControlReference;

// Struct for a sequence of smarc_control_msgs__msg__ControlReference.
typedef struct smarc_control_msgs__msg__ControlReference__Sequence
{
  smarc_control_msgs__msg__ControlReference * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_control_msgs__msg__ControlReference__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__STRUCT_H_
