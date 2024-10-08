// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/CTP.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CTP__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__CTP__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/ctp__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const CTP & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: conductivity
  {
    out << "conductivity: ";
    rosidl_generator_traits::value_to_yaml(msg.conductivity, out);
    out << ", ";
  }

  // member: temperature
  {
    out << "temperature: ";
    rosidl_generator_traits::value_to_yaml(msg.temperature, out);
    out << ", ";
  }

  // member: pressure
  {
    out << "pressure: ";
    rosidl_generator_traits::value_to_yaml(msg.pressure, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CTP & msg,
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

  // member: conductivity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "conductivity: ";
    rosidl_generator_traits::value_to_yaml(msg.conductivity, out);
    out << "\n";
  }

  // member: temperature
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "temperature: ";
    rosidl_generator_traits::value_to_yaml(msg.temperature, out);
    out << "\n";
  }

  // member: pressure
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pressure: ";
    rosidl_generator_traits::value_to_yaml(msg.pressure, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CTP & msg, bool use_flow_style = false)
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

}  // namespace sam_msgs

namespace rosidl_generator_traits
{

[[deprecated("use sam_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const sam_msgs::msg::CTP & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::CTP & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::CTP>()
{
  return "sam_msgs::msg::CTP";
}

template<>
inline const char * name<sam_msgs::msg::CTP>()
{
  return "sam_msgs/msg/CTP";
}

template<>
struct has_fixed_size<sam_msgs::msg::CTP>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<sam_msgs::msg::CTP>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<sam_msgs::msg::CTP>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__CTP__TRAITS_HPP_
