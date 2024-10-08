// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__BUILDER_HPP_
#define SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_LatLonToUTMOdometry_Request_lat_lon_odom
{
public:
  Init_LatLonToUTMOdometry_Request_lat_lon_odom()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::LatLonToUTMOdometry_Request lat_lon_odom(::smarc_msgs::srv::LatLonToUTMOdometry_Request::_lat_lon_odom_type arg)
  {
    msg_.lat_lon_odom = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::LatLonToUTMOdometry_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::LatLonToUTMOdometry_Request>()
{
  return smarc_msgs::srv::builder::Init_LatLonToUTMOdometry_Request_lat_lon_odom();
}

}  // namespace smarc_msgs


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_LatLonToUTMOdometry_Response_odom
{
public:
  Init_LatLonToUTMOdometry_Response_odom()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::LatLonToUTMOdometry_Response odom(::smarc_msgs::srv::LatLonToUTMOdometry_Response::_odom_type arg)
  {
    msg_.odom = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::LatLonToUTMOdometry_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::LatLonToUTMOdometry_Response>()
{
  return smarc_msgs::srv::builder::Init_LatLonToUTMOdometry_Response_odom();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__BUILDER_HPP_
