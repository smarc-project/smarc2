// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/CTD.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__CTD__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__CTD__STRUCT_H_

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

/// Struct defined in msg/CTD in the package smarc_msgs.
typedef struct smarc_msgs__msg__CTD
{
  std_msgs__msg__Header header;
  double conductivity;
  double temperature;
  double depth;
} smarc_msgs__msg__CTD;

// Struct for a sequence of smarc_msgs__msg__CTD.
typedef struct smarc_msgs__msg__CTD__Sequence
{
  smarc_msgs__msg__CTD * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__CTD__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__CTD__STRUCT_H_
