// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/uavcan_node_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const UavcanNodeStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: uptime_sec
  {
    out << "uptime_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.uptime_sec, out);
    out << ", ";
  }

  // member: health
  {
    out << "health: ";
    rosidl_generator_traits::value_to_yaml(msg.health, out);
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: sub_mode
  {
    out << "sub_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.sub_mode, out);
    out << ", ";
  }

  // member: vendor_specific_status_code
  {
    out << "vendor_specific_status_code: ";
    rosidl_generator_traits::value_to_yaml(msg.vendor_specific_status_code, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UavcanNodeStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: uptime_sec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "uptime_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.uptime_sec, out);
    out << "\n";
  }

  // member: health
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "health: ";
    rosidl_generator_traits::value_to_yaml(msg.health, out);
    out << "\n";
  }

  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }

  // member: sub_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "sub_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.sub_mode, out);
    out << "\n";
  }

  // member: vendor_specific_status_code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vendor_specific_status_code: ";
    rosidl_generator_traits::value_to_yaml(msg.vendor_specific_status_code, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UavcanNodeStatus & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::UavcanNodeStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::UavcanNodeStatus & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::UavcanNodeStatus>()
{
  return "sam_msgs::msg::UavcanNodeStatus";
}

template<>
inline const char * name<sam_msgs::msg::UavcanNodeStatus>()
{
  return "sam_msgs/msg/UavcanNodeStatus";
}

template<>
struct has_fixed_size<sam_msgs::msg::UavcanNodeStatus>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_msgs::msg::UavcanNodeStatus>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_msgs::msg::UavcanNodeStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__TRAITS_HPP_
