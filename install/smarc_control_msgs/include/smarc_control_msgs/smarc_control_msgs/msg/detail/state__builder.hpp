// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_control_msgs:msg/State.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_control_msgs/msg/detail/state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_control_msgs
{

namespace msg
{

namespace builder
{

class Init_State_yaw
{
public:
  explicit Init_State_yaw(::smarc_control_msgs::msg::State & msg)
  : msg_(msg)
  {}
  ::smarc_control_msgs::msg::State yaw(::smarc_control_msgs::msg::State::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

class Init_State_pitch
{
public:
  explicit Init_State_pitch(::smarc_control_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_yaw pitch(::smarc_control_msgs::msg::State::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_State_yaw(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

class Init_State_roll
{
public:
  explicit Init_State_roll(::smarc_control_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_pitch roll(::smarc_control_msgs::msg::State::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_State_pitch(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

class Init_State_z
{
public:
  explicit Init_State_z(::smarc_control_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_roll z(::smarc_control_msgs::msg::State::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_State_roll(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

class Init_State_y
{
public:
  explicit Init_State_y(::smarc_control_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_z y(::smarc_control_msgs::msg::State::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_State_z(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

class Init_State_x
{
public:
  Init_State_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_State_y x(::smarc_control_msgs::msg::State::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_State_y(msg_);
  }

private:
  ::smarc_control_msgs::msg::State msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_control_msgs::msg::State>()
{
  return smarc_control_msgs::msg::builder::Init_State_x();
}

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_
