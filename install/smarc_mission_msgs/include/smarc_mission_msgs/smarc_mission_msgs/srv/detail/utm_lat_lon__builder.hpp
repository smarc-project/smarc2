// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:srv/UTMLatLon.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__BUILDER_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/srv/detail/utm_lat_lon__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace srv
{

namespace builder
{

class Init_UTMLatLon_Request_lat_lon_points
{
public:
  explicit Init_UTMLatLon_Request_lat_lon_points(::smarc_mission_msgs::srv::UTMLatLon_Request & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::srv::UTMLatLon_Request lat_lon_points(::smarc_mission_msgs::srv::UTMLatLon_Request::_lat_lon_points_type arg)
  {
    msg_.lat_lon_points = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::srv::UTMLatLon_Request msg_;
};

class Init_UTMLatLon_Request_utm_points
{
public:
  Init_UTMLatLon_Request_utm_points()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_UTMLatLon_Request_lat_lon_points utm_points(::smarc_mission_msgs::srv::UTMLatLon_Request::_utm_points_type arg)
  {
    msg_.utm_points = std::move(arg);
    return Init_UTMLatLon_Request_lat_lon_points(msg_);
  }

private:
  ::smarc_mission_msgs::srv::UTMLatLon_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::srv::UTMLatLon_Request>()
{
  return smarc_mission_msgs::srv::builder::Init_UTMLatLon_Request_utm_points();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace srv
{

namespace builder
{

class Init_UTMLatLon_Response_utm_points
{
public:
  explicit Init_UTMLatLon_Response_utm_points(::smarc_mission_msgs::srv::UTMLatLon_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::srv::UTMLatLon_Response utm_points(::smarc_mission_msgs::srv::UTMLatLon_Response::_utm_points_type arg)
  {
    msg_.utm_points = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::srv::UTMLatLon_Response msg_;
};

class Init_UTMLatLon_Response_lat_lon_points
{
public:
  Init_UTMLatLon_Response_lat_lon_points()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_UTMLatLon_Response_utm_points lat_lon_points(::smarc_mission_msgs::srv::UTMLatLon_Response::_lat_lon_points_type arg)
  {
    msg_.lat_lon_points = std::move(arg);
    return Init_UTMLatLon_Response_utm_points(msg_);
  }

private:
  ::smarc_mission_msgs::srv::UTMLatLon_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::srv::UTMLatLon_Response>()
{
  return smarc_mission_msgs::srv::builder::Init_UTMLatLon_Response_lat_lon_points();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__BUILDER_HPP_
