// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'name'
#include "rosidl_runtime_c/string.h"
// Member 'ns'
#include "sam_msgs/msg/detail/uavcan_node_status__struct.h"

/// Struct defined in msg/UavcanNodeStatusNamed in the package sam_msgs.
/**
  * Node ID
 */
typedef struct sam_msgs__msg__UavcanNodeStatusNamed
{
  uint8_t id;
  /// Node name
  rosidl_runtime_c__String name;
  /// NodeStatus
  sam_msgs__msg__UavcanNodeStatus ns;
} sam_msgs__msg__UavcanNodeStatusNamed;

// Struct for a sequence of sam_msgs__msg__UavcanNodeStatusNamed.
typedef struct sam_msgs__msg__UavcanNodeStatusNamed__Sequence
{
  sam_msgs__msg__UavcanNodeStatusNamed * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__UavcanNodeStatusNamed__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_H_
