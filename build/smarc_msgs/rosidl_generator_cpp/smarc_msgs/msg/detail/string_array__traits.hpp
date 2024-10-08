// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/StringArray.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/string_array__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const StringArray & msg,
  std::ostream & out)
{
  out << "{";
  // member: string_array
  {
    if (msg.string_array.size() == 0) {
      out << "string_array: []";
    } else {
      out << "string_array: [";
      size_t pending_items = msg.string_array.size();
      for (auto item : msg.string_array) {
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
  const StringArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: string_array
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.string_array.size() == 0) {
      out << "string_array: []\n";
    } else {
      out << "string_array:\n";
      for (auto item : msg.string_array) {
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

inline std::string to_yaml(const StringArray & msg, bool use_flow_style = false)
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

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::msg::StringArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::StringArray & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::StringArray>()
{
  return "smarc_msgs::msg::StringArray";
}

template<>
inline const char * name<smarc_msgs::msg::StringArray>()
{
  return "smarc_msgs/msg/StringArray";
}

template<>
struct has_fixed_size<smarc_msgs::msg::StringArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::msg::StringArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::msg::StringArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__STRING_ARRAY__TRAITS_HPP_
