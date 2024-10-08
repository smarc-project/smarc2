// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_H_
#define SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'waypoints'
#include "geometry_msgs/msg/detail/pose2_d__struct.h"

/// Struct defined in srv/DubinsPlan in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__srv__DubinsPlan_Request
{
  geometry_msgs__msg__Pose2D__Sequence waypoints;
  double step;
  double turning_radius;
} smarc_mission_msgs__srv__DubinsPlan_Request;

// Struct for a sequence of smarc_mission_msgs__srv__DubinsPlan_Request.
typedef struct smarc_mission_msgs__srv__DubinsPlan_Request__Sequence
{
  smarc_mission_msgs__srv__DubinsPlan_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__srv__DubinsPlan_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'waypoints'
// already included above
// #include "geometry_msgs/msg/detail/pose2_d__struct.h"
// Member 'original_wp_indices'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in srv/DubinsPlan in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__srv__DubinsPlan_Response
{
  geometry_msgs__msg__Pose2D__Sequence waypoints;
  rosidl_runtime_c__uint16__Sequence original_wp_indices;
} smarc_mission_msgs__srv__DubinsPlan_Response;

// Struct for a sequence of smarc_mission_msgs__srv__DubinsPlan_Response.
typedef struct smarc_mission_msgs__srv__DubinsPlan_Response__Sequence
{
  smarc_mission_msgs__srv__DubinsPlan_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__srv__DubinsPlan_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_H_
