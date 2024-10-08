// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/ThrusterFeedback.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/thruster_feedback__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrusterFeedback_torque
{
public:
  explicit Init_ThrusterFeedback_torque(::smarc_msgs::msg::ThrusterFeedback & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::ThrusterFeedback torque(::smarc_msgs::msg::ThrusterFeedback::_torque_type arg)
  {
    msg_.torque = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterFeedback msg_;
};

class Init_ThrusterFeedback_current
{
public:
  explicit Init_ThrusterFeedback_current(::smarc_msgs::msg::ThrusterFeedback & msg)
  : msg_(msg)
  {}
  Init_ThrusterFeedback_torque current(::smarc_msgs::msg::ThrusterFeedback::_current_type arg)
  {
    msg_.current = std::move(arg);
    return Init_ThrusterFeedback_torque(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterFeedback msg_;
};

class Init_ThrusterFeedback_dc
{
public:
  explicit Init_ThrusterFeedback_dc(::smarc_msgs::msg::ThrusterFeedback & msg)
  : msg_(msg)
  {}
  Init_ThrusterFeedback_current dc(::smarc_msgs::msg::ThrusterFeedback::_dc_type arg)
  {
    msg_.dc = std::move(arg);
    return Init_ThrusterFeedback_current(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterFeedback msg_;
};

class Init_ThrusterFeedback_rpm
{
public:
  explicit Init_ThrusterFeedback_rpm(::smarc_msgs::msg::ThrusterFeedback & msg)
  : msg_(msg)
  {}
  Init_ThrusterFeedback_dc rpm(::smarc_msgs::msg::ThrusterFeedback::_rpm_type arg)
  {
    msg_.rpm = std::move(arg);
    return Init_ThrusterFeedback_dc(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterFeedback msg_;
};

class Init_ThrusterFeedback_header
{
public:
  Init_ThrusterFeedback_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ThrusterFeedback_rpm header(::smarc_msgs::msg::ThrusterFeedback::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ThrusterFeedback_rpm(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterFeedback msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::ThrusterFeedback>()
{
  return smarc_msgs::msg::builder::Init_ThrusterFeedback_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__BUILDER_HPP_
