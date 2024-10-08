// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_control_msgs:msg/ControlInput.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_control_msgs/msg/detail/control_input__rosidl_typesupport_introspection_c.h"
#include "smarc_control_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_control_msgs/msg/detail/control_input__functions.h"
#include "smarc_control_msgs/msg/detail/control_input__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_control_msgs__msg__ControlInput__init(message_memory);
}

void smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_fini_function(void * message_memory)
{
  smarc_control_msgs__msg__ControlInput__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_member_array[5] = {
  {
    "thrusterrpm",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlInput, thrusterrpm),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "thrustervertical",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlInput, thrustervertical),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "thrusterhorizontal",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlInput, thrusterhorizontal),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "vbs",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlInput, vbs),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "lcg",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_control_msgs__msg__ControlInput, lcg),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_members = {
  "smarc_control_msgs__msg",  // message namespace
  "ControlInput",  // message name
  5,  // number of fields
  sizeof(smarc_control_msgs__msg__ControlInput),
  smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_member_array,  // message members
  smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_type_support_handle = {
  0,
  &smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_control_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_control_msgs, msg, ControlInput)() {
  if (!smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_type_support_handle.typesupport_identifier) {
    smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_control_msgs__msg__ControlInput__rosidl_typesupport_introspection_c__ControlInput_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
