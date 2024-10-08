// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/Leak.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LEAK__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__LEAK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Leak in the package smarc_msgs.
typedef struct smarc_msgs__msg__Leak
{
  bool value;
  int32_t leak_counter;
} smarc_msgs__msg__Leak;

// Struct for a sequence of smarc_msgs__msg__Leak.
typedef struct smarc_msgs__msg__Leak__Sequence
{
  smarc_msgs__msg__Leak * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__Leak__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__LEAK__STRUCT_H_
