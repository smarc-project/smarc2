// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/BallastAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/ballast_angles__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_BallastAngles_header
{
public:
  explicit Init_BallastAngles_header(::sam_msgs::msg::BallastAngles & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::BallastAngles header(::sam_msgs::msg::BallastAngles::_header_type arg)
  {
    msg_.header = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::BallastAngles msg_;
};

class Init_BallastAngles_weight_2_offset_radians
{
public:
  explicit Init_BallastAngles_weight_2_offset_radians(::sam_msgs::msg::BallastAngles & msg)
  : msg_(msg)
  {}
  Init_BallastAngles_header weight_2_offset_radians(::sam_msgs::msg::BallastAngles::_weight_2_offset_radians_type arg)
  {
    msg_.weight_2_offset_radians = std::move(arg);
    return Init_BallastAngles_header(msg_);
  }

private:
  ::sam_msgs::msg::BallastAngles msg_;
};

class Init_BallastAngles_weight_1_offset_radians
{
public:
  Init_BallastAngles_weight_1_offset_radians()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_BallastAngles_weight_2_offset_radians weight_1_offset_radians(::sam_msgs::msg::BallastAngles::_weight_1_offset_radians_type arg)
  {
    msg_.weight_1_offset_radians = std::move(arg);
    return Init_BallastAngles_weight_2_offset_radians(msg_);
  }

private:
  ::sam_msgs::msg::BallastAngles msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::BallastAngles>()
{
  return sam_msgs::msg::builder::Init_BallastAngles_weight_1_offset_radians();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__BUILDER_HPP_
