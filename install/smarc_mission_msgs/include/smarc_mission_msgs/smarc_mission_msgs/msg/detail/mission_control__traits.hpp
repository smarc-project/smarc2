// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__TRAITS_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_mission_msgs/msg/detail/mission_control__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'waypoints'
#include "smarc_mission_msgs/msg/detail/goto_waypoint__traits.hpp"

namespace smarc_mission_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const MissionControl & msg,
  std::ostream & out)
{
  out << "{";
  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: hash
  {
    out << "hash: ";
    rosidl_generator_traits::value_to_yaml(msg.hash, out);
    out << ", ";
  }

  // member: timeout
  {
    out << "timeout: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout, out);
    out << ", ";
  }

  // member: command
  {
    out << "command: ";
    rosidl_generator_traits::value_to_yaml(msg.command, out);
    out << ", ";
  }

  // member: plan_state
  {
    out << "plan_state: ";
    rosidl_generator_traits::value_to_yaml(msg.plan_state, out);
    out << ", ";
  }

  // member: feedback_str
  {
    out << "feedback_str: ";
    rosidl_generator_traits::value_to_yaml(msg.feedback_str, out);
    out << ", ";
  }

  // member: waypoints
  {
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []";
    } else {
      out << "waypoints: [";
      size_t pending_items = msg.waypoints.size();
      for (auto item : msg.waypoints) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MissionControl & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: hash
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "hash: ";
    rosidl_generator_traits::value_to_yaml(msg.hash, out);
    out << "\n";
  }

  // member: timeout
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timeout: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout, out);
    out << "\n";
  }

  // member: command
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "command: ";
    rosidl_generator_traits::value_to_yaml(msg.command, out);
    out << "\n";
  }

  // member: plan_state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "plan_state: ";
    rosidl_generator_traits::value_to_yaml(msg.plan_state, out);
    out << "\n";
  }

  // member: feedback_str
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedback_str: ";
    rosidl_generator_traits::value_to_yaml(msg.feedback_str, out);
    out << "\n";
  }

  // member: waypoints
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []\n";
    } else {
      out << "waypoints:\n";
      for (auto item : msg.waypoints) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MissionControl & msg, bool use_flow_style = false)
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
  const smarc_mission_msgs::msg::MissionControl & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::msg::MissionControl & msg)
{
  return smarc_mission_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::msg::MissionControl>()
{
  return "smarc_mission_msgs::msg::MissionControl";
}

template<>
inline const char * name<smarc_mission_msgs::msg::MissionControl>()
{
  return "smarc_mission_msgs/msg/MissionControl";
}

template<>
struct has_fixed_size<smarc_mission_msgs::msg::MissionControl>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::msg::MissionControl>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::msg::MissionControl>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__TRAITS_HPP_
