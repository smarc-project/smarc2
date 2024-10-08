// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/msg/detail/execution_status__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/msg/detail/execution_status__functions.h"
#include "smarc_msgs/msg/detail/execution_status__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `execution_queue`
#include "smarc_msgs/msg/sm_task.h"
// Member `execution_queue`
#include "smarc_msgs/msg/detail/sm_task__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__msg__ExecutionStatus__init(message_memory);
}

void smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_fini_function(void * message_memory)
{
  smarc_msgs__msg__ExecutionStatus__fini(message_memory);
}

size_t smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__size_function__ExecutionStatus__execution_queue(
  const void * untyped_member)
{
  const smarc_msgs__msg__SMTask__Sequence * member =
    (const smarc_msgs__msg__SMTask__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_const_function__ExecutionStatus__execution_queue(
  const void * untyped_member, size_t index)
{
  const smarc_msgs__msg__SMTask__Sequence * member =
    (const smarc_msgs__msg__SMTask__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_function__ExecutionStatus__execution_queue(
  void * untyped_member, size_t index)
{
  smarc_msgs__msg__SMTask__Sequence * member =
    (smarc_msgs__msg__SMTask__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__fetch_function__ExecutionStatus__execution_queue(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const smarc_msgs__msg__SMTask * item =
    ((const smarc_msgs__msg__SMTask *)
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_const_function__ExecutionStatus__execution_queue(untyped_member, index));
  smarc_msgs__msg__SMTask * value =
    (smarc_msgs__msg__SMTask *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__assign_function__ExecutionStatus__execution_queue(
  void * untyped_member, size_t index, const void * untyped_value)
{
  smarc_msgs__msg__SMTask * item =
    ((smarc_msgs__msg__SMTask *)
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_function__ExecutionStatus__execution_queue(untyped_member, index));
  const smarc_msgs__msg__SMTask * value =
    (const smarc_msgs__msg__SMTask *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__resize_function__ExecutionStatus__execution_queue(
  void * untyped_member, size_t size)
{
  smarc_msgs__msg__SMTask__Sequence * member =
    (smarc_msgs__msg__SMTask__Sequence *)(untyped_member);
  smarc_msgs__msg__SMTask__Sequence__fini(member);
  return smarc_msgs__msg__SMTask__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_member_array[3] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__ExecutionStatus, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "currently_executing",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__ExecutionStatus, currently_executing),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "execution_queue",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__ExecutionStatus, execution_queue),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__size_function__ExecutionStatus__execution_queue,  // size() function pointer
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_const_function__ExecutionStatus__execution_queue,  // get_const(index) function pointer
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__get_function__ExecutionStatus__execution_queue,  // get(index) function pointer
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__fetch_function__ExecutionStatus__execution_queue,  // fetch(index, &value) function pointer
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__assign_function__ExecutionStatus__execution_queue,  // assign(index, value) function pointer
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__resize_function__ExecutionStatus__execution_queue  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_members = {
  "smarc_msgs__msg",  // message namespace
  "ExecutionStatus",  // message name
  3,  // number of fields
  sizeof(smarc_msgs__msg__ExecutionStatus),
  smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_member_array,  // message members
  smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_type_support_handle = {
  0,
  &smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, ExecutionStatus)() {
  smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, SMTask)();
  if (!smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__msg__ExecutionStatus__rosidl_typesupport_introspection_c__ExecutionStatus_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
