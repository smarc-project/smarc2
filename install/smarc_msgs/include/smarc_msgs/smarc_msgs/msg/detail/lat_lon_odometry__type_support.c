// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/msg/detail/lat_lon_odometry__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/msg/detail/lat_lon_odometry__functions.h"
#include "smarc_msgs/msg/detail/lat_lon_odometry__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `lat_lon_pose`
#include "geographic_msgs/msg/geo_pose.h"
// Member `lat_lon_pose`
#include "geographic_msgs/msg/detail/geo_pose__rosidl_typesupport_introspection_c.h"
// Member `twist`
#include "geometry_msgs/msg/twist_with_covariance.h"
// Member `twist`
#include "geometry_msgs/msg/detail/twist_with_covariance__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__msg__LatLonOdometry__init(message_memory);
}

void smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_fini_function(void * message_memory)
{
  smarc_msgs__msg__LatLonOdometry__fini(message_memory);
}

size_t smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__size_function__LatLonOdometry__covariance(
  const void * untyped_member)
{
  (void)untyped_member;
  return 36;
}

const void * smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_const_function__LatLonOdometry__covariance(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_function__LatLonOdometry__covariance(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__fetch_function__LatLonOdometry__covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_const_function__LatLonOdometry__covariance(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__assign_function__LatLonOdometry__covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_function__LatLonOdometry__covariance(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_member_array[4] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__LatLonOdometry, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "lat_lon_pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__LatLonOdometry, lat_lon_pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "covariance",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    36,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__LatLonOdometry, covariance),  // bytes offset in struct
    NULL,  // default value
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__size_function__LatLonOdometry__covariance,  // size() function pointer
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_const_function__LatLonOdometry__covariance,  // get_const(index) function pointer
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__get_function__LatLonOdometry__covariance,  // get(index) function pointer
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__fetch_function__LatLonOdometry__covariance,  // fetch(index, &value) function pointer
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__assign_function__LatLonOdometry__covariance,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "twist",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__msg__LatLonOdometry, twist),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_members = {
  "smarc_msgs__msg",  // message namespace
  "LatLonOdometry",  // message name
  4,  // number of fields
  sizeof(smarc_msgs__msg__LatLonOdometry),
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_member_array,  // message members
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_type_support_handle = {
  0,
  &smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, LatLonOdometry)() {
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geographic_msgs, msg, GeoPose)();
  smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, TwistWithCovariance)();
  if (!smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__msg__LatLonOdometry__rosidl_typesupport_introspection_c__LatLonOdometry_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
