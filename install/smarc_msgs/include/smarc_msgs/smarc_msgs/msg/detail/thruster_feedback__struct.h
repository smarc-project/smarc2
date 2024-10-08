// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/ThrusterFeedback.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_H_

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
// Member 'rpm'
#include "smarc_msgs/msg/detail/thruster_rpm__struct.h"
// Member 'dc'
#include "smarc_msgs/msg/detail/thruster_dc__struct.h"

/// Struct defined in msg/ThrusterFeedback in the package smarc_msgs.
typedef struct smarc_msgs__msg__ThrusterFeedback
{
  std_msgs__msg__Header header;
  smarc_msgs__msg__ThrusterRPM rpm;
  smarc_msgs__msg__ThrusterDC dc;
  float current;
  float torque;
} smarc_msgs__msg__ThrusterFeedback;

// Struct for a sequence of smarc_msgs__msg__ThrusterFeedback.
typedef struct smarc_msgs__msg__ThrusterFeedback__Sequence
{
  smarc_msgs__msg__ThrusterFeedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__ThrusterFeedback__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_H_
