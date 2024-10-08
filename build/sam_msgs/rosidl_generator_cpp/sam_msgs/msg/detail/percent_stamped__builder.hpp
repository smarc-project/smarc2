// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/PercentStamped.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__PERCENT_STAMPED__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__PERCENT_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/percent_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_PercentStamped_header
{
public:
  explicit Init_PercentStamped_header(::sam_msgs::msg::PercentStamped & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::PercentStamped header(::sam_msgs::msg::PercentStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::PercentStamped msg_;
};

class Init_PercentStamped_value
{
public:
  Init_PercentStamped_value()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PercentStamped_header value(::sam_msgs::msg::PercentStamped::_value_type arg)
  {
    msg_.value = std::move(arg);
    return Init_PercentStamped_header(msg_);
  }

private:
  ::sam_msgs::msg::PercentStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::PercentStamped>()
{
  return sam_msgs::msg::builder::Init_PercentStamped_value();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__PERCENT_STAMPED__BUILDER_HPP_
