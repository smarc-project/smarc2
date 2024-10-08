// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/msg/detail/sidescan__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/msg/detail/sidescan__functions.h"
#include "smarc_msgs/msg/detail/sidescan__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `port_channel`
// Member `starboard_channel`
// Member `port_channel_angle_high`
// Member `port_channel_angle_low`
// Member `starboard_channel_angle_high`
// Member `starboard_channel_angle_low`
// Member `extra_channel`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__msg__Sidescan__init(message_memory);
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_fini_function(void * message_memory)
{
  smarc_msgs__msg__Sidescan__fini(message_memory);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel_angle_high(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_high(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_high(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel_angle_high(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_high(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel_angle_high(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_high(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel_angle_high(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel_angle_low(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_low(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_low(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel_angle_low(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_low(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel_angle_low(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_low(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel_angle_low(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel_angle_high(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_high(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_high(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel_angle_high(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_high(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel_angle_high(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_high(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel_angle_high(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel_angle_low(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_low(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_low(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel_angle_low(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_low(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel_angle_low(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_low(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel_angle_low(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

size_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__extra_channel(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__extra_channel(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint8__Sequence * member =
    (const rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__extra_channel(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__extra_channel(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint8_t * item =
    ((const uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__extra_channel(untyped_member, index));
  uint8_t * value =
    (uint8_t *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__extra_channel(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint8_t * item =
    ((uint8_t *)
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__extra_channel(untyped_member, index));
  const uint8_t * value =
    (const uint8_t *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__extra_channel(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint8__Sequence * member =
    (rosidl_runtime_c__uint8__Sequence *)(untyped_member);
  rosidl_runtime_c__uint8__Sequence__fini(member);
  return rosidl_runtime_c__uint8__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_member_array[14] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "type",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, type),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "frequency_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, frequency_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "gain",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, gain),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "decimation",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, decimation),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "max_duration",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, max_duration),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "port_channel",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, port_channel),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel  // resize(index) function pointer
  },
  {
    "starboard_channel",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, starboard_channel),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel  // resize(index) function pointer
  },
  {
    "port_channel_angle_high",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, port_channel_angle_high),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel_angle_high,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_high,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_high,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel_angle_high,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel_angle_high,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel_angle_high  // resize(index) function pointer
  },
  {
    "port_channel_angle_low",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, port_channel_angle_low),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__port_channel_angle_low,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__port_channel_angle_low,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__port_channel_angle_low,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__port_channel_angle_low,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__port_channel_angle_low,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__port_channel_angle_low  // resize(index) function pointer
  },
  {
    "starboard_channel_angle_high",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, starboard_channel_angle_high),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel_angle_high,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_high,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_high,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel_angle_high,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel_angle_high,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel_angle_high  // resize(index) function pointer
  },
  {
    "starboard_channel_angle_low",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, starboard_channel_angle_low),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__starboard_channel_angle_low,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__starboard_channel_angle_low,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__starboard_channel_angle_low,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__starboard_channel_angle_low,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__starboard_channel_angle_low,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__starboard_channel_angle_low  // resize(index) function pointer
  },
  {
    "extra_channel",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__Sidescan, extra_channel),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__size_function__Sidescan__extra_channel,  // size() function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_const_function__Sidescan__extra_channel,  // get_const(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__get_function__Sidescan__extra_channel,  // get(index) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__fetch_function__Sidescan__extra_channel,  // fetch(index, &value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__assign_function__Sidescan__extra_channel,  // assign(index, value) function pointer
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__resize_function__Sidescan__extra_channel  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_members = {
  "smarc_msgs__msg",  // message namespace
  "Sidescan",  // message name
  14,  // number of fields
  sizeof(smarc_msgs__msg__Sidescan),
  smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_member_array,  // message members
  smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_type_support_handle = {
  0,
  &smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, Sidescan)() {
  smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__msg__Sidescan__rosidl_typesupport_introspection_c__Sidescan_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
