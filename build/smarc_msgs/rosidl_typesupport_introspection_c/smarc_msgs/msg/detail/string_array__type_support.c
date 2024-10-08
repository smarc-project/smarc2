// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:msg/StringArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/msg/detail/string_array__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/msg/detail/string_array__functions.h"
#include "smarc_msgs/msg/detail/string_array__struct.h"


// Include directives for member types
// Member `string_array`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__msg__StringArray__init(message_memory);
}

void smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_fini_function(void * message_memory)
{
  smarc_msgs__msg__StringArray__fini(message_memory);
}

size_t smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__size_function__StringArray__string_array(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_const_function__StringArray__string_array(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_function__StringArray__string_array(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__fetch_function__StringArray__string_array(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_const_function__StringArray__string_array(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__assign_function__StringArray__string_array(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_function__StringArray__string_array(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__resize_function__StringArray__string_array(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_member_array[1] = {
  {
    "string_array",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__StringArray, string_array),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__size_function__StringArray__string_array,  // size() function pointer
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_const_function__StringArray__string_array,  // get_const(index) function pointer
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__get_function__StringArray__string_array,  // get(index) function pointer
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__fetch_function__StringArray__string_array,  // fetch(index, &value) function pointer
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__assign_function__StringArray__string_array,  // assign(index, value) function pointer
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__resize_function__StringArray__string_array  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_members = {
  "smarc_msgs__msg",  // message namespace
  "StringArray",  // message name
  1,  // number of fields
  sizeof(smarc_msgs__msg__StringArray),
  smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_member_array,  // message members
  smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_type_support_handle = {
  0,
  &smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, StringArray)() {
  if (!smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__msg__StringArray__rosidl_typesupport_introspection_c__StringArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
