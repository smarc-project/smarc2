// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:action/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__STRUCT_H_
#define SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'waypoint'
#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Goal
{
  smarc_mission_msgs__msg__GotoWaypoint waypoint;
} smarc_mission_msgs__action__GotoWaypoint_Goal;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_Goal.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence;


// Constants defined in the message

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Result
{
  bool reached_waypoint;
} smarc_mission_msgs__action__GotoWaypoint_Result;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_Result.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Result__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'time_remaining'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'feedback_message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Feedback
{
  builtin_interfaces__msg__Time time_remaining;
  rosidl_runtime_c__String feedback_message;
  float distance_remaining;
} smarc_mission_msgs__action__GotoWaypoint_Feedback;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_Feedback.
typedef struct smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "smarc_mission_msgs/action/detail/goto_waypoint__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  smarc_mission_msgs__action__GotoWaypoint_Goal goal;
} smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request.
typedef struct smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
// already included above
// #include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response.
typedef struct smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} smarc_mission_msgs__action__GotoWaypoint_GetResult_Request;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_GetResult_Request.
typedef struct smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_GetResult_Response
{
  int8_t status;
  smarc_mission_msgs__action__GotoWaypoint_Result result;
} smarc_mission_msgs__action__GotoWaypoint_GetResult_Response;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_GetResult_Response.
typedef struct smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.h"

/// Struct defined in action/GotoWaypoint in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  smarc_mission_msgs__action__GotoWaypoint_Feedback feedback;
} smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage;

// Struct for a sequence of smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage.
typedef struct smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence
{
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__STRUCT_H_
