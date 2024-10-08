// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_control_msgs:msg/ControlInput.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__BUILDER_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_control_msgs/msg/detail/control_input__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_control_msgs
{

namespace msg
{

namespace builder
{

class Init_ControlInput_lcg
{
public:
  explicit Init_ControlInput_lcg(::smarc_control_msgs::msg::ControlInput & msg)
  : msg_(msg)
  {}
  ::smarc_control_msgs::msg::ControlInput lcg(::smarc_control_msgs::msg::ControlInput::_lcg_type arg)
  {
    msg_.lcg = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlInput msg_;
};

class Init_ControlInput_vbs
{
public:
  explicit Init_ControlInput_vbs(::smarc_control_msgs::msg::ControlInput & msg)
  : msg_(msg)
  {}
  Init_ControlInput_lcg vbs(::smarc_control_msgs::msg::ControlInput::_vbs_type arg)
  {
    msg_.vbs = std::move(arg);
    return Init_ControlInput_lcg(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlInput msg_;
};

class Init_ControlInput_thrusterhorizontal
{
public:
  explicit Init_ControlInput_thrusterhorizontal(::smarc_control_msgs::msg::ControlInput & msg)
  : msg_(msg)
  {}
  Init_ControlInput_vbs thrusterhorizontal(::smarc_control_msgs::msg::ControlInput::_thrusterhorizontal_type arg)
  {
    msg_.thrusterhorizontal = std::move(arg);
    return Init_ControlInput_vbs(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlInput msg_;
};

class Init_ControlInput_thrustervertical
{
public:
  explicit Init_ControlInput_thrustervertical(::smarc_control_msgs::msg::ControlInput & msg)
  : msg_(msg)
  {}
  Init_ControlInput_thrusterhorizontal thrustervertical(::smarc_control_msgs::msg::ControlInput::_thrustervertical_type arg)
  {
    msg_.thrustervertical = std::move(arg);
    return Init_ControlInput_thrusterhorizontal(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlInput msg_;
};

class Init_ControlInput_thrusterrpm
{
public:
  Init_ControlInput_thrusterrpm()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ControlInput_thrustervertical thrusterrpm(::smarc_control_msgs::msg::ControlInput::_thrusterrpm_type arg)
  {
    msg_.thrusterrpm = std::move(arg);
    return Init_ControlInput_thrustervertical(msg_);
  }

private:
  ::smarc_control_msgs::msg::ControlInput msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_control_msgs::msg::ControlInput>()
{
  return smarc_control_msgs::msg::builder::Init_ControlInput_thrusterrpm();
}

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__BUILDER_HPP_
