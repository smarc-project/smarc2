// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:srv/CellOccupied.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__TRAITS_HPP_
#define SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/srv/detail/cell_occupied__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const CellOccupied_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CellOccupied_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CellOccupied_Request & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::CellOccupied_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::CellOccupied_Request & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::CellOccupied_Request>()
{
  return "smarc_msgs::srv::CellOccupied_Request";
}

template<>
inline const char * name<smarc_msgs::srv::CellOccupied_Request>()
{
  return "smarc_msgs/srv/CellOccupied_Request";
}

template<>
struct has_fixed_size<smarc_msgs::srv::CellOccupied_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_msgs::srv::CellOccupied_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_msgs::srv::CellOccupied_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const CellOccupied_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: cost
  {
    out << "cost: ";
    rosidl_generator_traits::value_to_yaml(msg.cost, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CellOccupied_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: cost
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cost: ";
    rosidl_generator_traits::value_to_yaml(msg.cost, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CellOccupied_Response & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::CellOccupied_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::CellOccupied_Response & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::CellOccupied_Response>()
{
  return "smarc_msgs::srv::CellOccupied_Response";
}

template<>
inline const char * name<smarc_msgs::srv::CellOccupied_Response>()
{
  return "smarc_msgs/srv/CellOccupied_Response";
}

template<>
struct has_fixed_size<smarc_msgs::srv::CellOccupied_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_msgs::srv::CellOccupied_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_msgs::srv::CellOccupied_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_msgs::srv::CellOccupied>()
{
  return "smarc_msgs::srv::CellOccupied";
}

template<>
inline const char * name<smarc_msgs::srv::CellOccupied>()
{
  return "smarc_msgs/srv/CellOccupied";
}

template<>
struct has_fixed_size<smarc_msgs::srv::CellOccupied>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_msgs::srv::CellOccupied_Request>::value &&
    has_fixed_size<smarc_msgs::srv::CellOccupied_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_msgs::srv::CellOccupied>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_msgs::srv::CellOccupied_Request>::value &&
    has_bounded_size<smarc_msgs::srv::CellOccupied_Response>::value
  >
{
};

template<>
struct is_service<smarc_msgs::srv::CellOccupied>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_msgs::srv::CellOccupied_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_msgs::srv::CellOccupied_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__TRAITS_HPP_
