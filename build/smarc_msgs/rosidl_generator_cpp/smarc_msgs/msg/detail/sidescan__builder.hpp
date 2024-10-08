// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SIDESCAN__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__SIDESCAN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/sidescan__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_Sidescan_extra_channel
{
public:
  explicit Init_Sidescan_extra_channel(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::Sidescan extra_channel(::smarc_msgs::msg::Sidescan::_extra_channel_type arg)
  {
    msg_.extra_channel = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_starboard_channel_angle_low
{
public:
  explicit Init_Sidescan_starboard_channel_angle_low(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_extra_channel starboard_channel_angle_low(::smarc_msgs::msg::Sidescan::_starboard_channel_angle_low_type arg)
  {
    msg_.starboard_channel_angle_low = std::move(arg);
    return Init_Sidescan_extra_channel(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_starboard_channel_angle_high
{
public:
  explicit Init_Sidescan_starboard_channel_angle_high(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_starboard_channel_angle_low starboard_channel_angle_high(::smarc_msgs::msg::Sidescan::_starboard_channel_angle_high_type arg)
  {
    msg_.starboard_channel_angle_high = std::move(arg);
    return Init_Sidescan_starboard_channel_angle_low(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_port_channel_angle_low
{
public:
  explicit Init_Sidescan_port_channel_angle_low(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_starboard_channel_angle_high port_channel_angle_low(::smarc_msgs::msg::Sidescan::_port_channel_angle_low_type arg)
  {
    msg_.port_channel_angle_low = std::move(arg);
    return Init_Sidescan_starboard_channel_angle_high(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_port_channel_angle_high
{
public:
  explicit Init_Sidescan_port_channel_angle_high(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_port_channel_angle_low port_channel_angle_high(::smarc_msgs::msg::Sidescan::_port_channel_angle_high_type arg)
  {
    msg_.port_channel_angle_high = std::move(arg);
    return Init_Sidescan_port_channel_angle_low(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_starboard_channel
{
public:
  explicit Init_Sidescan_starboard_channel(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_port_channel_angle_high starboard_channel(::smarc_msgs::msg::Sidescan::_starboard_channel_type arg)
  {
    msg_.starboard_channel = std::move(arg);
    return Init_Sidescan_port_channel_angle_high(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_port_channel
{
public:
  explicit Init_Sidescan_port_channel(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_starboard_channel port_channel(::smarc_msgs::msg::Sidescan::_port_channel_type arg)
  {
    msg_.port_channel = std::move(arg);
    return Init_Sidescan_starboard_channel(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_max_duration
{
public:
  explicit Init_Sidescan_max_duration(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_port_channel max_duration(::smarc_msgs::msg::Sidescan::_max_duration_type arg)
  {
    msg_.max_duration = std::move(arg);
    return Init_Sidescan_port_channel(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_decimation
{
public:
  explicit Init_Sidescan_decimation(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_max_duration decimation(::smarc_msgs::msg::Sidescan::_decimation_type arg)
  {
    msg_.decimation = std::move(arg);
    return Init_Sidescan_max_duration(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_gain
{
public:
  explicit Init_Sidescan_gain(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_decimation gain(::smarc_msgs::msg::Sidescan::_gain_type arg)
  {
    msg_.gain = std::move(arg);
    return Init_Sidescan_decimation(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_frequency_id
{
public:
  explicit Init_Sidescan_frequency_id(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_gain frequency_id(::smarc_msgs::msg::Sidescan::_frequency_id_type arg)
  {
    msg_.frequency_id = std::move(arg);
    return Init_Sidescan_gain(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_time
{
public:
  explicit Init_Sidescan_time(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_frequency_id time(::smarc_msgs::msg::Sidescan::_time_type arg)
  {
    msg_.time = std::move(arg);
    return Init_Sidescan_frequency_id(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_type
{
public:
  explicit Init_Sidescan_type(::smarc_msgs::msg::Sidescan & msg)
  : msg_(msg)
  {}
  Init_Sidescan_time type(::smarc_msgs::msg::Sidescan::_type_type arg)
  {
    msg_.type = std::move(arg);
    return Init_Sidescan_time(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

class Init_Sidescan_header
{
public:
  Init_Sidescan_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Sidescan_type header(::smarc_msgs::msg::Sidescan::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_Sidescan_type(msg_);
  }

private:
  ::smarc_msgs::msg::Sidescan msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::Sidescan>()
{
  return smarc_msgs::msg::builder::Init_Sidescan_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__SIDESCAN__BUILDER_HPP_
