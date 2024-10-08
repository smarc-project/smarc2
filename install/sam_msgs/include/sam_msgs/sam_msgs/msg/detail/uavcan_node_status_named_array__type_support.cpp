// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamedArray.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "sam_msgs/msg/detail/uavcan_node_status_named_array__struct.hpp"
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

void UavcanNodeStatusNamedArray_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) sam_msgs::msg::UavcanNodeStatusNamedArray(_init);
}

void UavcanNodeStatusNamedArray_fini_function(void * message_memory)
{
  auto typed_message = static_cast<sam_msgs::msg::UavcanNodeStatusNamedArray *>(message_memory);
  typed_message->~UavcanNodeStatusNamedArray();
}

size_t size_function__UavcanNodeStatusNamedArray__array(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<sam_msgs::msg::UavcanNodeStatusNamed> *>(untyped_member);
  return member->size();
}

const void * get_const_function__UavcanNodeStatusNamedArray__array(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<sam_msgs::msg::UavcanNodeStatusNamed> *>(untyped_member);
  return &member[index];
}

void * get_function__UavcanNodeStatusNamedArray__array(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<sam_msgs::msg::UavcanNodeStatusNamed> *>(untyped_member);
  return &member[index];
}

void fetch_function__UavcanNodeStatusNamedArray__array(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const sam_msgs::msg::UavcanNodeStatusNamed *>(
    get_const_function__UavcanNodeStatusNamedArray__array(untyped_member, index));
  auto & value = *reinterpret_cast<sam_msgs::msg::UavcanNodeStatusNamed *>(untyped_value);
  value = item;
}

void assign_function__UavcanNodeStatusNamedArray__array(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<sam_msgs::msg::UavcanNodeStatusNamed *>(
    get_function__UavcanNodeStatusNamedArray__array(untyped_member, index));
  const auto & value = *reinterpret_cast<const sam_msgs::msg::UavcanNodeStatusNamed *>(untyped_value);
  item = value;
}

void resize_function__UavcanNodeStatusNamedArray__array(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<sam_msgs::msg::UavcanNodeStatusNamed> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember UavcanNodeStatusNamedArray_message_member_array[1] = {
  {
    "array",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<sam_msgs::msg::UavcanNodeStatusNamed>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs::msg::UavcanNodeStatusNamedArray, array),  // bytes offset in struct
    nullptr,  // default value
    size_function__UavcanNodeStatusNamedArray__array,  // size() function pointer
    get_const_function__UavcanNodeStatusNamedArray__array,  // get_const(index) function pointer
    get_function__UavcanNodeStatusNamedArray__array,  // get(index) function pointer
    fetch_function__UavcanNodeStatusNamedArray__array,  // fetch(index, &value) function pointer
    assign_function__UavcanNodeStatusNamedArray__array,  // assign(index, value) function pointer
    resize_function__UavcanNodeStatusNamedArray__array  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers UavcanNodeStatusNamedArray_message_members = {
  "sam_msgs::msg",  // message namespace
  "UavcanNodeStatusNamedArray",  // message name
  1,  // number of fields
  sizeof(sam_msgs::msg::UavcanNodeStatusNamedArray),
  UavcanNodeStatusNamedArray_message_member_array,  // message members
  UavcanNodeStatusNamedArray_init_function,  // function to initialize message memory (memory has to be allocated)
  UavcanNodeStatusNamedArray_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t UavcanNodeStatusNamedArray_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &UavcanNodeStatusNamedArray_message_members,
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
get_message_type_support_handle<sam_msgs::msg::UavcanNodeStatusNamedArray>()
{
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::UavcanNodeStatusNamedArray_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, sam_msgs, msg, UavcanNodeStatusNamedArray)() {
  return &::sam_msgs::msg::rosidl_typesupport_introspection_cpp::UavcanNodeStatusNamedArray_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
