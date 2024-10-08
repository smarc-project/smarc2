// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__TRAITS_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace smarc_mission_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const GotoWaypoint & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

  // member: goal_tolerance
  {
    out << "goal_tolerance: ";
    rosidl_generator_traits::value_to_yaml(msg.goal_tolerance, out);
    out << ", ";
  }

  // member: z_control_mode
  {
    out << "z_control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.z_control_mode, out);
    out << ", ";
  }

  // member: travel_altitude
  {
    out << "travel_altitude: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_altitude, out);
    out << ", ";
  }

  // member: travel_depth
  {
    out << "travel_depth: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_depth, out);
    out << ", ";
  }

  // member: speed_control_mode
  {
    out << "speed_control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.speed_control_mode, out);
    out << ", ";
  }

  // member: travel_rpm
  {
    out << "travel_rpm: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_rpm, out);
    out << ", ";
  }

  // member: travel_speed
  {
    out << "travel_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_speed, out);
    out << ", ";
  }

  // member: lat
  {
    out << "lat: ";
    rosidl_generator_traits::value_to_yaml(msg.lat, out);
    out << ", ";
  }

  // member: lon
  {
    out << "lon: ";
    rosidl_generator_traits::value_to_yaml(msg.lon, out);
    out << ", ";
  }

  // member: arrival_heading
  {
    out << "arrival_heading: ";
    rosidl_generator_traits::value_to_yaml(msg.arrival_heading, out);
    out << ", ";
  }

  // member: use_heading
  {
    out << "use_heading: ";
    rosidl_generator_traits::value_to_yaml(msg.use_heading, out);
    out << ", ";
  }

  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GotoWaypoint & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }

  // member: goal_tolerance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_tolerance: ";
    rosidl_generator_traits::value_to_yaml(msg.goal_tolerance, out);
    out << "\n";
  }

  // member: z_control_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z_control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.z_control_mode, out);
    out << "\n";
  }

  // member: travel_altitude
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "travel_altitude: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_altitude, out);
    out << "\n";
  }

  // member: travel_depth
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "travel_depth: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_depth, out);
    out << "\n";
  }

  // member: speed_control_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "speed_control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.speed_control_mode, out);
    out << "\n";
  }

  // member: travel_rpm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "travel_rpm: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_rpm, out);
    out << "\n";
  }

  // member: travel_speed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "travel_speed: ";
    rosidl_generator_traits::value_to_yaml(msg.travel_speed, out);
    out << "\n";
  }

  // member: lat
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lat: ";
    rosidl_generator_traits::value_to_yaml(msg.lat, out);
    out << "\n";
  }

  // member: lon
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lon: ";
    rosidl_generator_traits::value_to_yaml(msg.lon, out);
    out << "\n";
  }

  // member: arrival_heading
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "arrival_heading: ";
    rosidl_generator_traits::value_to_yaml(msg.arrival_heading, out);
    out << "\n";
  }

  // member: use_heading
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "use_heading: ";
    rosidl_generator_traits::value_to_yaml(msg.use_heading, out);
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GotoWaypoint & msg, bool use_flow_style = false)
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
  const smarc_mission_msgs::msg::GotoWaypoint & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::msg::GotoWaypoint & msg)
{
  return smarc_mission_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::msg::GotoWaypoint>()
{
  return "smarc_mission_msgs::msg::GotoWaypoint";
}

template<>
inline const char * name<smarc_mission_msgs::msg::GotoWaypoint>()
{
  return "smarc_mission_msgs/msg/GotoWaypoint";
}

template<>
struct has_fixed_size<smarc_mission_msgs::msg::GotoWaypoint>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::msg::GotoWaypoint>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::msg::GotoWaypoint>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__TRAITS_HPP_
