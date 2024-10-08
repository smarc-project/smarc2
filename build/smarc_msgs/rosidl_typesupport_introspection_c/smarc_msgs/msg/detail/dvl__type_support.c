// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:msg/DVL.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/msg/detail/dvl__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/msg/detail/dvl__functions.h"
#include "smarc_msgs/msg/detail/dvl__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `velocity`
#include "geometry_msgs/msg/vector3.h"
// Member `velocity`
#include "geometry_msgs/msg/detail/vector3__rosidl_typesupport_introspection_c.h"
// Member `beams`
#include "smarc_msgs/msg/dvl_beam.h"
// Member `beams`
#include "smarc_msgs/msg/detail/dvl_beam__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__msg__DVL__init(message_memory);
}

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_fini_function(void * message_memory)
{
  smarc_msgs__msg__DVL__fini(message_memory);
}

size_t smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__size_function__DVL__velocity_covariance(
  const void * untyped_member)
{
  (void)untyped_member;
  return 9;
}

const void * smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__velocity_covariance(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__velocity_covariance(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__fetch_function__DVL__velocity_covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__velocity_covariance(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__assign_function__DVL__velocity_covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__velocity_covariance(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

size_t smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__size_function__DVL__beams(
  const void * untyped_member)
{
  const smarc_msgs__msg__DVLBeam__Sequence * member =
    (const smarc_msgs__msg__DVLBeam__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__beams(
  const void * untyped_member, size_t index)
{
  const smarc_msgs__msg__DVLBeam__Sequence * member =
    (const smarc_msgs__msg__DVLBeam__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__beams(
  void * untyped_member, size_t index)
{
  smarc_msgs__msg__DVLBeam__Sequence * member =
    (smarc_msgs__msg__DVLBeam__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__fetch_function__DVL__beams(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const smarc_msgs__msg__DVLBeam * item =
    ((const smarc_msgs__msg__DVLBeam *)
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__beams(untyped_member, index));
  smarc_msgs__msg__DVLBeam * value =
    (smarc_msgs__msg__DVLBeam *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__assign_function__DVL__beams(
  void * untyped_member, size_t index, const void * untyped_value)
{
  smarc_msgs__msg__DVLBeam * item =
    ((smarc_msgs__msg__DVLBeam *)
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__beams(untyped_member, index));
  const smarc_msgs__msg__DVLBeam * value =
    (const smarc_msgs__msg__DVLBeam *)(untyped_value);
  *item = *value;
}

bool smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__resize_function__DVL__beams(
  void * untyped_member, size_t size)
{
  smarc_msgs__msg__DVLBeam__Sequence * member =
    (smarc_msgs__msg__DVLBeam__Sequence *)(untyped_member);
  smarc_msgs__msg__DVLBeam__Sequence__fini(member);
  return smarc_msgs__msg__DVLBeam__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_member_array[5] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__DVL, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "velocity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__DVL, velocity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "velocity_covariance",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    9,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__DVL, velocity_covariance),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__size_function__DVL__velocity_covariance,  // size() function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__velocity_covariance,  // get_const(index) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__velocity_covariance,  // get(index) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__fetch_function__DVL__velocity_covariance,  // fetch(index, &value) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__assign_function__DVL__velocity_covariance,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "altitude",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__DVL, altitude),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "beams",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__DVL, beams),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__size_function__DVL__beams,  // size() function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_const_function__DVL__beams,  // get_const(index) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__get_function__DVL__beams,  // get(index) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__fetch_function__DVL__beams,  // fetch(index, &value) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__assign_function__DVL__beams,  // assign(index, value) function pointer
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__resize_function__DVL__beams  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_members = {
  "smarc_msgs__msg",  // message namespace
  "DVL",  // message name
  5,  // number of fields
  sizeof(smarc_msgs__msg__DVL),
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_member_array,  // message members
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_type_support_handle = {
  0,
  &smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, DVL)() {
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, DVLBeam)();
  if (!smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__msg__DVL__rosidl_typesupport_introspection_c__DVL_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
