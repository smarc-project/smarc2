// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/CircuitStatusStamped.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'circuit'
#include "sam_msgs/msg/detail/circuit_status__struct.h"

/// Struct defined in msg/CircuitStatusStamped in the package sam_msgs.
/**
  * Circuit status with timestamp
 */
typedef struct sam_msgs__msg__CircuitStatusStamped
{
  std_msgs__msg__Header header;
  /// Uavcan CircuitStatus
  sam_msgs__msg__CircuitStatus circuit;
} sam_msgs__msg__CircuitStatusStamped;

// Struct for a sequence of sam_msgs__msg__CircuitStatusStamped.
typedef struct sam_msgs__msg__CircuitStatusStamped__Sequence
{
  sam_msgs__msg__CircuitStatusStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__CircuitStatusStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_H_
