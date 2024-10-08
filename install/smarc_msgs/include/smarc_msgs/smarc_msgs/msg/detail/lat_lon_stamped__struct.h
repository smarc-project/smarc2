// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/LatLonStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__STRUCT_H_

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

/// Struct defined in msg/LatLonStamped in the package smarc_msgs.
typedef struct smarc_msgs__msg__LatLonStamped
{
  std_msgs__msg__Header header;
  double latitude;
  double longitude;
} smarc_msgs__msg__LatLonStamped;

// Struct for a sequence of smarc_msgs__msg__LatLonStamped.
typedef struct smarc_msgs__msg__LatLonStamped__Sequence
{
  smarc_msgs__msg__LatLonStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__LatLonStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__STRUCT_H_
