// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__TRAITS_HPP_
#define SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'lat_lon_odom'
#include "smarc_msgs/msg/detail/lat_lon_odometry__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const LatLonToUTMOdometry_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: lat_lon_odom
  {
    out << "lat_lon_odom: ";
    to_flow_style_yaml(msg.lat_lon_odom, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const LatLonToUTMOdometry_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: lat_lon_odom
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lat_lon_odom:\n";
    to_block_style_yaml(msg.lat_lon_odom, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const LatLonToUTMOdometry_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::srv::LatLonToUTMOdometry_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::LatLonToUTMOdometry_Request & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::LatLonToUTMOdometry_Request>()
{
  return "smarc_msgs::srv::LatLonToUTMOdometry_Request";
}

template<>
inline const char * name<smarc_msgs::srv::LatLonToUTMOdometry_Request>()
{
  return "smarc_msgs/srv/LatLonToUTMOdometry_Request";
}

template<>
struct has_fixed_size<smarc_msgs::srv::LatLonToUTMOdometry_Request>
  : std::integral_constant<bool, has_fixed_size<smarc_msgs::msg::LatLonOdometry>::value> {};

template<>
struct has_bounded_size<smarc_msgs::srv::LatLonToUTMOdometry_Request>
  : std::integral_constant<bool, has_bounded_size<smarc_msgs::msg::LatLonOdometry>::value> {};

template<>
struct is_message<smarc_msgs::srv::LatLonToUTMOdometry_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'odom'
#include "nav_msgs/msg/detail/odometry__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const LatLonToUTMOdometry_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: odom
  {
    out << "odom: ";
    to_flow_style_yaml(msg.odom, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const LatLonToUTMOdometry_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: odom
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "odom:\n";
    to_block_style_yaml(msg.odom, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const LatLonToUTMOdometry_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::srv::LatLonToUTMOdometry_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::LatLonToUTMOdometry_Response & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::LatLonToUTMOdometry_Response>()
{
  return "smarc_msgs::srv::LatLonToUTMOdometry_Response";
}

template<>
inline const char * name<smarc_msgs::srv::LatLonToUTMOdometry_Response>()
{
  return "smarc_msgs/srv/LatLonToUTMOdometry_Response";
}

template<>
struct has_fixed_size<smarc_msgs::srv::LatLonToUTMOdometry_Response>
  : std::integral_constant<bool, has_fixed_size<nav_msgs::msg::Odometry>::value> {};

template<>
struct has_bounded_size<smarc_msgs::srv::LatLonToUTMOdometry_Response>
  : std::integral_constant<bool, has_bounded_size<nav_msgs::msg::Odometry>::value> {};

template<>
struct is_message<smarc_msgs::srv::LatLonToUTMOdometry_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_msgs::srv::LatLonToUTMOdometry>()
{
  return "smarc_msgs::srv::LatLonToUTMOdometry";
}

template<>
inline const char * name<smarc_msgs::srv::LatLonToUTMOdometry>()
{
  return "smarc_msgs/srv/LatLonToUTMOdometry";
}

template<>
struct has_fixed_size<smarc_msgs::srv::LatLonToUTMOdometry>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_msgs::srv::LatLonToUTMOdometry_Request>::value &&
    has_fixed_size<smarc_msgs::srv::LatLonToUTMOdometry_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_msgs::srv::LatLonToUTMOdometry>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_msgs::srv::LatLonToUTMOdometry_Request>::value &&
    has_bounded_size<smarc_msgs::srv::LatLonToUTMOdometry_Response>::value
  >
{
};

template<>
struct is_service<smarc_msgs::srv::LatLonToUTMOdometry>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_msgs::srv::LatLonToUTMOdometry_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_msgs::srv::LatLonToUTMOdometry_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__TRAITS_HPP_
