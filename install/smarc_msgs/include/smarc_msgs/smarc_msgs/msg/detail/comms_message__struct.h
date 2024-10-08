// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/CommsMessage.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__STRUCT_H_

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
// Member 'source_ns'
// Member 'target_ns'
// Member 'data'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/CommsMessage in the package smarc_msgs.
typedef struct smarc_msgs__msg__CommsMessage
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__String source_ns;
  rosidl_runtime_c__String target_ns;
  rosidl_runtime_c__String data;
} smarc_msgs__msg__CommsMessage;

// Struct for a sequence of smarc_msgs__msg__CommsMessage.
typedef struct smarc_msgs__msg__CommsMessage__Sequence
{
  smarc_msgs__msg__CommsMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__CommsMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__STRUCT_H_
