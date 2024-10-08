// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/ControllerStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/controller_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ControllerStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: control_status
  {
    out << "control_status: ";
    rosidl_generator_traits::value_to_yaml(msg.control_status, out);
    out << ", ";
  }

  // member: service_name
  {
    out << "service_name: ";
    rosidl_generator_traits::value_to_yaml(msg.service_name, out);
    out << ", ";
  }

  // member: diagnostics_message
  {
    out << "diagnostics_message: ";
    rosidl_generator_traits::value_to_yaml(msg.diagnostics_message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ControllerStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: control_status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "control_status: ";
    rosidl_generator_traits::value_to_yaml(msg.control_status, out);
    out << "\n";
  }

  // member: service_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "service_name: ";
    rosidl_generator_traits::value_to_yaml(msg.service_name, out);
    out << "\n";
  }

  // member: diagnostics_message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "diagnostics_message: ";
    rosidl_generator_traits::value_to_yaml(msg.diagnostics_message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ControllerStatus & msg, bool use_flow_style = false)
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
  const smarc_msgs::msg::ControllerStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::ControllerStatus & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::ControllerStatus>()
{
  return "smarc_msgs::msg::ControllerStatus";
}

template<>
inline const char * name<smarc_msgs::msg::ControllerStatus>()
{
  return "smarc_msgs/msg/ControllerStatus";
}

template<>
struct has_fixed_size<smarc_msgs::msg::ControllerStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::msg::ControllerStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::msg::ControllerStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__TRAITS_HPP_
