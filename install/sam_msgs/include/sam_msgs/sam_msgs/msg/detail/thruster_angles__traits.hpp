// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/ThrusterAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/thruster_angles__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ThrusterAngles & msg,
  std::ostream & out)
{
  out << "{";
  // member: thruster_vertical_radians
  {
    out << "thruster_vertical_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.thruster_vertical_radians, out);
    out << ", ";
  }

  // member: thruster_horizontal_radians
  {
    out << "thruster_horizontal_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.thruster_horizontal_radians, out);
    out << ", ";
  }

  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ThrusterAngles & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: thruster_vertical_radians
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thruster_vertical_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.thruster_vertical_radians, out);
    out << "\n";
  }

  // member: thruster_horizontal_radians
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thruster_horizontal_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.thruster_horizontal_radians, out);
    out << "\n";
  }

  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ThrusterAngles & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::ThrusterAngles & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::ThrusterAngles & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::ThrusterAngles>()
{
  return "sam_msgs::msg::ThrusterAngles";
}

template<>
inline const char * name<sam_msgs::msg::ThrusterAngles>()
{
  return "sam_msgs/msg/ThrusterAngles";
}

template<>
struct has_fixed_size<sam_msgs::msg::ThrusterAngles>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<sam_msgs::msg::ThrusterAngles>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<sam_msgs::msg::ThrusterAngles>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__TRAITS_HPP_
