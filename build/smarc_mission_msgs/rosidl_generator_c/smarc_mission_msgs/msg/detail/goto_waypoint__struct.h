// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_H_
#define SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'Z_CONTROL_NONE'.
/**
  * Defines the type of z control used going there
 */
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__Z_CONTROL_NONE = 0
};

/// Constant 'Z_CONTROL_DEPTH'.
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__Z_CONTROL_DEPTH = 1
};

/// Constant 'Z_CONTROL_ALTITUDE'.
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__Z_CONTROL_ALTITUDE = 2
};

/// Constant 'SPEED_CONTROL_NONE'.
/**
  * Defines the type of speed control used going there
 */
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__SPEED_CONTROL_NONE = 0
};

/// Constant 'SPEED_CONTROL_RPM'.
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__SPEED_CONTROL_RPM = 1
};

/// Constant 'SPEED_CONTROL_SPEED'.
enum
{
  smarc_mission_msgs__msg__GotoWaypoint__SPEED_CONTROL_SPEED = 2
};

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"
// Member 'name'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/GotoWaypoint in the package smarc_mission_msgs.
/**
  * target pose in local UTM zone ENU coordinates
  * UTM zone used defined by global
  * /utm_zone and /utm_band ROS params
 */
typedef struct smarc_mission_msgs__msg__GotoWaypoint
{
  geometry_msgs__msg__PoseStamped pose;
  /// required proximity in meters to waypoint in
  /// order to consider the waypoint as reached
  double goal_tolerance;
  uint8_t z_control_mode;
  double travel_altitude;
  double travel_depth;
  uint8_t speed_control_mode;
  double travel_rpm;
  double travel_speed;
  double lat;
  double lon;
  double arrival_heading;
  bool use_heading;
  rosidl_runtime_c__String name;
} smarc_mission_msgs__msg__GotoWaypoint;

// Struct for a sequence of smarc_mission_msgs__msg__GotoWaypoint.
typedef struct smarc_mission_msgs__msg__GotoWaypoint__Sequence
{
  smarc_mission_msgs__msg__GotoWaypoint * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__msg__GotoWaypoint__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_H_
