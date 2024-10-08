// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/ControllerStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'CONTROL_STATUS_NOT_CONTROLLING'.
enum
{
  smarc_msgs__msg__ControllerStatus__CONTROL_STATUS_NOT_CONTROLLING = 0
};

/// Constant 'CONTROL_STATUS_CONTROLLING'.
enum
{
  smarc_msgs__msg__ControllerStatus__CONTROL_STATUS_CONTROLLING = 1
};

/// Constant 'CONTROL_STATUS_ERROR'.
enum
{
  smarc_msgs__msg__ControllerStatus__CONTROL_STATUS_ERROR = 2
};

// Include directives for member types
// Member 'service_name'
// Member 'diagnostics_message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/ControllerStatus in the package smarc_msgs.
typedef struct smarc_msgs__msg__ControllerStatus
{
  uint8_t control_status;
  /// name of service to turn on and off controller
  rosidl_runtime_c__String service_name;
  /// optional diagnostics message
  rosidl_runtime_c__String diagnostics_message;
} smarc_msgs__msg__ControllerStatus;

// Struct for a sequence of smarc_msgs__msg__ControllerStatus.
typedef struct smarc_msgs__msg__ControllerStatus__Sequence
{
  smarc_msgs__msg__ControllerStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__ControllerStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_H_
