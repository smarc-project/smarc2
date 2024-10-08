// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ThrusterAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/thruster_angles__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrusterAngles_header
{
public:
  explicit Init_ThrusterAngles_header(::sam_msgs::msg::ThrusterAngles & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::ThrusterAngles header(::sam_msgs::msg::ThrusterAngles::_header_type arg)
  {
    msg_.header = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterAngles msg_;
};

class Init_ThrusterAngles_thruster_horizontal_radians
{
public:
  explicit Init_ThrusterAngles_thruster_horizontal_radians(::sam_msgs::msg::ThrusterAngles & msg)
  : msg_(msg)
  {}
  Init_ThrusterAngles_header thruster_horizontal_radians(::sam_msgs::msg::ThrusterAngles::_thruster_horizontal_radians_type arg)
  {
    msg_.thruster_horizontal_radians = std::move(arg);
    return Init_ThrusterAngles_header(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterAngles msg_;
};

class Init_ThrusterAngles_thruster_vertical_radians
{
public:
  Init_ThrusterAngles_thruster_vertical_radians()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ThrusterAngles_thruster_horizontal_radians thruster_vertical_radians(::sam_msgs::msg::ThrusterAngles::_thruster_vertical_radians_type arg)
  {
    msg_.thruster_vertical_radians = std::move(arg);
    return Init_ThrusterAngles_thruster_horizontal_radians(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterAngles msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ThrusterAngles>()
{
  return sam_msgs::msg::builder::Init_ThrusterAngles_thruster_vertical_radians();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__BUILDER_HPP_
