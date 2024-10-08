// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/DVL.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DVL__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__DVL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/dvl__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_DVL_beams
{
public:
  explicit Init_DVL_beams(::smarc_msgs::msg::DVL & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::DVL beams(::smarc_msgs::msg::DVL::_beams_type arg)
  {
    msg_.beams = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::DVL msg_;
};

class Init_DVL_altitude
{
public:
  explicit Init_DVL_altitude(::smarc_msgs::msg::DVL & msg)
  : msg_(msg)
  {}
  Init_DVL_beams altitude(::smarc_msgs::msg::DVL::_altitude_type arg)
  {
    msg_.altitude = std::move(arg);
    return Init_DVL_beams(msg_);
  }

private:
  ::smarc_msgs::msg::DVL msg_;
};

class Init_DVL_velocity_covariance
{
public:
  explicit Init_DVL_velocity_covariance(::smarc_msgs::msg::DVL & msg)
  : msg_(msg)
  {}
  Init_DVL_altitude velocity_covariance(::smarc_msgs::msg::DVL::_velocity_covariance_type arg)
  {
    msg_.velocity_covariance = std::move(arg);
    return Init_DVL_altitude(msg_);
  }

private:
  ::smarc_msgs::msg::DVL msg_;
};

class Init_DVL_velocity
{
public:
  explicit Init_DVL_velocity(::smarc_msgs::msg::DVL & msg)
  : msg_(msg)
  {}
  Init_DVL_velocity_covariance velocity(::smarc_msgs::msg::DVL::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_DVL_velocity_covariance(msg_);
  }

private:
  ::smarc_msgs::msg::DVL msg_;
};

class Init_DVL_header
{
public:
  Init_DVL_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DVL_velocity header(::smarc_msgs::msg::DVL::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_DVL_velocity(msg_);
  }

private:
  ::smarc_msgs::msg::DVL msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::DVL>()
{
  return smarc_msgs::msg::builder::Init_DVL_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DVL__BUILDER_HPP_
