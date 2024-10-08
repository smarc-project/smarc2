// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_mission_msgs:msg/BTCommand.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__TRAITS_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_mission_msgs/msg/detail/bt_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_mission_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const BTCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: msg_type
  {
    out << "msg_type: ";
    rosidl_generator_traits::value_to_yaml(msg.msg_type, out);
    out << ", ";
  }

  // member: cmd_json
  {
    out << "cmd_json: ";
    rosidl_generator_traits::value_to_yaml(msg.cmd_json, out);
    out << ", ";
  }

  // member: fb_json
  {
    out << "fb_json: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_json, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const BTCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: msg_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "msg_type: ";
    rosidl_generator_traits::value_to_yaml(msg.msg_type, out);
    out << "\n";
  }

  // member: cmd_json
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cmd_json: ";
    rosidl_generator_traits::value_to_yaml(msg.cmd_json, out);
    out << "\n";
  }

  // member: fb_json
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_json: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_json, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const BTCommand & msg, bool use_flow_style = false)
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

}  // namespace smarc_mission_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_mission_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_mission_msgs::msg::BTCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::msg::BTCommand & msg)
{
  return smarc_mission_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::msg::BTCommand>()
{
  return "smarc_mission_msgs::msg::BTCommand";
}

template<>
inline const char * name<smarc_mission_msgs::msg::BTCommand>()
{
  return "smarc_mission_msgs/msg/BTCommand";
}

template<>
struct has_fixed_size<smarc_mission_msgs::msg::BTCommand>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::msg::BTCommand>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::msg::BTCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__TRAITS_HPP_
