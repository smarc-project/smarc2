// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/ThrusterDC.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ThrusterDC in the package smarc_msgs.
typedef struct smarc_msgs__msg__ThrusterDC
{
  /// NOTE: [-1.,1]
  float dc;
} smarc_msgs__msg__ThrusterDC;

// Struct for a sequence of smarc_msgs__msg__ThrusterDC.
typedef struct smarc_msgs__msg__ThrusterDC__Sequence
{
  smarc_msgs__msg__ThrusterDC * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__ThrusterDC__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_H_
