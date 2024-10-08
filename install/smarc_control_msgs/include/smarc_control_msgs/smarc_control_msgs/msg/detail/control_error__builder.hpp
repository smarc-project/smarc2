// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_control_msgs:msg/ControlError.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__BUILDER_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_control_msgs/msg/detail/control_error__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_control_msgs
{

namespace msg
{

namespace builder
{

class Init_ControlError_distance
{
public:
  explicit Init_ControlError_distance(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  ::smarc_control_msgs::msg::ControlError distance(::smarc_control_msgs::msg::ControlError::_distance_type arg)
  {
    msg_.distance = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_heading
{
public:
  explicit Init_ControlError_heading(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_distance heading(::smarc_control_msgs::msg::ControlError::_heading_type arg)
  {
    msg_.heading = std::move(arg);
    return Init_ControlError_distance(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_yaw
{
public:
  explicit Init_ControlError_yaw(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_heading yaw(::smarc_control_msgs::msg::ControlError::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return Init_ControlError_heading(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_pitch
{
public:
  explicit Init_ControlError_pitch(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_yaw pitch(::smarc_control_msgs::msg::ControlError::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_ControlError_yaw(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_roll
{
public:
  explicit Init_ControlError_roll(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_pitch roll(::smarc_control_msgs::msg::ControlError::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_ControlError_pitch(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_z
{
public:
  explicit Init_ControlError_z(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_roll z(::smarc_control_msgs::msg::ControlError::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_ControlError_roll(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_y
{
public:
  explicit Init_ControlError_y(::smarc_control_msgs::msg::ControlError & msg)
  : msg_(msg)
  {}
  Init_ControlError_z y(::smarc_control_msgs::msg::ControlError::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_ControlError_z(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

class Init_ControlError_x
{
public:
  Init_ControlError_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ControlError_y x(::smarc_control_msgs::msg::ControlError::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_ControlError_y(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlError msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_control_msgs::msg::ControlError>()
{
  return smarc_control_msgs::msg::builder::Init_ControlError_x();
}

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__BUILDER_HPP_
