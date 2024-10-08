// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/StringStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/string_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_StringStamped_data
{
public:
  explicit Init_StringStamped_data(::smarc_msgs::msg::StringStamped & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::StringStamped data(::smarc_msgs::msg::StringStamped::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::StringStamped msg_;
};

class Init_StringStamped_time_received
{
public:
  explicit Init_StringStamped_time_received(::smarc_msgs::msg::StringStamped & msg)
  : msg_(msg)
  {}
  Init_StringStamped_data time_received(::smarc_msgs::msg::StringStamped::_time_received_type arg)
  {
    msg_.time_received = std::move(arg);
    return Init_StringStamped_data(msg_);
  }

private:
  ::smarc_msgs::msg::StringStamped msg_;
};

class Init_StringStamped_time_sent
{
public:
  Init_StringStamped_time_sent()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StringStamped_time_received time_sent(::smarc_msgs::msg::StringStamped::_time_sent_type arg)
  {
    msg_.time_sent = std::move(arg);
    return Init_StringStamped_time_received(msg_);
  }

private:
  ::smarc_msgs::msg::StringStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::StringStamped>()
{
  return smarc_msgs::msg::builder::Init_StringStamped_time_sent();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_
