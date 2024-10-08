// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:msg/BTCommand.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_H_
#define SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'TYPE_CMD'.
enum
{
  smarc_mission_msgs__msg__BTCommand__TYPE_CMD = 0
};

/// Constant 'TYPE_FB'.
enum
{
  smarc_mission_msgs__msg__BTCommand__TYPE_FB = 1
};

// Include directives for member types
// Member 'cmd_json'
// Member 'fb_json'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/BTCommand in the package smarc_mission_msgs.
/**
  * For now, we want max flexibility, so I'm just gonna
  * make nodered and BT talk in JSON
  * Still useful to split the CMD/FEEDBACK types clearly tho
 */
typedef struct smarc_mission_msgs__msg__BTCommand
{
  uint8_t msg_type;
  /// also might be nice to have both a cmd and a feedback
  /// in the same message
  rosidl_runtime_c__String cmd_json;
  rosidl_runtime_c__String fb_json;
} smarc_mission_msgs__msg__BTCommand;

// Struct for a sequence of smarc_mission_msgs__msg__BTCommand.
typedef struct smarc_mission_msgs__msg__BTCommand__Sequence
{
  smarc_mission_msgs__msg__BTCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__msg__BTCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_H_
