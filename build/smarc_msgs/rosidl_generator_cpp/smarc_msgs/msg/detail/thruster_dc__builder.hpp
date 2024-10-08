// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/ThrusterDC.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/thruster_dc__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrusterDC_dc
{
public:
  Init_ThrusterDC_dc()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::msg::ThrusterDC dc(::smarc_msgs::msg::ThrusterDC::_dc_type arg)
  {
    msg_.dc = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::ThrusterDC msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::ThrusterDC>()
{
  return smarc_msgs::msg::builder::Init_ThrusterDC_dc();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__BUILDER_HPP_
