// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace sam_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void UavcanNodeStatusNamed_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) sam_msgs::msg::UavcanNodeStatusNamed(_init);
}

void UavcanNodeStatusNamed_fini_function(void * message_memory)
{
  auto typed_message = static_cast<sam_msgs::msg::UavcanNodeStatusNamed *>(message_memory);
  typed_message->~UavcanNodeStatusNamed();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember UavcanNodeStatusNamed_message_member_array[3] = {
  {
    "id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs::msg::UavcanNodeStatusNamed, id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "name",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs::msg::UavcanNodeStatusNamed, name),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "ns",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<sam_msgs::msg::UavcanNodeStatus>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs::msg::UavcanNodeStatusNamed, ns),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers UavcanNodeStatusNamed_message_members = {
  "sam_msgs::msg",  // message namespace
  "UavcanNodeStatusNamed",  // message name
  3,  // number of fields
  sizeof(sam_msgs::msg::UavcanNodeStatusNamed),
  UavcanNodeStatusNamed_message_member_array,  // message members
  UavcanNodeStatusNamed_init_function,  // function to initialize message memory (memory has to be allocated)
  UavcanNodeStatusNamed_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t UavcanNodeStatusNamed_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &UavcanNodeStatusNamed_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace sam_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<sam_msgs::msg::UavcanNodeStatusNamed>()
{
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::UavcanNodeStatusNamed_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, sam_msgs, msg, UavcanNodeStatusNamed)() {
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::UavcanNodeStatusNamed_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
