// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:srv/NEDENURotation.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__STRUCT_H_
#define SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'orientation'
#include "geometry_msgs/msg/detail/quaternion__struct.h"

/// Struct defined in srv/NEDENURotation in the package smarc_msgs.
typedef struct smarc_msgs__srv__NEDENURotation_Request
{
  geometry_msgs__msg__Quaternion orientation;
} smarc_msgs__srv__NEDENURotation_Request;

// Struct for a sequence of smarc_msgs__srv__NEDENURotation_Request.
typedef struct smarc_msgs__srv__NEDENURotation_Request__Sequence
{
  smarc_msgs__srv__NEDENURotation_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__NEDENURotation_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'orientation'
// already included above
// #include "geometry_msgs/msg/detail/quaternion__struct.h"

/// Struct defined in srv/NEDENURotation in the package smarc_msgs.
typedef struct smarc_msgs__srv__NEDENURotation_Response
{
  geometry_msgs__msg__Quaternion orientation;
} smarc_msgs__srv__NEDENURotation_Response;

// Struct for a sequence of smarc_msgs__srv__NEDENURotation_Response.
typedef struct smarc_msgs__srv__NEDENURotation_Response__Sequence
{
  smarc_msgs__srv__NEDENURotation_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__NEDENURotation_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__STRUCT_H_
