// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "sam_msgs/msg/detail/uavcan_node_status__rosidl_typesupport_introspection_c.h"
#include "sam_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "sam_msgs/msg/detail/uavcan_node_status__functions.h"
#include "sam_msgs/msg/detail/uavcan_node_status__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  sam_msgs__msg__UavcanNodeStatus__init(message_memory);
}

void sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_fini_function(void * message_memory)
{
  sam_msgs__msg__UavcanNodeStatus__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_member_array[5] = {
  {
    "uptime_sec",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__UavcanNodeStatus, uptime_sec),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "health",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__UavcanNodeStatus, health),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mode",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__UavcanNodeStatus, mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "sub_mode",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__UavcanNodeStatus, sub_mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "vendor_specific_status_code",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__UavcanNodeStatus, vendor_specific_status_code),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_members = {
  "sam_msgs__msg",  // message namespace
  "UavcanNodeStatus",  // message name
  5,  // number of fields
  sizeof(sam_msgs__msg__UavcanNodeStatus),
  sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_member_array,  // message members
  sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_init_function,  // function to initialize message memory (memory has to be allocated)
  sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_type_support_handle = {
  0,
  &sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_sam_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sam_msgs, msg, UavcanNodeStatus)() {
  if (!sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_type_support_handle.typesupport_identifier) {
    sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &sam_msgs__msg__UavcanNodeStatus__rosidl_typesupport_introspection_c__UavcanNodeStatus_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
