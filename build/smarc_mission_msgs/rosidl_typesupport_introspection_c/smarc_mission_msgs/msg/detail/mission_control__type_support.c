// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_mission_msgs/msg/detail/mission_control__rosidl_typesupport_introspection_c.h"
#include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_mission_msgs/msg/detail/mission_control__functions.h"
#include "smarc_mission_msgs/msg/detail/mission_control__struct.h"


// Include directives for member types
// Member `name`
// Member `hash`
// Member `feedback_str`
#include "rosidl_runtime_c/string_functions.h"
// Member `waypoints`
#include "smarc_mission_msgs/msg/goto_waypoint.h"
// Member `waypoints`
#include "smarc_mission_msgs/msg/detail/goto_waypoint__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_mission_msgs__msg__MissionControl__init(message_memory);
}

void smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_fini_function(void * message_memory)
{
  smarc_mission_msgs__msg__MissionControl__fini(message_memory);
}

size_t smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__size_function__MissionControl__waypoints(
  const void * untyped_member)
{
  const smarc_mission_msgs__msg__GotoWaypoint__Sequence * member =
    (const smarc_mission_msgs__msg__GotoWaypoint__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_const_function__MissionControl__waypoints(
  const void * untyped_member, size_t index)
{
  const smarc_mission_msgs__msg__GotoWaypoint__Sequence * member =
    (const smarc_mission_msgs__msg__GotoWaypoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_function__MissionControl__waypoints(
  void * untyped_member, size_t index)
{
  smarc_mission_msgs__msg__GotoWaypoint__Sequence * member =
    (smarc_mission_msgs__msg__GotoWaypoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__fetch_function__MissionControl__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const smarc_mission_msgs__msg__GotoWaypoint * item =
    ((const smarc_mission_msgs__msg__GotoWaypoint *)
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_const_function__MissionControl__waypoints(untyped_member, index));
  smarc_mission_msgs__msg__GotoWaypoint * value =
    (smarc_mission_msgs__msg__GotoWaypoint *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__assign_function__MissionControl__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  smarc_mission_msgs__msg__GotoWaypoint * item =
    ((smarc_mission_msgs__msg__GotoWaypoint *)
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_function__MissionControl__waypoints(untyped_member, index));
  const smarc_mission_msgs__msg__GotoWaypoint * value =
    (const smarc_mission_msgs__msg__GotoWaypoint *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__resize_function__MissionControl__waypoints(
  void * untyped_member, size_t size)
{
  smarc_mission_msgs__msg__GotoWaypoint__Sequence * member =
    (smarc_mission_msgs__msg__GotoWaypoint__Sequence *)(untyped_member);
  smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini(member);
  return smarc_mission_msgs__msg__GotoWaypoint__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_member_array[7] = {
  {
    "name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "hash",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, hash),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "timeout",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, timeout),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "command",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, command),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "plan_state",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, plan_state),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "feedback_str",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, feedback_str),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__msg__MissionControl, waypoints),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__size_function__MissionControl__waypoints,  // size() function pointer
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_const_function__MissionControl__waypoints,  // get_const(index) function pointer
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__get_function__MissionControl__waypoints,  // get(index) function pointer
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__fetch_function__MissionControl__waypoints,  // fetch(index, &value) function pointer
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__assign_function__MissionControl__waypoints,  // assign(index, value) function pointer
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__resize_function__MissionControl__waypoints  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_members = {
  "smarc_mission_msgs__msg",  // message namespace
  "MissionControl",  // message name
  7,  // number of fields
  sizeof(smarc_mission_msgs__msg__MissionControl),
  smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_member_array,  // message members
  smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_type_support_handle = {
  0,
  &smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, msg, MissionControl)() {
  smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_member_array[6].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, msg, GotoWaypoint)();
  if (!smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_mission_msgs__msg__MissionControl__rosidl_typesupport_introspection_c__MissionControl_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
