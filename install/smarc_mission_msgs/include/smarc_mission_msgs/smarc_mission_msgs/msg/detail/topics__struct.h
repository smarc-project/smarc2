// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define SMARC_MISSION_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'DUBINS_SERVICE'.
static const char * const smarc_mission_msgs__msg__Topics__DUBINS_SERVICE = "mission/dubins_service";

/// Constant 'UTM_LATLON_CONVERSION_SERVICE'.
static const char * const smarc_mission_msgs__msg__Topics__UTM_LATLON_CONVERSION_SERVICE = "mission/utm_latlon_conversion_service";

/// Constant 'MISSION_COMPLETE_TOPIC'.
static const char * const smarc_mission_msgs__msg__Topics__MISSION_COMPLETE_TOPIC = "mission/complete";

/// Constant 'MISSION_CONTROL_TOPIC'.
static const char * const smarc_mission_msgs__msg__Topics__MISSION_CONTROL_TOPIC = "mission/mission_control";

/// Constant 'BT_COMMAND_TOPIC'.
static const char * const smarc_mission_msgs__msg__Topics__BT_COMMAND_TOPIC = "mission/bt_command";

/// Constant 'BT_TIP_TOPIC'.
static const char * const smarc_mission_msgs__msg__Topics__BT_TIP_TOPIC = "mission/bt_tip";

/// Constant 'BT_LAST_WP_TOPIC'.
static const char * const smarc_mission_msgs__msg__Topics__BT_LAST_WP_TOPIC = "mission/last_wp";

/// Constant 'GOTO_WP_ACTION'.
static const char * const smarc_mission_msgs__msg__Topics__GOTO_WP_ACTION = "mission/goto_wp_action";

/// Struct defined in msg/Topics in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} smarc_mission_msgs__msg__Topics;

// Struct for a sequence of smarc_mission_msgs__msg__Topics.
typedef struct smarc_mission_msgs__msg__Topics__Sequence
{
  smarc_mission_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
