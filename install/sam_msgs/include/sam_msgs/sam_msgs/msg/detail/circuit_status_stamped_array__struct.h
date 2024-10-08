// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/CircuitStatusStampedArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'array'
#include "sam_msgs/msg/detail/circuit_status_stamped__struct.h"

/// Struct defined in msg/CircuitStatusStampedArray in the package sam_msgs.
/**
  * Uavcan CircuitStatus
 */
typedef struct sam_msgs__msg__CircuitStatusStampedArray
{
  sam_msgs__msg__CircuitStatusStamped__Sequence array;
} sam_msgs__msg__CircuitStatusStampedArray;

// Struct for a sequence of sam_msgs__msg__CircuitStatusStampedArray.
typedef struct sam_msgs__msg__CircuitStatusStampedArray__Sequence
{
  sam_msgs__msg__CircuitStatusStampedArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__CircuitStatusStampedArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_H_
