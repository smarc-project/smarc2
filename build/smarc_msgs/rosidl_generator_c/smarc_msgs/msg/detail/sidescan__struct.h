// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_H_

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
// Member 'port_channel'
// Member 'starboard_channel'
// Member 'port_channel_angle_high'
// Member 'port_channel_angle_low'
// Member 'starboard_channel_angle_high'
// Member 'starboard_channel_angle_low'
// Member 'extra_channel'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/Sidescan in the package smarc_msgs.
typedef struct smarc_msgs__msg__Sidescan
{
  std_msgs__msg__Header header;
  /// Packet Type, 0xE2 = Sonar 8 Bit
  uint8_t type;
  /// Ping time
  uint32_t time;
  /// Freq Id, currently 0x00
  uint8_t frequency_id;
  int16_t gain;
  uint16_t decimation;
  /// Max travel time of outermost bins (s)
  float max_duration;
  rosidl_runtime_c__uint8__Sequence port_channel;
  rosidl_runtime_c__uint8__Sequence starboard_channel;
  rosidl_runtime_c__uint8__Sequence port_channel_angle_high;
  rosidl_runtime_c__uint8__Sequence port_channel_angle_low;
  rosidl_runtime_c__uint8__Sequence starboard_channel_angle_high;
  rosidl_runtime_c__uint8__Sequence starboard_channel_angle_low;
  rosidl_runtime_c__uint8__Sequence extra_channel;
} smarc_msgs__msg__Sidescan;

// Struct for a sequence of smarc_msgs__msg__Sidescan.
typedef struct smarc_msgs__msg__Sidescan__Sequence
{
  smarc_msgs__msg__Sidescan * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__Sidescan__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_H_
