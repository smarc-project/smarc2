// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/CTP.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CTP__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CTP__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/ctp__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_CTP_pressure
{
public:
  explicit Init_CTP_pressure(::sam_msgs::msg::CTP & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::CTP pressure(::sam_msgs::msg::CTP::_pressure_type arg)
  {
    msg_.pressure = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::CTP msg_;
};

class Init_CTP_temperature
{
public:
  explicit Init_CTP_temperature(::sam_msgs::msg::CTP & msg)
  : msg_(msg)
  {}
  Init_CTP_pressure temperature(::sam_msgs::msg::CTP::_temperature_type arg)
  {
    msg_.temperature = std::move(arg);
    return Init_CTP_pressure(msg_);
  }

private:
  ::sam_msgs::msg::CTP msg_;
};

class Init_CTP_conductivity
{
public:
  explicit Init_CTP_conductivity(::sam_msgs::msg::CTP & msg)
  : msg_(msg)
  {}
  Init_CTP_temperature conductivity(::sam_msgs::msg::CTP::_conductivity_type arg)
  {
    msg_.conductivity = std::move(arg);
    return Init_CTP_temperature(msg_);
  }

private:
  ::sam_msgs::msg::CTP msg_;
};

class Init_CTP_header
{
public:
  Init_CTP_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CTP_conductivity header(::sam_msgs::msg::CTP::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CTP_conductivity(msg_);
  }

private:
  ::sam_msgs::msg::CTP msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::CTP>()
{
  return sam_msgs::msg::builder::Init_CTP_header();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CTP__BUILDER_HPP_
