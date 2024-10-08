// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'BATTERY_TOPIC'.
static const char * const smarc_msgs__msg__Topics__BATTERY_TOPIC = "core/battery";

/// Constant 'GPS_TOPIC'.
static const char * const smarc_msgs__msg__Topics__GPS_TOPIC = "core/gps";

/// Constant 'HEADING_TOPIC'.
static const char * const smarc_msgs__msg__Topics__HEADING_TOPIC = "core/heading";

/// Constant 'ABORT_TOPIC'.
static const char * const smarc_msgs__msg__Topics__ABORT_TOPIC = "core/abort";

/// Constant 'HEARTBEAT_TOPIC'.
static const char * const smarc_msgs__msg__Topics__HEARTBEAT_TOPIC = "core/heartbeat";

/// Constant 'VEHICLE_READY_TOPIC'.
static const char * const smarc_msgs__msg__Topics__VEHICLE_READY_TOPIC = "core/vehicle_ready";

/// Struct defined in msg/Topics in the package smarc_msgs.
typedef struct smarc_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} smarc_msgs__msg__Topics;

// Struct for a sequence of smarc_msgs__msg__Topics.
typedef struct smarc_msgs__msg__Topics__Sequence
{
  smarc_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
