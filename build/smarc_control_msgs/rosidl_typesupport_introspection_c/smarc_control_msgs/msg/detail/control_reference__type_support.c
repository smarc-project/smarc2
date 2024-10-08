// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_control_msgs:msg/ControlReference.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_control_msgs/msg/detail/control_reference__rosidl_typesupport_introspection_c.h"
#include "smarc_control_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_control_msgs/msg/detail/control_reference__functions.h"
#include "smarc_control_msgs/msg/detail/control_reference__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_control_msgs__msg__ControlReference__init(message_memory);
}

void smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_fini_function(void * message_memory)
{
  smarc_control_msgs__msg__ControlReference__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_member_array[6] = {
  {
    "x",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, x),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "y",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, y),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "z",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, z),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "roll",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, roll),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pitch",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, pitch),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "yaw",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlReference, yaw),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_members = {
  "smarc_control_msgs__msg",  // message namespace
  "ControlReference",  // message name
  6,  // number of fields
  sizeof(smarc_control_msgs__msg__ControlReference),
  smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_member_array,  // message members
  smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_type_support_handle = {
  0,
  &smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_control_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_control_msgs, msg, ControlReference)() {
  if (!smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_type_support_handle.typesupport_identifier) {
    smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_control_msgs__msg__ControlReference__rosidl_typesupport_introspection_c__ControlReference_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
