// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/CTD.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__CTD__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__CTD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/ctd__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_CTD_depth
{
public:
  explicit Init_CTD_depth(::smarc_msgs::msg::CTD & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::CTD depth(::smarc_msgs::msg::CTD::_depth_type arg)
  {
    msg_.depth = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::CTD msg_;
};

class Init_CTD_temperature
{
public:
  explicit Init_CTD_temperature(::smarc_msgs::msg::CTD & msg)
  : msg_(msg)
  {}
  Init_CTD_depth temperature(::smarc_msgs::msg::CTD::_temperature_type arg)
  {
    msg_.temperature = std::move(arg);
    return Init_CTD_depth(msg_);
  }

private:
  ::smarc_msgs::msg::CTD msg_;
};

class Init_CTD_conductivity
{
public:
  explicit Init_CTD_conductivity(::smarc_msgs::msg::CTD & msg)
  : msg_(msg)
  {}
  Init_CTD_temperature conductivity(::smarc_msgs::msg::CTD::_conductivity_type arg)
  {
    msg_.conductivity = std::move(arg);
    return Init_CTD_temperature(msg_);
  }

private:
  ::smarc_msgs::msg::CTD msg_;
};

class Init_CTD_header
{
public:
  Init_CTD_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CTD_conductivity header(::smarc_msgs::msg::CTD::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CTD_conductivity(msg_);
  }

private:
  ::smarc_msgs::msg::CTD msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::CTD>()
{
  return smarc_msgs::msg::builder::Init_CTD_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__CTD__BUILDER_HPP_
