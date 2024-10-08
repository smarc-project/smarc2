// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_control_msgs:msg/ControlState.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__TRAITS_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_control_msgs/msg/detail/control_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
// Member 'vel'
#include "smarc_control_msgs/msg/detail/state__traits.hpp"

namespace smarc_control_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ControlState & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

  // member: vel
  {
    out << "vel: ";
    to_flow_style_yaml(msg.vel, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ControlState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }

  // member: vel
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vel:\n";
    to_block_style_yaml(msg.vel, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ControlState & msg, bool use_flow_style = false)
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
  const smarc_control_msgs::msg::ControlState & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_control_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_control_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_control_msgs::msg::ControlState & msg)
{
  return smarc_control_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_control_msgs::msg::ControlState>()
{
  return "smarc_control_msgs::msg::ControlState";
}

template<>
inline const char * name<smarc_control_msgs::msg::ControlState>()
{
  return "smarc_control_msgs/msg/ControlState";
}

template<>
struct has_fixed_size<smarc_control_msgs::msg::ControlState>
  : std::integral_constant<bool, has_fixed_size<smarc_control_msgs::msg::State>::value> {};

template<>
struct has_bounded_size<smarc_control_msgs::msg::ControlState>
  : std::integral_constant<bool, has_bounded_size<smarc_control_msgs::msg::State>::value> {};

template<>
struct is_message<smarc_control_msgs::msg::ControlState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__TRAITS_HPP_
