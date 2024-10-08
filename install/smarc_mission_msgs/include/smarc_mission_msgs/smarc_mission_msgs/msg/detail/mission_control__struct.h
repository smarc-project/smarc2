// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_H_
#define SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'CMD_START'.
/**
  * start or stop the current plan
  * stop will stop and delete the plan
  * pause will stop the execution, but not delete it
  * start either starts a new plan or continues a paused one
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_START = 0
};

/// Constant 'CMD_STOP'.
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_STOP = 1
};

/// Constant 'CMD_PAUSE'.
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_PAUSE = 2
};

/// Constant 'CMD_EMERGENCY'.
/**
  * one-way stop button. no plan should be started
  * after this is received
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_EMERGENCY = 3
};

/// Constant 'CMD_SET_PLAN'.
/**
  * re-set the plan with the given waypoints
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_SET_PLAN = 4
};

/// Constant 'CMD_IS_FEEDBACK'.
/**
  * to indicate that this is just feedback
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_IS_FEEDBACK = 5
};

/// Constant 'CMD_REQUEST_FEEDBACK'.
/**
  * to specifically request a feedback message
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__CMD_REQUEST_FEEDBACK = 6
};

/// Constant 'FB_RUNNING'.
/**
  * corresponding to each command
 */
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_RUNNING = 0
};

/// Constant 'FB_STOPPED'.
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_STOPPED = 1
};

/// Constant 'FB_PAUSED'.
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_PAUSED = 2
};

/// Constant 'FB_EMERGENCY'.
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_EMERGENCY = 3
};

/// Constant 'FB_RECEIVED'.
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_RECEIVED = 4
};

/// Constant 'FB_COMPLETED'.
enum
{
  smarc_mission_msgs__msg__MissionControl__FB_COMPLETED = 5
};

// Include directives for member types
// Member 'name'
// Member 'hash'
// Member 'feedback_str'
#include "rosidl_runtime_c/string.h"
// Member 'waypoints'
#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.h"

/// Struct defined in msg/MissionControl in the package smarc_mission_msgs.
/**
  * name of the plan
 */
typedef struct smarc_mission_msgs__msg__MissionControl
{
  rosidl_runtime_c__String name;
  /// a hash derived frm this entire message. optional.
  rosidl_runtime_c__String hash;
  /// a timeout in seconds, in which the vehicle should stop
  /// doing what this mission control message wants it to do
  /// after trying for this many seconds
  uint64_t timeout;
  uint8_t command;
  uint8_t plan_state;
  /// and some extra string, because why not
  rosidl_runtime_c__String feedback_str;
  /// if the cmd is set plan, then this should contain the waypoints
  /// to follow, otherwise ignored
  smarc_mission_msgs__msg__GotoWaypoint__Sequence waypoints;
} smarc_mission_msgs__msg__MissionControl;

// Struct for a sequence of smarc_mission_msgs__msg__MissionControl.
typedef struct smarc_mission_msgs__msg__MissionControl__Sequence
{
  smarc_mission_msgs__msg__MissionControl * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__msg__MissionControl__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_H_
