// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/StringStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'time_sent'
// Member 'time_received'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'data'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/StringStamped in the package smarc_msgs.
typedef struct smarc_msgs__msg__StringStamped
{
  builtin_interfaces__msg__Time time_sent;
  builtin_interfaces__msg__Time time_received;
  rosidl_runtime_c__String data;
} smarc_msgs__msg__StringStamped;

// Struct for a sequence of smarc_msgs__msg__StringStamped.
typedef struct smarc_msgs__msg__StringStamped__Sequence
{
  smarc_msgs__msg__StringStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__StringStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__STRUCT_H_
