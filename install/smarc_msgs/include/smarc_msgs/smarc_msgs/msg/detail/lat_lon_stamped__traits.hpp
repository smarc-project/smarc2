// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/LatLonStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/lat_lon_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const LatLonStamped & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: latitude
  {
    out << "latitude: ";
    rosidl_generator_traits::value_to_yaml(msg.latitude, out);
    out << ", ";
  }

  // member: longitude
  {
    out << "longitude: ";
    rosidl_generator_traits::value_to_yaml(msg.longitude, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const LatLonStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: latitude
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "latitude: ";
    rosidl_generator_traits::value_to_yaml(msg.latitude, out);
    out << "\n";
  }

  // member: longitude
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "longitude: ";
    rosidl_generator_traits::value_to_yaml(msg.longitude, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const LatLonStamped & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::msg::LatLonStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::LatLonStamped & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::LatLonStamped>()
{
  return "smarc_msgs::msg::LatLonStamped";
}

template<>
inline const char * name<smarc_msgs::msg::LatLonStamped>()
{
  return "smarc_msgs/msg/LatLonStamped";
}

template<>
struct has_fixed_size<smarc_msgs::msg::LatLonStamped>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<smarc_msgs::msg::LatLonStamped>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<smarc_msgs::msg::LatLonStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_STAMPED__TRAITS_HPP_
