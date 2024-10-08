// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from sam_msgs:msg/Links.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "sam_msgs/msg/detail/links__struct.hpp"
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

void Links_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) sam_msgs::msg::Links(_init);
}

void Links_fini_function(void * message_memory)
{
  auto typed_message = static_cast<sam_msgs::msg::Links *>(message_memory);
  typed_message->~Links();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Links_message_member_array[1] = {
  {
    "structure_needs_at_least_one_member",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs::msg::Links, structure_needs_at_least_one_member),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Links_message_members = {
  "sam_msgs::msg",  // message namespace
  "Links",  // message name
  1,  // number of fields
  sizeof(sam_msgs::msg::Links),
  Links_message_member_array,  // message members
  Links_init_function,  // function to initialize message memory (memory has to be allocated)
  Links_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Links_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Links_message_members,
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
get_message_type_support_handle<sam_msgs::msg::Links>()
{
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::Links_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, sam_msgs, msg, Links)() {
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::Links_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
