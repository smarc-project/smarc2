// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/DVLBeam.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DVL_BEAM__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__DVL_BEAM__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/dvl_beam__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_DVLBeam_pose
{
public:
  explicit Init_DVLBeam_pose(::smarc_msgs::msg::DVLBeam & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::DVLBeam pose(::smarc_msgs::msg::DVLBeam::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::DVLBeam msg_;
};

class Init_DVLBeam_velocity_covariance
{
public:
  explicit Init_DVLBeam_velocity_covariance(::smarc_msgs::msg::DVLBeam & msg)
  : msg_(msg)
  {}
  Init_DVLBeam_pose velocity_covariance(::smarc_msgs::msg::DVLBeam::_velocity_covariance_type arg)
  {
    msg_.velocity_covariance = std::move(arg);
    return Init_DVLBeam_pose(msg_);
  }

private:
  ::smarc_msgs::msg::DVLBeam msg_;
};

class Init_DVLBeam_velocity
{
public:
  explicit Init_DVLBeam_velocity(::smarc_msgs::msg::DVLBeam & msg)
  : msg_(msg)
  {}
  Init_DVLBeam_velocity_covariance velocity(::smarc_msgs::msg::DVLBeam::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_DVLBeam_velocity_covariance(msg_);
  }

private:
  ::smarc_msgs::msg::DVLBeam msg_;
};

class Init_DVLBeam_range_covariance
{
public:
  explicit Init_DVLBeam_range_covariance(::smarc_msgs::msg::DVLBeam & msg)
  : msg_(msg)
  {}
  Init_DVLBeam_velocity range_covariance(::smarc_msgs::msg::DVLBeam::_range_covariance_type arg)
  {
    msg_.range_covariance = std::move(arg);
    return Init_DVLBeam_velocity(msg_);
  }

private:
  ::smarc_msgs::msg::DVLBeam msg_;
};

class Init_DVLBeam_range
{
public:
  Init_DVLBeam_range()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DVLBeam_range_covariance range(::smarc_msgs::msg::DVLBeam::_range_type arg)
  {
    msg_.range = std::move(arg);
    return Init_DVLBeam_range_covariance(msg_);
  }

private:
  ::smarc_msgs::msg::DVLBeam msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::DVLBeam>()
{
  return smarc_msgs::msg::builder::Init_DVLBeam_range();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DVL_BEAM__BUILDER_HPP_
