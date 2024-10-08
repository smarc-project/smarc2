// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/ThrusterRPM.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/thruster_rpm__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrusterRPM_rpm
{
public:
  Init_ThrusterRPM_rpm()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::msg::ThrusterRPM rpm(::smarc_msgs::msg::ThrusterRPM::_rpm_type arg)
  {
    msg_.rpm = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterRPM msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::ThrusterRPM>()
{
  return smarc_msgs::msg::builder::Init_ThrusterRPM_rpm();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__BUILDER_HPP_
