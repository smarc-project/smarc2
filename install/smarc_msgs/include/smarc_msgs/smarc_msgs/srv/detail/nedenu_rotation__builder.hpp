// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:srv/NEDENURotation.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__BUILDER_HPP_
#define SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/srv/detail/nedenu_rotation__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_NEDENURotation_Request_orientation
{
public:
  Init_NEDENURotation_Request_orientation()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::NEDENURotation_Request orientation(::smarc_msgs::srv::NEDENURotation_Request::_orientation_type arg)
  {
    msg_.orientation = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::NEDENURotation_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::NEDENURotation_Request>()
{
  return smarc_msgs::srv::builder::Init_NEDENURotation_Request_orientation();
}

}  // namespace smarc_msgs


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_NEDENURotation_Response_orientation
{
public:
  Init_NEDENURotation_Response_orientation()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::NEDENURotation_Response orientation(::smarc_msgs::srv::NEDENURotation_Response::_orientation_type arg)
  {
    msg_.orientation = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::NEDENURotation_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::NEDENURotation_Response>()
{
  return smarc_msgs::srv::builder::Init_NEDENURotation_Response_orientation();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__BUILDER_HPP_
