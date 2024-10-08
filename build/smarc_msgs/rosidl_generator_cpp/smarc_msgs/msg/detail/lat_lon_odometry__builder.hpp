// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/lat_lon_odometry__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_LatLonOdometry_twist
{
public:
  explicit Init_LatLonOdometry_twist(::smarc_msgs::msg::LatLonOdometry & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::LatLonOdometry twist(::smarc_msgs::msg::LatLonOdometry::_twist_type arg)
  {
    msg_.twist = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonOdometry msg_;
};

class Init_LatLonOdometry_covariance
{
public:
  explicit Init_LatLonOdometry_covariance(::smarc_msgs::msg::LatLonOdometry & msg)
  : msg_(msg)
  {}
  Init_LatLonOdometry_twist covariance(::smarc_msgs::msg::LatLonOdometry::_covariance_type arg)
  {
    msg_.covariance = std::move(arg);
    return Init_LatLonOdometry_twist(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonOdometry msg_;
};

class Init_LatLonOdometry_lat_lon_pose
{
public:
  explicit Init_LatLonOdometry_lat_lon_pose(::smarc_msgs::msg::LatLonOdometry & msg)
  : msg_(msg)
  {}
  Init_LatLonOdometry_covariance lat_lon_pose(::smarc_msgs::msg::LatLonOdometry::_lat_lon_pose_type arg)
  {
    msg_.lat_lon_pose = std::move(arg);
    return Init_LatLonOdometry_covariance(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonOdometry msg_;
};

class Init_LatLonOdometry_header
{
public:
  Init_LatLonOdometry_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_LatLonOdometry_lat_lon_pose header(::smarc_msgs::msg::LatLonOdometry::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_LatLonOdometry_lat_lon_pose(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonOdometry msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::LatLonOdometry>()
{
  return smarc_msgs::msg::builder::Init_LatLonOdometry_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__BUILDER_HPP_
