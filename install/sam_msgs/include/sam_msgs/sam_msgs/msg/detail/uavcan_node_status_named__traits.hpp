// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'ns'
#include "sam_msgs/msg/detail/uavcan_node_status__traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const UavcanNodeStatusNamed & msg,
  std::ostream & out)
{
  out << "{";
  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: ns
  {
    out << "ns: ";
    to_flow_style_yaml(msg.ns, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UavcanNodeStatusNamed & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << "\n";
  }

  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: ns
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ns:\n";
    to_block_style_yaml(msg.ns, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UavcanNodeStatusNamed & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::UavcanNodeStatusNamed & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::UavcanNodeStatusNamed & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::UavcanNodeStatusNamed>()
{
  return "sam_msgs::msg::UavcanNodeStatusNamed";
}

template<>
inline const char * name<sam_msgs::msg::UavcanNodeStatusNamed>()
{
  return "sam_msgs/msg/UavcanNodeStatusNamed";
}

template<>
struct has_fixed_size<sam_msgs::msg::UavcanNodeStatusNamed>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<sam_msgs::msg::UavcanNodeStatusNamed>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<sam_msgs::msg::UavcanNodeStatusNamed>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__TRAITS_HPP_
