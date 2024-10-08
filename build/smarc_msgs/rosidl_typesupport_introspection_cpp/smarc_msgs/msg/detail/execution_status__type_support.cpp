// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "smarc_msgs/msg/detail/execution_status__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace smarc_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void ExecutionStatus_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) smarc_msgs::msg::ExecutionStatus(_init);
}

void ExecutionStatus_fini_function(void * message_memory)
{
  auto typed_message = static_cast<smarc_msgs::msg::ExecutionStatus *>(message_memory);
  typed_message->~ExecutionStatus();
}

size_t size_function__ExecutionStatus__execution_queue(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<smarc_msgs::msg::SMTask> *>(untyped_member);
  return member->size();
}

const void * get_const_function__ExecutionStatus__execution_queue(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<smarc_msgs::msg::SMTask> *>(untyped_member);
  return &member[index];
}

void * get_function__ExecutionStatus__execution_queue(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<smarc_msgs::msg::SMTask> *>(untyped_member);
  return &member[index];
}

void fetch_function__ExecutionStatus__execution_queue(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const smarc_msgs::msg::SMTask *>(
    get_const_function__ExecutionStatus__execution_queue(untyped_member, index));
  auto & value = *reinterpret_cast<smarc_msgs::msg::SMTask *>(untyped_value);
  value = item;
}

void assign_function__ExecutionStatus__execution_queue(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<smarc_msgs::msg::SMTask *>(
    get_function__ExecutionStatus__execution_queue(untyped_member, index));
  const auto & value = *reinterpret_cast<const smarc_msgs::msg::SMTask *>(untyped_value);
  item = value;
}

void resize_function__ExecutionStatus__execution_queue(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<smarc_msgs::msg::SMTask> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember ExecutionStatus_message_member_array[3] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs::msg::ExecutionStatus, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "currently_executing",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs::msg::ExecutionStatus, currently_executing),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "execution_queue",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<smarc_msgs::msg::SMTask>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs::msg::ExecutionStatus, execution_queue),  // bytes offset in struct
    nullptr,  // default value
    size_function__ExecutionStatus__execution_queue,  // size() function pointer
    get_const_function__ExecutionStatus__execution_queue,  // get_const(index) function pointer
    get_function__ExecutionStatus__execution_queue,  // get(index) function pointer
    fetch_function__ExecutionStatus__execution_queue,  // fetch(index, &value) function pointer
    assign_function__ExecutionStatus__execution_queue,  // assign(index, value) function pointer
    resize_function__ExecutionStatus__execution_queue  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers ExecutionStatus_message_members = {
  "smarc_msgs::msg",  // message namespace
  "ExecutionStatus",  // message name
  3,  // number of fields
  sizeof(smarc_msgs::msg::ExecutionStatus),
  ExecutionStatus_message_member_array,  // message members
  ExecutionStatus_init_function,  // function to initialize message memory (memory has to be allocated)
  ExecutionStatus_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t ExecutionStatus_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &ExecutionStatus_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace smarc_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_msgs::msg::ExecutionStatus>()
{
  return &::smarc_msgs::msg::rosidl_typesupport_introspection_cpp::ExecutionStatus_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_msgs, msg, ExecutionStatus)() {
  return &::smarc_msgs::msg::rosidl_typesupport_introspection_cpp::ExecutionStatus_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
