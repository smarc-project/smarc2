// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_control_msgs:msg/ControlError.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__TRAITS_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_control_msgs/msg/detail/control_error__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_control_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ControlError & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: roll
  {
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << ", ";
  }

  // member: pitch
  {
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << ", ";
  }

  // member: yaw
  {
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
    out << ", ";
  }

  // member: heading
  {
    out << "heading: ";
    rosidl_generator_traits::value_to_yaml(msg.heading, out);
    out << ", ";
  }

  // member: distance
  {
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ControlError & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: roll
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << "\n";
  }

  // member: pitch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << "\n";
  }

  // member: yaw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
    out << "\n";
  }

  // member: heading
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "heading: ";
    rosidl_generator_traits::value_to_yaml(msg.heading, out);
    out << "\n";
  }

  // member: distance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ControlError & msg, bool use_flow_style = false)
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
  const smarc_control_msgs::msg::ControlError & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_control_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_control_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_control_msgs::msg::ControlError & msg)
{
  return smarc_control_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_control_msgs::msg::ControlError>()
{
  return "smarc_control_msgs::msg::ControlError";
}

template<>
inline const char * name<smarc_control_msgs::msg::ControlError>()
{
  return "smarc_control_msgs/msg/ControlError";
}

template<>
struct has_fixed_size<smarc_control_msgs::msg::ControlError>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_control_msgs::msg::ControlError>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_control_msgs::msg::ControlError>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__TRAITS_HPP_
