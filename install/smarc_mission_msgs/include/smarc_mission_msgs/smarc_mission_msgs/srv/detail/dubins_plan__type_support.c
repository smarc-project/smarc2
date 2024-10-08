// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_mission_msgs/srv/detail/dubins_plan__rosidl_typesupport_introspection_c.h"
#include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_mission_msgs/srv/detail/dubins_plan__functions.h"
#include "smarc_mission_msgs/srv/detail/dubins_plan__struct.h"


// Include directives for member types
// Member `waypoints`
#include "geometry_msgs/msg/pose2_d.h"
// Member `waypoints`
#include "geometry_msgs/msg/detail/pose2_d__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_mission_msgs__srv__DubinsPlan_Request__init(message_memory);
}

void smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_fini_function(void * message_memory)
{
  smarc_mission_msgs__srv__DubinsPlan_Request__fini(message_memory);
}

size_t smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Request__waypoints(
  const void * untyped_member)
{
  const geometry_msgs__msg__Pose2D__Sequence * member =
    (const geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Request__waypoints(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Pose2D__Sequence * member =
    (const geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Request__waypoints(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Pose2D__Sequence * member =
    (geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Request__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Pose2D * item =
    ((const geometry_msgs__msg__Pose2D *)
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Request__waypoints(untyped_member, index));
  geometry_msgs__msg__Pose2D * value =
    (geometry_msgs__msg__Pose2D *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Request__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Pose2D * item =
    ((geometry_msgs__msg__Pose2D *)
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Request__waypoints(untyped_member, index));
  const geometry_msgs__msg__Pose2D * value =
    (const geometry_msgs__msg__Pose2D *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Request__waypoints(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Pose2D__Sequence * member =
    (geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  geometry_msgs__msg__Pose2D__Sequence__fini(member);
  return geometry_msgs__msg__Pose2D__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_member_array[3] = {
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__DubinsPlan_Request, waypoints),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Request__waypoints,  // size() function pointer
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Request__waypoints,  // get_const(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Request__waypoints,  // get(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Request__waypoints,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Request__waypoints,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Request__waypoints  // resize(index) function pointer
  },
  {
    "step",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__DubinsPlan_Request, step),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "turning_radius",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__DubinsPlan_Request, turning_radius),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_members = {
  "smarc_mission_msgs__srv",  // message namespace
  "DubinsPlan_Request",  // message name
  3,  // number of fields
  sizeof(smarc_mission_msgs__srv__DubinsPlan_Request),
  smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_member_array,  // message members
  smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Request)() {
  smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose2D)();
  if (!smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_mission_msgs__srv__DubinsPlan_Request__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "smarc_mission_msgs/srv/detail/dubins_plan__rosidl_typesupport_introspection_c.h"
// already included above
// #include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/dubins_plan__functions.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/dubins_plan__struct.h"


// Include directives for member types
// Member `waypoints`
// already included above
// #include "geometry_msgs/msg/pose2_d.h"
// Member `waypoints`
// already included above
// #include "geometry_msgs/msg/detail/pose2_d__rosidl_typesupport_introspection_c.h"
// Member `original_wp_indices`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_mission_msgs__srv__DubinsPlan_Response__init(message_memory);
}

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_fini_function(void * message_memory)
{
  smarc_mission_msgs__srv__DubinsPlan_Response__fini(message_memory);
}

size_t smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Response__waypoints(
  const void * untyped_member)
{
  const geometry_msgs__msg__Pose2D__Sequence * member =
    (const geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__waypoints(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Pose2D__Sequence * member =
    (const geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__waypoints(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Pose2D__Sequence * member =
    (geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Response__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Pose2D * item =
    ((const geometry_msgs__msg__Pose2D *)
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__waypoints(untyped_member, index));
  geometry_msgs__msg__Pose2D * value =
    (geometry_msgs__msg__Pose2D *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Response__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Pose2D * item =
    ((geometry_msgs__msg__Pose2D *)
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__waypoints(untyped_member, index));
  const geometry_msgs__msg__Pose2D * value =
    (const geometry_msgs__msg__Pose2D *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Response__waypoints(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Pose2D__Sequence * member =
    (geometry_msgs__msg__Pose2D__Sequence *)(untyped_member);
  geometry_msgs__msg__Pose2D__Sequence__fini(member);
  return geometry_msgs__msg__Pose2D__Sequence__init(member, size);
}

size_t smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Response__original_wp_indices(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint16__Sequence * member =
    (const rosidl_runtime_c__uint16__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__original_wp_indices(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint16__Sequence * member =
    (const rosidl_runtime_c__uint16__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__original_wp_indices(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint16__Sequence * member =
    (rosidl_runtime_c__uint16__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Response__original_wp_indices(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint16_t * item =
    ((const uint16_t *)
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__original_wp_indices(untyped_member, index));
  uint16_t * value =
    (uint16_t *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Response__original_wp_indices(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint16_t * item =
    ((uint16_t *)
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__original_wp_indices(untyped_member, index));
  const uint16_t * value =
    (const uint16_t *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Response__original_wp_indices(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint16__Sequence * member =
    (rosidl_runtime_c__uint16__Sequence *)(untyped_member);
  rosidl_runtime_c__uint16__Sequence__fini(member);
  return rosidl_runtime_c__uint16__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_member_array[2] = {
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__DubinsPlan_Response, waypoints),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Response__waypoints,  // size() function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__waypoints,  // get_const(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__waypoints,  // get(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Response__waypoints,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Response__waypoints,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Response__waypoints  // resize(index) function pointer
  },
  {
    "original_wp_indices",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__DubinsPlan_Response, original_wp_indices),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__size_function__DubinsPlan_Response__original_wp_indices,  // size() function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_const_function__DubinsPlan_Response__original_wp_indices,  // get_const(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__get_function__DubinsPlan_Response__original_wp_indices,  // get(index) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__fetch_function__DubinsPlan_Response__original_wp_indices,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__assign_function__DubinsPlan_Response__original_wp_indices,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__resize_function__DubinsPlan_Response__original_wp_indices  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_members = {
  "smarc_mission_msgs__srv",  // message namespace
  "DubinsPlan_Response",  // message name
  2,  // number of fields
  sizeof(smarc_mission_msgs__srv__DubinsPlan_Response),
  smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_member_array,  // message members
  smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Response)() {
  smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose2D)();
  if (!smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_mission_msgs__srv__DubinsPlan_Response__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/dubins_plan__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_members = {
  "smarc_mission_msgs__srv",  // service namespace
  "DubinsPlan",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_Request_message_type_support_handle,
  NULL  // response message
  // smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_Response_message_type_support_handle
};

static rosidl_service_type_support_t smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan)() {
  if (!smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, DubinsPlan_Response)()->data;
  }

  return &smarc_mission_msgs__srv__detail__dubins_plan__rosidl_typesupport_introspection_c__DubinsPlan_service_type_support_handle;
}
