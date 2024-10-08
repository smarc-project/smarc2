// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/StringPair.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_PAIR__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__STRING_PAIR__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'first'
// Member 'second'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/StringPair in the package smarc_msgs.
typedef struct smarc_msgs__msg__StringPair
{
  rosidl_runtime_c__String first;
  rosidl_runtime_c__String second;
} smarc_msgs__msg__StringPair;

// Struct for a sequence of smarc_msgs__msg__StringPair.
typedef struct smarc_msgs__msg__StringPair__Sequence
{
  smarc_msgs__msg__StringPair * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__StringPair__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_PAIR__STRUCT_H_
