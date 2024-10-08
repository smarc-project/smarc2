// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/ConsumedChargeArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__STRUCT_H_

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
// Member 'array'
#include "sam_msgs/msg/detail/consumed_charge__struct.h"

/// Struct defined in msg/ConsumedChargeArray in the package sam_msgs.
/**
  * Consumed charge array
 */
typedef struct sam_msgs__msg__ConsumedChargeArray
{
  std_msgs__msg__Header header;
  /// Consumed charge mAh
  sam_msgs__msg__ConsumedCharge__Sequence array;
} sam_msgs__msg__ConsumedChargeArray;

// Struct for a sequence of sam_msgs__msg__ConsumedChargeArray.
typedef struct sam_msgs__msg__ConsumedChargeArray__Sequence
{
  sam_msgs__msg__ConsumedChargeArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__ConsumedChargeArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__STRUCT_H_
