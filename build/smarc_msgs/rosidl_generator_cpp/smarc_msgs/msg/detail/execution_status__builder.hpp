// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/execution_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_ExecutionStatus_execution_queue
{
public:
  explicit Init_ExecutionStatus_execution_queue(::smarc_msgs::msg::ExecutionStatus & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::ExecutionStatus execution_queue(::smarc_msgs::msg::ExecutionStatus::_execution_queue_type arg)
  {
    msg_.execution_queue = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::ExecutionStatus msg_;
};

class Init_ExecutionStatus_currently_executing
{
public:
  explicit Init_ExecutionStatus_currently_executing(::smarc_msgs::msg::ExecutionStatus & msg)
  : msg_(msg)
  {}
  Init_ExecutionStatus_execution_queue currently_executing(::smarc_msgs::msg::ExecutionStatus::_currently_executing_type arg)
  {
    msg_.currently_executing = std::move(arg);
    return Init_ExecutionStatus_execution_queue(msg_);
  }

private:
  ::smarc_msgs::msg::ExecutionStatus msg_;
};

class Init_ExecutionStatus_header
{
public:
  Init_ExecutionStatus_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecutionStatus_currently_executing header(::smarc_msgs::msg::ExecutionStatus::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ExecutionStatus_currently_executing(msg_);
  }

private:
  ::smarc_msgs::msg::ExecutionStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::ExecutionStatus>()
{
  return smarc_msgs::msg::builder::Init_ExecutionStatus_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__BUILDER_HPP_
