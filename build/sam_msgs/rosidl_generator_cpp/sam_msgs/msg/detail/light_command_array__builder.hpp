// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/LightCommandArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/light_command_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_LightCommandArray_array
{
public:
  Init_LightCommandArray_array()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::sam_msgs::msg::LightCommandArray array(::sam_msgs::msg::LightCommandArray::_array_type arg)
  {
    msg_.array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::LightCommandArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::LightCommandArray>()
{
  return sam_msgs::msg::builder::Init_LightCommandArray_array();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND_ARRAY__BUILDER_HPP_
