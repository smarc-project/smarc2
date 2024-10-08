// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/Leak.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Leak in the package sam_msgs.
typedef struct sam_msgs__msg__Leak
{
  bool value;
  int32_t leak_counter;
} sam_msgs__msg__Leak;

// Struct for a sequence of sam_msgs__msg__Leak.
typedef struct sam_msgs__msg__Leak__Sequence
{
  sam_msgs__msg__Leak * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__Leak__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_H_
