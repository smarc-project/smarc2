// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/CircuitStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/circuit_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const CircuitStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: error_flags
  {
    out << "error_flags: ";
    rosidl_generator_traits::value_to_yaml(msg.error_flags, out);
    out << ", ";
  }

  // member: circuit_id
  {
    out << "circuit_id: ";
    rosidl_generator_traits::value_to_yaml(msg.circuit_id, out);
    out << ", ";
  }

  // member: voltage
  {
    out << "voltage: ";
    rosidl_generator_traits::value_to_yaml(msg.voltage, out);
    out << ", ";
  }

  // member: current
  {
    out << "current: ";
    rosidl_generator_traits::value_to_yaml(msg.current, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CircuitStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: error_flags
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_flags: ";
    rosidl_generator_traits::value_to_yaml(msg.error_flags, out);
    out << "\n";
  }

  // member: circuit_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "circuit_id: ";
    rosidl_generator_traits::value_to_yaml(msg.circuit_id, out);
    out << "\n";
  }

  // member: voltage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "voltage: ";
    rosidl_generator_traits::value_to_yaml(msg.voltage, out);
    out << "\n";
  }

  // member: current
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current: ";
    rosidl_generator_traits::value_to_yaml(msg.current, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CircuitStatus & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::CircuitStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::CircuitStatus & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::CircuitStatus>()
{
  return "sam_msgs::msg::CircuitStatus";
}

template<>
inline const char * name<sam_msgs::msg::CircuitStatus>()
{
  return "sam_msgs/msg/CircuitStatus";
}

template<>
struct has_fixed_size<sam_msgs::msg::CircuitStatus>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_msgs::msg::CircuitStatus>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_msgs::msg::CircuitStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__TRAITS_HPP_
