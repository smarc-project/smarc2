// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_msgs:msg/Leak.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LEAK__TRAITS_HPP_
#define SAM_MSGS__MSG__DETAIL__LEAK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_msgs/msg/detail/leak__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace sam_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Leak & msg,
  std::ostream & out)
{
  out << "{";
  // member: value
  {
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
    out << ", ";
  }

  // member: leak_counter
  {
    out << "leak_counter: ";
    rosidl_generator_traits::value_to_yaml(msg.leak_counter, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Leak & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: value
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value: ";
    rosidl_generator_traits::value_to_yaml(msg.value, out);
    out << "\n";
  }

  // member: leak_counter
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "leak_counter: ";
    rosidl_generator_traits::value_to_yaml(msg.leak_counter, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Leak & msg, bool use_flow_style = false)
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
  const sam_msgs::msg::Leak & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_msgs::msg::Leak & msg)
{
  return sam_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_msgs::msg::Leak>()
{
  return "sam_msgs::msg::Leak";
}

template<>
inline const char * name<sam_msgs::msg::Leak>()
{
  return "sam_msgs/msg/Leak";
}

template<>
struct has_fixed_size<sam_msgs::msg::Leak>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_msgs::msg::Leak>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_msgs::msg::Leak>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_MSGS__MSG__DETAIL__LEAK__TRAITS_HPP_
