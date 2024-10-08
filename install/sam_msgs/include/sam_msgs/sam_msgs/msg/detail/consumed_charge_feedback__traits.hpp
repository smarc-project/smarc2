// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/consumed_charge_feedback__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ConsumedChargeFeedback & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: main
  {
    out << "main: ";
    rosidl_generator_traits::value_to_yaml(msg.main, out);
    out << ", ";
  }

  // member: esc1
  {
    out << "esc1: ";
    rosidl_generator_traits::value_to_yaml(msg.esc1, out);
    out << ", ";
  }

  // member: esc2
  {
    out << "esc2: ";
    rosidl_generator_traits::value_to_yaml(msg.esc2, out);
    out << ", ";
  }

  // member: esc3
  {
    out << "esc3: ";
    rosidl_generator_traits::value_to_yaml(msg.esc3, out);
    out << ", ";
  }

  // member: v20
  {
    out << "v20: ";
    rosidl_generator_traits::value_to_yaml(msg.v20, out);
    out << ", ";
  }

  // member: v12
  {
    out << "v12: ";
    rosidl_generator_traits::value_to_yaml(msg.v12, out);
    out << ", ";
  }

  // member: v7
  {
    out << "v7: ";
    rosidl_generator_traits::value_to_yaml(msg.v7, out);
    out << ", ";
  }

  // member: v5
  {
    out << "v5: ";
    rosidl_generator_traits::value_to_yaml(msg.v5, out);
    out << ", ";
  }

  // member: v33
  {
    out << "v33: ";
    rosidl_generator_traits::value_to_yaml(msg.v33, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ConsumedChargeFeedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: main
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "main: ";
    rosidl_generator_traits::value_to_yaml(msg.main, out);
    out << "\n";
  }

  // member: esc1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "esc1: ";
    rosidl_generator_traits::value_to_yaml(msg.esc1, out);
    out << "\n";
  }

  // member: esc2
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "esc2: ";
    rosidl_generator_traits::value_to_yaml(msg.esc2, out);
    out << "\n";
  }

  // member: esc3
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "esc3: ";
    rosidl_generator_traits::value_to_yaml(msg.esc3, out);
    out << "\n";
  }

  // member: v20
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v20: ";
    rosidl_generator_traits::value_to_yaml(msg.v20, out);
    out << "\n";
  }

  // member: v12
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v12: ";
    rosidl_generator_traits::value_to_yaml(msg.v12, out);
    out << "\n";
  }

  // member: v7
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v7: ";
    rosidl_generator_traits::value_to_yaml(msg.v7, out);
    out << "\n";
  }

  // member: v5
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v5: ";
    rosidl_generator_traits::value_to_yaml(msg.v5, out);
    out << "\n";
  }

  // member: v33
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v33: ";
    rosidl_generator_traits::value_to_yaml(msg.v33, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ConsumedChargeFeedback & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::ConsumedChargeFeedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::ConsumedChargeFeedback & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::ConsumedChargeFeedback>()
{
  return "sam_msgs::msg::ConsumedChargeFeedback";
}

template<>
inline const char * name<sam_msgs::msg::ConsumedChargeFeedback>()
{
  return "sam_msgs/msg/ConsumedChargeFeedback";
}

template<>
struct has_fixed_size<sam_msgs::msg::ConsumedChargeFeedback>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<sam_msgs::msg::ConsumedChargeFeedback>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<sam_msgs::msg::ConsumedChargeFeedback>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__TRAITS_HPP_
