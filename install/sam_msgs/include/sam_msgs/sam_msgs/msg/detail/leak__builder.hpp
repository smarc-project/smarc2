// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/Leak.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LEAK__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__LEAK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/leak__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_Leak_leak_counter
{
public:
  explicit Init_Leak_leak_counter(::sam_msgs::msg::Leak & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::Leak leak_counter(::sam_msgs::msg::Leak::_leak_counter_type arg)
  {
    msg_.leak_counter = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::Leak msg_;
};

class Init_Leak_value
{
public:
  Init_Leak_value()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Leak_leak_counter value(::sam_msgs::msg::Leak::_value_type arg)
  {
    msg_.value = std::move(arg);
    return Init_Leak_leak_counter(msg_);
  }

private:
  ::sam_msgs::msg::Leak msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::Leak>()
{
  return sam_msgs::msg::builder::Init_Leak_value();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LEAK__BUILDER_HPP_
