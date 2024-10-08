// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:srv/NEDENURotation.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__TRAITS_HPP_
#define SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/srv/detail/nedenu_rotation__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'orientation'
#include "geometry_msgs/msg/detail/quaternion__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const NEDENURotation_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: orientation
  {
    out << "orientation: ";
    to_flow_style_yaml(msg.orientation, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const NEDENURotation_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: orientation
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "orientation:\n";
    to_block_style_yaml(msg.orientation, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const NEDENURotation_Request & msg, bool use_flow_style = false)
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

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::srv::NEDENURotation_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::NEDENURotation_Request & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::NEDENURotation_Request>()
{
  return "smarc_msgs::srv::NEDENURotation_Request";
}

template<>
inline const char * name<smarc_msgs::srv::NEDENURotation_Request>()
{
  return "smarc_msgs/srv/NEDENURotation_Request";
}

template<>
struct has_fixed_size<smarc_msgs::srv::NEDENURotation_Request>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Quaternion>::value> {};

template<>
struct has_bounded_size<smarc_msgs::srv::NEDENURotation_Request>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Quaternion>::value> {};

template<>
struct is_message<smarc_msgs::srv::NEDENURotation_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'orientation'
// already included above
// #include "geometry_msgs/msg/detail/quaternion__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const NEDENURotation_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: orientation
  {
    out << "orientation: ";
    to_flow_style_yaml(msg.orientation, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const NEDENURotation_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: orientation
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "orientation:\n";
    to_block_style_yaml(msg.orientation, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const NEDENURotation_Response & msg, bool use_flow_style = false)
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

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::srv::NEDENURotation_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::NEDENURotation_Response & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::NEDENURotation_Response>()
{
  return "smarc_msgs::srv::NEDENURotation_Response";
}

template<>
inline const char * name<smarc_msgs::srv::NEDENURotation_Response>()
{
  return "smarc_msgs/srv/NEDENURotation_Response";
}

template<>
struct has_fixed_size<smarc_msgs::srv::NEDENURotation_Response>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Quaternion>::value> {};

template<>
struct has_bounded_size<smarc_msgs::srv::NEDENURotation_Response>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Quaternion>::value> {};

template<>
struct is_message<smarc_msgs::srv::NEDENURotation_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_msgs::srv::NEDENURotation>()
{
  return "smarc_msgs::srv::NEDENURotation";
}

template<>
inline const char * name<smarc_msgs::srv::NEDENURotation>()
{
  return "smarc_msgs/srv/NEDENURotation";
}

template<>
struct has_fixed_size<smarc_msgs::srv::NEDENURotation>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_msgs::srv::NEDENURotation_Request>::value &&
    has_fixed_size<smarc_msgs::srv::NEDENURotation_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_msgs::srv::NEDENURotation>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_msgs::srv::NEDENURotation_Request>::value &&
    has_bounded_size<smarc_msgs::srv::NEDENURotation_Response>::value
  >
{
};

template<>
struct is_service<smarc_msgs::srv::NEDENURotation>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_msgs::srv::NEDENURotation_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_msgs::srv::NEDENURotation_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__SRV__DETAIL__NEDENU_ROTATION__TRAITS_HPP_
