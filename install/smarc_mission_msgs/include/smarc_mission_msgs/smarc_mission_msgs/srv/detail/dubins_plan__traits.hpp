// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__TRAITS_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_mission_msgs/srv/detail/dubins_plan__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'waypoints'
#include "geometry_msgs/msg/detail/pose2_d__traits.hpp"

namespace smarc_mission_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const DubinsPlan_Request & msg,
  std::ostream & out)
{
  out << "{";
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
    out << ", ";
  }

  // member: step
  {
    out << "step: ";
    rosidl_generator_traits::value_to_yaml(msg.step, out);
    out << ", ";
  }

  // member: turning_radius
  {
    out << "turning_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.turning_radius, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DubinsPlan_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
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

  // member: step
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "step: ";
    rosidl_generator_traits::value_to_yaml(msg.step, out);
    out << "\n";
  }

  // member: turning_radius
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "turning_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.turning_radius, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DubinsPlan_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_mission_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_mission_msgs::srv::DubinsPlan_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::srv::DubinsPlan_Request & msg)
{
  return smarc_mission_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::srv::DubinsPlan_Request>()
{
  return "smarc_mission_msgs::srv::DubinsPlan_Request";
}

template<>
inline const char * name<smarc_mission_msgs::srv::DubinsPlan_Request>()
{
  return "smarc_mission_msgs/srv/DubinsPlan_Request";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::DubinsPlan_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::DubinsPlan_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::srv::DubinsPlan_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'waypoints'
// already included above
// #include "geometry_msgs/msg/detail/pose2_d__traits.hpp"

namespace smarc_mission_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const DubinsPlan_Response & msg,
  std::ostream & out)
{
  out << "{";
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
    out << ", ";
  }

  // member: original_wp_indices
  {
    if (msg.original_wp_indices.size() == 0) {
      out << "original_wp_indices: []";
    } else {
      out << "original_wp_indices: [";
      size_t pending_items = msg.original_wp_indices.size();
      for (auto item : msg.original_wp_indices) {
        rosidl_generator_traits::value_to_yaml(item, out);
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
  const DubinsPlan_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
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

  // member: original_wp_indices
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.original_wp_indices.size() == 0) {
      out << "original_wp_indices: []\n";
    } else {
      out << "original_wp_indices:\n";
      for (auto item : msg.original_wp_indices) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DubinsPlan_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_mission_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_mission_msgs::srv::DubinsPlan_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::srv::DubinsPlan_Response & msg)
{
  return smarc_mission_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::srv::DubinsPlan_Response>()
{
  return "smarc_mission_msgs::srv::DubinsPlan_Response";
}

template<>
inline const char * name<smarc_mission_msgs::srv::DubinsPlan_Response>()
{
  return "smarc_mission_msgs/srv/DubinsPlan_Response";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::DubinsPlan_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::DubinsPlan_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::srv::DubinsPlan_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_mission_msgs::srv::DubinsPlan>()
{
  return "smarc_mission_msgs::srv::DubinsPlan";
}

template<>
inline const char * name<smarc_mission_msgs::srv::DubinsPlan>()
{
  return "smarc_mission_msgs/srv/DubinsPlan";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::DubinsPlan>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_mission_msgs::srv::DubinsPlan_Request>::value &&
    has_fixed_size<smarc_mission_msgs::srv::DubinsPlan_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::DubinsPlan>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_mission_msgs::srv::DubinsPlan_Request>::value &&
    has_bounded_size<smarc_mission_msgs::srv::DubinsPlan_Response>::value
  >
{
};

template<>
struct is_service<smarc_mission_msgs::srv::DubinsPlan>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_mission_msgs::srv::DubinsPlan_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_mission_msgs::srv::DubinsPlan_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__TRAITS_HPP_
