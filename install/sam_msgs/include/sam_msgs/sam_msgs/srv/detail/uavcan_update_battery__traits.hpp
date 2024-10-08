// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__TRAITS_HPP_
#define SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/srv/detail/uavcan_update_battery__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace sam_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const UavcanUpdateBattery_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: node_id
  {
    out << "node_id: ";
    rosidl_generator_traits::value_to_yaml(msg.node_id, out);
    out << ", ";
  }

  // member: command
  {
    out << "command: ";
    rosidl_generator_traits::value_to_yaml(msg.command, out);
    out << ", ";
  }

  // member: charge
  {
    out << "charge: ";
    rosidl_generator_traits::value_to_yaml(msg.charge, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UavcanUpdateBattery_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: node_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "node_id: ";
    rosidl_generator_traits::value_to_yaml(msg.node_id, out);
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

  // member: charge
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "charge: ";
    rosidl_generator_traits::value_to_yaml(msg.charge, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UavcanUpdateBattery_Request & msg, bool use_flow_style = false)
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

}  // namespace sam_msgs

namespace rosidl_generator_traits
{

[[deprecated("use sam_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const sam_msgs::srv::UavcanUpdateBattery_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::srv::UavcanUpdateBattery_Request & msg)
{
  return sam_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::srv::UavcanUpdateBattery_Request>()
{
  return "sam_msgs::srv::UavcanUpdateBattery_Request";
}

template<>
inline const char * name<sam_msgs::srv::UavcanUpdateBattery_Request>()
{
  return "sam_msgs/srv/UavcanUpdateBattery_Request";
}

template<>
struct has_fixed_size<sam_msgs::srv::UavcanUpdateBattery_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_msgs::srv::UavcanUpdateBattery_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_msgs::srv::UavcanUpdateBattery_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace sam_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const UavcanUpdateBattery_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UavcanUpdateBattery_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UavcanUpdateBattery_Response & msg, bool use_flow_style = false)
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

}  // namespace sam_msgs

namespace rosidl_generator_traits
{

[[deprecated("use sam_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const sam_msgs::srv::UavcanUpdateBattery_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::srv::UavcanUpdateBattery_Response & msg)
{
  return sam_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::srv::UavcanUpdateBattery_Response>()
{
  return "sam_msgs::srv::UavcanUpdateBattery_Response";
}

template<>
inline const char * name<sam_msgs::srv::UavcanUpdateBattery_Response>()
{
  return "sam_msgs/srv/UavcanUpdateBattery_Response";
}

template<>
struct has_fixed_size<sam_msgs::srv::UavcanUpdateBattery_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_msgs::srv::UavcanUpdateBattery_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_msgs::srv::UavcanUpdateBattery_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<sam_msgs::srv::UavcanUpdateBattery>()
{
  return "sam_msgs::srv::UavcanUpdateBattery";
}

template<>
inline const char * name<sam_msgs::srv::UavcanUpdateBattery>()
{
  return "sam_msgs/srv/UavcanUpdateBattery";
}

template<>
struct has_fixed_size<sam_msgs::srv::UavcanUpdateBattery>
  : std::integral_constant<
    bool,
    has_fixed_size<sam_msgs::srv::UavcanUpdateBattery_Request>::value &&
    has_fixed_size<sam_msgs::srv::UavcanUpdateBattery_Response>::value
  >
{
};

template<>
struct has_bounded_size<sam_msgs::srv::UavcanUpdateBattery>
  : std::integral_constant<
    bool,
    has_bounded_size<sam_msgs::srv::UavcanUpdateBattery_Request>::value &&
    has_bounded_size<sam_msgs::srv::UavcanUpdateBattery_Response>::value
  >
{
};

template<>
struct is_service<sam_msgs::srv::UavcanUpdateBattery>
  : std::true_type
{
};

template<>
struct is_service_request<sam_msgs::srv::UavcanUpdateBattery_Request>
  : std::true_type
{
};

template<>
struct is_service_response<sam_msgs::srv::UavcanUpdateBattery_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__TRAITS_HPP_
