// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from dead_reckoning_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_
#define DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "dead_reckoning_msgs/msg/detail/topics__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace dead_reckoning_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Topics & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Topics & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Topics & msg, bool use_flow_style = false)
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

}  // namespace dead_reckoning_msgs

namespace rosidl_generator_traits
{

[[deprecated("use dead_reckoning_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const dead_reckoning_msgs::msg::Topics & msg,
  std::ostream & out, size_t indentation = 0)
{
  dead_reckoning_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use dead_reckoning_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const dead_reckoning_msgs::msg::Topics & msg)
{
  return dead_reckoning_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<dead_reckoning_msgs::msg::Topics>()
{
  return "dead_reckoning_msgs::msg::Topics";
}

template<>
inline const char * name<dead_reckoning_msgs::msg::Topics>()
{
  return "dead_reckoning_msgs/msg/Topics";
}

template<>
struct has_fixed_size<dead_reckoning_msgs::msg::Topics>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<dead_reckoning_msgs::msg::Topics>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<dead_reckoning_msgs::msg::Topics>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_
