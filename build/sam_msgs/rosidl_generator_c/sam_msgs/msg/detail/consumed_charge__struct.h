// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/ConsumedCharge.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_H_

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

/// Struct defined in msg/ConsumedCharge in the package sam_msgs.
/**
  * Consumed charge message
 */
typedef struct sam_msgs__msg__ConsumedCharge
{
  std_msgs__msg__Header header;
  /// circuit id
  uint16_t circuit_id;
  /// Consumed charge mAh
  float charge;
} sam_msgs__msg__ConsumedCharge;

// Struct for a sequence of sam_msgs__msg__ConsumedCharge.
typedef struct sam_msgs__msg__ConsumedCharge__Sequence
{
  sam_msgs__msg__ConsumedCharge * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__ConsumedCharge__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_H_
