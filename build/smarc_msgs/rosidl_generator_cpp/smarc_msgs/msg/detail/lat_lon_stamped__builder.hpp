// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/LatLonStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/lat_lon_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_LatLonStamped_longitude
{
public:
  explicit Init_LatLonStamped_longitude(::smarc_msgs::msg::LatLonStamped & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::LatLonStamped longitude(::smarc_msgs::msg::LatLonStamped::_longitude_type arg)
  {
    msg_.longitude = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonStamped msg_;
};

class Init_LatLonStamped_latitude
{
public:
  explicit Init_LatLonStamped_latitude(::smarc_msgs::msg::LatLonStamped & msg)
  : msg_(msg)
  {}
  Init_LatLonStamped_longitude latitude(::smarc_msgs::msg::LatLonStamped::_latitude_type arg)
  {
    msg_.latitude = std::move(arg);
    return Init_LatLonStamped_longitude(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonStamped msg_;
};

class Init_LatLonStamped_header
{
public:
  Init_LatLonStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_LatLonStamped_latitude header(::smarc_msgs::msg::LatLonStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_LatLonStamped_latitude(msg_);
  }

private:
  ::smarc_msgs::msg::LatLonStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::LatLonStamped>()
{
  return smarc_msgs::msg::builder::Init_LatLonStamped_header();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__BUILDER_HPP_
