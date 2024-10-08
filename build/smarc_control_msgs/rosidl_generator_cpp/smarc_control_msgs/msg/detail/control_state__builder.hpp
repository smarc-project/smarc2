// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_control_msgs:msg/ControlState.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__BUILDER_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_control_msgs/msg/detail/control_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_control_msgs
{

namespace msg
{

namespace builder
{

class Init_ControlState_vel
{
public:
  explicit Init_ControlState_vel(::smarc_control_msgs::msg::ControlState & msg)
  : msg_(msg)
  {}
  ::smarc_control_msgs::msg::ControlState vel(::smarc_control_msgs::msg::ControlState::_vel_type arg)
  {
    msg_.vel = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlState msg_;
};

class Init_ControlState_pose
{
public:
  Init_ControlState_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ControlState_vel pose(::smarc_control_msgs::msg::ControlState::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_ControlState_vel(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_control_msgs::msg::ControlState>()
{
  return smarc_control_msgs::msg::builder::Init_ControlState_pose();
}

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__BUILDER_HPP_
