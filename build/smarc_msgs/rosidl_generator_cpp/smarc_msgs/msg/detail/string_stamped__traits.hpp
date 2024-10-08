// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/StringStamped.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/string_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'time_sent'
// Member 'time_received'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const StringStamped & msg,
  std::ostream & out)
{
  out << "{";
  // member: time_sent
  {
    out << "time_sent: ";
    to_flow_style_yaml(msg.time_sent, out);
    out << ", ";
  }

  // member: time_received
  {
    out << "time_received: ";
    to_flow_style_yaml(msg.time_received, out);
    out << ", ";
  }

  // member: data
  {
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const StringStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: time_sent
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time_sent:\n";
    to_block_style_yaml(msg.time_sent, out, indentation + 2);
  }

  // member: time_received
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time_received:\n";
    to_block_style_yaml(msg.time_received, out, indentation + 2);
  }

  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "data: ";
    rosidl_generator_traits::value_to_yaml(msg.data, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StringStamped & msg, bool use_flow_style = false)
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
  const smarc_msgs::msg::StringStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::StringStamped & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::StringStamped>()
{
  return "smarc_msgs::msg::StringStamped";
}

template<>
inline const char * name<smarc_msgs::msg::StringStamped>()
{
  return "smarc_msgs/msg/StringStamped";
}

template<>
struct has_fixed_size<smarc_msgs::msg::StringStamped>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::msg::StringStamped>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::msg::StringStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_STAMPED__TRAITS_HPP_
