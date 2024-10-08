// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_control_msgs:msg/ControlInput.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__TRAITS_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_control_msgs/msg/detail/control_input__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_control_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ControlInput & msg,
  std::ostream & out)
{
  out << "{";
  // member: thrusterrpm
  {
    out << "thrusterrpm: ";
    rosidl_generator_traits::value_to_yaml(msg.thrusterrpm, out);
    out << ", ";
  }

  // member: thrustervertical
  {
    out << "thrustervertical: ";
    rosidl_generator_traits::value_to_yaml(msg.thrustervertical, out);
    out << ", ";
  }

  // member: thrusterhorizontal
  {
    out << "thrusterhorizontal: ";
    rosidl_generator_traits::value_to_yaml(msg.thrusterhorizontal, out);
    out << ", ";
  }

  // member: vbs
  {
    out << "vbs: ";
    rosidl_generator_traits::value_to_yaml(msg.vbs, out);
    out << ", ";
  }

  // member: lcg
  {
    out << "lcg: ";
    rosidl_generator_traits::value_to_yaml(msg.lcg, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ControlInput & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: thrusterrpm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thrusterrpm: ";
    rosidl_generator_traits::value_to_yaml(msg.thrusterrpm, out);
    out << "\n";
  }

  // member: thrustervertical
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thrustervertical: ";
    rosidl_generator_traits::value_to_yaml(msg.thrustervertical, out);
    out << "\n";
  }

  // member: thrusterhorizontal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thrusterhorizontal: ";
    rosidl_generator_traits::value_to_yaml(msg.thrusterhorizontal, out);
    out << "\n";
  }

  // member: vbs
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vbs: ";
    rosidl_generator_traits::value_to_yaml(msg.vbs, out);
    out << "\n";
  }

  // member: lcg
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lcg: ";
    rosidl_generator_traits::value_to_yaml(msg.lcg, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ControlInput & msg, bool use_flow_style = false)
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

}  // namespace smarc_control_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_control_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_control_msgs::msg::ControlInput & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_control_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_control_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_control_msgs::msg::ControlInput & msg)
{
  return smarc_control_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_control_msgs::msg::ControlInput>()
{
  return "smarc_control_msgs::msg::ControlInput";
}

template<>
inline const char * name<smarc_control_msgs::msg::ControlInput>()
{
  return "smarc_control_msgs/msg/ControlInput";
}

template<>
struct has_fixed_size<smarc_control_msgs::msg::ControlInput>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_control_msgs::msg::ControlInput>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_control_msgs::msg::ControlInput>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__TRAITS_HPP_
