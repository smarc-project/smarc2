// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/StringArray.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/string_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_StringArray_string_array
{
public:
  Init_StringArray_string_array()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::msg::StringArray string_array(::smarc_msgs::msg::StringArray::_string_array_type arg)
  {
    msg_.string_array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::StringArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::StringArray>()
{
  return smarc_msgs::msg::builder::Init_StringArray_string_array();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__BUILDER_HPP_
