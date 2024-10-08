// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/CommsMessage.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/comms_message__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_CommsMessage_data
{
public:
  explicit Init_CommsMessage_data(::smarc_msgs::msg::CommsMessage & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::CommsMessage data(::smarc_msgs::msg::CommsMessage::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::CommsMessage msg_;
};

class Init_CommsMessage_target_ns
{
public:
  explicit Init_CommsMessage_target_ns(::smarc_msgs::msg::CommsMessage & msg)
  : msg_(msg)
  {}
  Init_CommsMessage_data target_ns(::smarc_msgs::msg::CommsMessage::_target_ns_type arg)
  {
    msg_.target_ns = std::move(arg);
    return Init_CommsMessage_data(msg_);
  }

private:
  ::smarc_msgs::msg::CommsMessage msg_;
};

class Init_CommsMessage_source_ns
{
public:
  explicit Init_CommsMessage_source_ns(::smarc_msgs::msg::CommsMessage & msg)
  : msg_(msg)
  {}
  Init_CommsMessage_target_ns source_ns(::smarc_msgs::msg::CommsMessage::_source_ns_type arg)
  {
    msg_.source_ns = std::move(arg);
    return Init_CommsMessage_target_ns(msg_);
  }

private:
  ::smarc_msgs::msg::CommsMessage msg_;
};

class Init_CommsMessage_header
{
public:
  Init_CommsMessage_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CommsMessage_source_ns header(::smarc_msgs::msg::CommsMessage::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CommsMessage_source_ns(msg_);
  }

private:
  ::smarc_msgs::msg::CommsMessage msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::CommsMessage>()
{
  return smarc_msgs::msg::builder::Init_CommsMessage_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__COMMS_MESSAGE__BUILDER_HPP_
