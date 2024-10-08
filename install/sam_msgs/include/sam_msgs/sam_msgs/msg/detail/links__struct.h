// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/Links.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'BASE_LINK'.
static const char * const sam_msgs__msg__Links__BASE_LINK = "base_link";

/// Constant 'BASE_LINK_2D'.
static const char * const sam_msgs__msg__Links__BASE_LINK_2D = "base_link_2d";

/// Constant 'PRESS_LINK'.
static const char * const sam_msgs__msg__Links__PRESS_LINK = "pressure_link";

/// Constant 'GPS_LINK'.
static const char * const sam_msgs__msg__Links__GPS_LINK = "gps_link";

/// Constant 'DVL_LINK'.
static const char * const sam_msgs__msg__Links__DVL_LINK = "dvl_link";

/// Constant 'ODOM_LINK'.
static const char * const sam_msgs__msg__Links__ODOM_LINK = "odom";

/// Struct defined in msg/Links in the package sam_msgs.
/**
  * SAM links
 */
typedef struct sam_msgs__msg__Links
{
  uint8_t structure_needs_at_least_one_member;
} sam_msgs__msg__Links;

// Struct for a sequence of sam_msgs__msg__Links.
typedef struct sam_msgs__msg__Links__Sequence
{
  sam_msgs__msg__Links * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__Links__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_H_
