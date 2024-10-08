// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/BallastAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/ballast_angles__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const BallastAngles & msg,
  std::ostream & out)
{
  out << "{";
  // member: weight_1_offset_radians
  {
    out << "weight_1_offset_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.weight_1_offset_radians, out);
    out << ", ";
  }

  // member: weight_2_offset_radians
  {
    out << "weight_2_offset_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.weight_2_offset_radians, out);
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
  const BallastAngles & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: weight_1_offset_radians
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "weight_1_offset_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.weight_1_offset_radians, out);
    out << "\n";
  }

  // member: weight_2_offset_radians
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "weight_2_offset_radians: ";
    rosidl_generator_traits::value_to_yaml(msg.weight_2_offset_radians, out);
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

inline std::string to_yaml(const BallastAngles & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::BallastAngles & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::BallastAngles & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::BallastAngles>()
{
  return "sam_msgs::msg::BallastAngles";
}

template<>
inline const char * name<sam_msgs::msg::BallastAngles>()
{
  return "sam_msgs/msg/BallastAngles";
}

template<>
struct has_fixed_size<sam_msgs::msg::BallastAngles>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<sam_msgs::msg::BallastAngles>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<sam_msgs::msg::BallastAngles>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__TRAITS_HPP_
