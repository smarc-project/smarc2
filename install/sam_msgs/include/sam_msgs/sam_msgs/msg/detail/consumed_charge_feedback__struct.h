// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_H_

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

/// Struct defined in msg/ConsumedChargeFeedback in the package sam_msgs.
/**
  * Consumed charge for all power rails
 */
typedef struct sam_msgs__msg__ConsumedChargeFeedback
{
  std_msgs__msg__Header header;
  /// Consumed charge mAh
  float main;
  float esc1;
  float esc2;
  float esc3;
  float v20;
  float v12;
  float v7;
  float v5;
  float v33;
} sam_msgs__msg__ConsumedChargeFeedback;

// Struct for a sequence of sam_msgs__msg__ConsumedChargeFeedback.
typedef struct sam_msgs__msg__ConsumedChargeFeedback__Sequence
{
  sam_msgs__msg__ConsumedChargeFeedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__ConsumedChargeFeedback__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_H_
