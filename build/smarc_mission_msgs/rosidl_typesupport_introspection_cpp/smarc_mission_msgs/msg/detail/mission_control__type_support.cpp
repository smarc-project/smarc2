// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "smarc_mission_msgs/msg/detail/mission_control__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace smarc_mission_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void MissionControl_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) smarc_mission_msgs::msg::MissionControl(_init);
}

void MissionControl_fini_function(void * message_memory)
{
  auto typed_message = static_cast<smarc_mission_msgs::msg::MissionControl *>(message_memory);
  typed_message->~MissionControl();
}

size_t size_function__MissionControl__waypoints(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<smarc_mission_msgs::msg::GotoWaypoint> *>(untyped_member);
  return member->size();
}

const void * get_const_function__MissionControl__waypoints(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<smarc_mission_msgs::msg::GotoWaypoint> *>(untyped_member);
  return &member[index];
}

void * get_function__MissionControl__waypoints(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<smarc_mission_msgs::msg::GotoWaypoint> *>(untyped_member);
  return &member[index];
}

void fetch_function__MissionControl__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const smarc_mission_msgs::msg::GotoWaypoint *>(
    get_const_function__MissionControl__waypoints(untyped_member, index));
  auto & value = *reinterpret_cast<smarc_mission_msgs::msg::GotoWaypoint *>(untyped_value);
  value = item;
}

void assign_function__MissionControl__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<smarc_mission_msgs::msg::GotoWaypoint *>(
    get_function__MissionControl__waypoints(untyped_member, index));
  const auto & value = *reinterpret_cast<const smarc_mission_msgs::msg::GotoWaypoint *>(untyped_value);
  item = value;
}

void resize_function__MissionControl__waypoints(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<smarc_mission_msgs::msg::GotoWaypoint> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember MissionControl_message_member_array[7] = {
  {
    "name",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, name),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "hash",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, hash),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "timeout",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT64,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, timeout),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "command",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, command),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "plan_state",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, plan_state),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "feedback_str",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, feedback_str),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "waypoints",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<smarc_mission_msgs::msg::GotoWaypoint>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs::msg::MissionControl, waypoints),  // bytes offset in struct
    nullptr,  // default value
    size_function__MissionControl__waypoints,  // size() function pointer
    get_const_function__MissionControl__waypoints,  // get_const(index) function pointer
    get_function__MissionControl__waypoints,  // get(index) function pointer
    fetch_function__MissionControl__waypoints,  // fetch(index, &value) function pointer
    assign_function__MissionControl__waypoints,  // assign(index, value) function pointer
    resize_function__MissionControl__waypoints  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers MissionControl_message_members = {
  "smarc_mission_msgs::msg",  // message namespace
  "MissionControl",  // message name
  7,  // number of fields
  sizeof(smarc_mission_msgs::msg::MissionControl),
  MissionControl_message_member_array,  // message members
  MissionControl_init_function,  // function to initialize message memory (memory has to be allocated)
  MissionControl_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t MissionControl_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &MissionControl_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace smarc_mission_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::msg::MissionControl>()
{
  return &::smarc_mission_msgs::msg::rosidl_typesupport_introspection_cpp::MissionControl_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, msg, MissionControl)() {
  return &::smarc_mission_msgs::msg::rosidl_typesupport_introspection_cpp::MissionControl_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
