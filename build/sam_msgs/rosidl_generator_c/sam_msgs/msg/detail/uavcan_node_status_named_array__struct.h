// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/UavcanNodeStatusNamedArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__STRUCT_H_

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
#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.h"

/// Struct defined in msg/UavcanNodeStatusNamedArray in the package sam_msgs.
typedef struct sam_msgs__msg__UavcanNodeStatusNamedArray
{
  sam_msgs__msg__UavcanNodeStatusNamed__Sequence array;
} sam_msgs__msg__UavcanNodeStatusNamedArray;

// Struct for a sequence of sam_msgs__msg__UavcanNodeStatusNamedArray.
typedef struct sam_msgs__msg__UavcanNodeStatusNamedArray__Sequence
{
  sam_msgs__msg__UavcanNodeStatusNamedArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__UavcanNodeStatusNamedArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__STRUCT_H_
