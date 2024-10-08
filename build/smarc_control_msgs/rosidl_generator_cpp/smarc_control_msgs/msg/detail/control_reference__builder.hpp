// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_control_msgs:msg/ControlReference.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__BUILDER_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_control_msgs/msg/detail/control_reference__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_control_msgs
{

namespace msg
{

namespace builder
{

class Init_ControlReference_yaw
{
public:
  explicit Init_ControlReference_yaw(::smarc_control_msgs::msg::ControlReference & msg)
  : msg_(msg)
  {}
  ::smarc_control_msgs::msg::ControlReference yaw(::smarc_control_msgs::msg::ControlReference::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

class Init_ControlReference_pitch
{
public:
  explicit Init_ControlReference_pitch(::smarc_control_msgs::msg::ControlReference & msg)
  : msg_(msg)
  {}
  Init_ControlReference_yaw pitch(::smarc_control_msgs::msg::ControlReference::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_ControlReference_yaw(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

class Init_ControlReference_roll
{
public:
  explicit Init_ControlReference_roll(::smarc_control_msgs::msg::ControlReference & msg)
  : msg_(msg)
  {}
  Init_ControlReference_pitch roll(::smarc_control_msgs::msg::ControlReference::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_ControlReference_pitch(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

class Init_ControlReference_z
{
public:
  explicit Init_ControlReference_z(::smarc_control_msgs::msg::ControlReference & msg)
  : msg_(msg)
  {}
  Init_ControlReference_roll z(::smarc_control_msgs::msg::ControlReference::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_ControlReference_roll(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

class Init_ControlReference_y
{
public:
  explicit Init_ControlReference_y(::smarc_control_msgs::msg::ControlReference & msg)
  : msg_(msg)
  {}
  Init_ControlReference_z y(::smarc_control_msgs::msg::ControlReference::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_ControlReference_z(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

class Init_ControlReference_x
{
public:
  Init_ControlReference_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ControlReference_y x(::smarc_control_msgs::msg::ControlReference::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_ControlReference_y(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlReference msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_control_msgs::msg::ControlReference>()
{
  return smarc_control_msgs::msg::builder::Init_ControlReference_x();
}

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__BUILDER_HPP_
