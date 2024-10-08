// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/DualThrusterFeedback.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/dual_thruster_feedback__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_DualThrusterFeedback_thruster_back
{
public:
  explicit Init_DualThrusterFeedback_thruster_back(::smarc_msgs::msg::DualThrusterFeedback & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::DualThrusterFeedback thruster_back(::smarc_msgs::msg::DualThrusterFeedback::_thruster_back_type arg)
  {
    msg_.thruster_back = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::DualThrusterFeedback msg_;
};

class Init_DualThrusterFeedback_thruster_front
{
public:
  Init_DualThrusterFeedback_thruster_front()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DualThrusterFeedback_thruster_back thruster_front(::smarc_msgs::msg::DualThrusterFeedback::_thruster_front_type arg)
  {
    msg_.thruster_front = std::move(arg);
    return Init_DualThrusterFeedback_thruster_back(msg_);
  }

private:
  ::smarc_msgs::msg::DualThrusterFeedback msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::DualThrusterFeedback>()
{
  return smarc_msgs::msg::builder::Init_DualThrusterFeedback_thruster_front();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__BUILDER_HPP_
