// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/DualThrusterRPM.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'thruster_front'
// Member 'thruster_back'
#include "smarc_msgs/msg/detail/thruster_rpm__struct.h"

/// Struct defined in msg/DualThrusterRPM in the package smarc_msgs.
typedef struct smarc_msgs__msg__DualThrusterRPM
{
  smarc_msgs__msg__ThrusterRPM thruster_front;
  smarc_msgs__msg__ThrusterRPM thruster_back;
} smarc_msgs__msg__DualThrusterRPM;

// Struct for a sequence of smarc_msgs__msg__DualThrusterRPM.
typedef struct smarc_msgs__msg__DualThrusterRPM__Sequence
{
  smarc_msgs__msg__DualThrusterRPM * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__DualThrusterRPM__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__STRUCT_H_
