// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/ThrusterRPM.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ThrusterRPM in the package smarc_msgs.
typedef struct smarc_msgs__msg__ThrusterRPM
{
  /// NOTE: can be negative also
  int32_t rpm;
} smarc_msgs__msg__ThrusterRPM;

// Struct for a sequence of smarc_msgs__msg__ThrusterRPM.
typedef struct smarc_msgs__msg__ThrusterRPM__Sequence
{
  smarc_msgs__msg__ThrusterRPM * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__ThrusterRPM__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_H_
