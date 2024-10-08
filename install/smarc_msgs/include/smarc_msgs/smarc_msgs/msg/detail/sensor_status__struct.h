// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/SensorStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'SENSOR_STATUS_NOT_ACTIVE'.
enum
{
  smarc_msgs__msg__SensorStatus__SENSOR_STATUS_NOT_ACTIVE = 0
};

/// Constant 'SENSOR_STATUS_ACTIVE'.
enum
{
  smarc_msgs__msg__SensorStatus__SENSOR_STATUS_ACTIVE = 1
};

/// Constant 'SENSOR_STATUS_ERROR'.
enum
{
  smarc_msgs__msg__SensorStatus__SENSOR_STATUS_ERROR = 2
};

// Include directives for member types
// Member 'service_name'
// Member 'diagnostics_message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/SensorStatus in the package smarc_msgs.
typedef struct smarc_msgs__msg__SensorStatus
{
  uint8_t sensor_status;
  /// name of service to turn on and off the sensor
  rosidl_runtime_c__String service_name;
  /// optional diagnostics message
  rosidl_runtime_c__String diagnostics_message;
} smarc_msgs__msg__SensorStatus;

// Struct for a sequence of smarc_msgs__msg__SensorStatus.
typedef struct smarc_msgs__msg__SensorStatus__Sequence
{
  smarc_msgs__msg__SensorStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__SensorStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__STRUCT_H_
