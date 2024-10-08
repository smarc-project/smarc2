// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/StringArray.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'string_array'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/StringArray in the package smarc_msgs.
typedef struct smarc_msgs__msg__StringArray
{
  rosidl_runtime_c__String__Sequence string_array;
} smarc_msgs__msg__StringArray;

// Struct for a sequence of smarc_msgs__msg__StringArray.
typedef struct smarc_msgs__msg__StringArray__Sequence
{
  smarc_msgs__msg__StringArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__StringArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__STRUCT_H_
