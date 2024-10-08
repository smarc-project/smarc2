// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/DualThrusterRPM.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/dual_thruster_rpm__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'thruster_front'
// Member 'thruster_back'
#include "smarc_msgs/msg/detail/thruster_rpm__traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const DualThrusterRPM & msg,
  std::ostream & out)
{
  out << "{";
  // member: thruster_front
  {
    out << "thruster_front: ";
    to_flow_style_yaml(msg.thruster_front, out);
    out << ", ";
  }

  // member: thruster_back
  {
    out << "thruster_back: ";
    to_flow_style_yaml(msg.thruster_back, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DualThrusterRPM & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: thruster_front
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thruster_front:\n";
    to_block_style_yaml(msg.thruster_front, out, indentation + 2);
  }

  // member: thruster_back
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thruster_back:\n";
    to_block_style_yaml(msg.thruster_back, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DualThrusterRPM & msg, bool use_flow_style = false)
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
  const smarc_msgs::msg::DualThrusterRPM & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::DualThrusterRPM & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::DualThrusterRPM>()
{
  return "smarc_msgs::msg::DualThrusterRPM";
}

template<>
inline const char * name<smarc_msgs::msg::DualThrusterRPM>()
{
  return "smarc_msgs/msg/DualThrusterRPM";
}

template<>
struct has_fixed_size<smarc_msgs::msg::DualThrusterRPM>
  : std::integral_constant<bool, has_fixed_size<smarc_msgs::msg::ThrusterRPM>::value> {};

template<>
struct has_bounded_size<smarc_msgs::msg::DualThrusterRPM>
  : std::integral_constant<bool, has_bounded_size<smarc_msgs::msg::ThrusterRPM>::value> {};

template<>
struct is_message<smarc_msgs::msg::DualThrusterRPM>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_RPM__TRAITS_HPP_
