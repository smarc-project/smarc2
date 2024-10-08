// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/SensorStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/sensor_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_SensorStatus_diagnostics_message
{
public:
  explicit Init_SensorStatus_diagnostics_message(::smarc_msgs::msg::SensorStatus & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::SensorStatus diagnostics_message(::smarc_msgs::msg::SensorStatus::_diagnostics_message_type arg)
  {
    msg_.diagnostics_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::SensorStatus msg_;
};

class Init_SensorStatus_service_name
{
public:
  explicit Init_SensorStatus_service_name(::smarc_msgs::msg::SensorStatus & msg)
  : msg_(msg)
  {}
  Init_SensorStatus_diagnostics_message service_name(::smarc_msgs::msg::SensorStatus::_service_name_type arg)
  {
    msg_.service_name = std::move(arg);
    return Init_SensorStatus_diagnostics_message(msg_);
  }

private:
  ::smarc_msgs::msg::SensorStatus msg_;
};

class Init_SensorStatus_sensor_status
{
public:
  Init_SensorStatus_sensor_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SensorStatus_service_name sensor_status(::smarc_msgs::msg::SensorStatus::_sensor_status_type arg)
  {
    msg_.sensor_status = std::move(arg);
    return Init_SensorStatus_service_name(msg_);
  }

private:
  ::smarc_msgs::msg::SensorStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::SensorStatus>()
{
  return smarc_msgs::msg::builder::Init_SensorStatus_sensor_status();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__SENSOR_STATUS__BUILDER_HPP_
