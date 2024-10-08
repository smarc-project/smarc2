// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from sam_graph_slam_2_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_
#define SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "sam_graph_slam_2_msgs/msg/detail/topics__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace sam_graph_slam_2_msgs
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

}  // namespace sam_graph_slam_2_msgs

namespace rosidl_generator_traits
{

[[deprecated("use sam_graph_slam_2_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const sam_graph_slam_2_msgs::msg::Topics & msg,
  std::ostream & out, size_t indentation = 0)
{
  sam_graph_slam_2_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use sam_graph_slam_2_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const sam_graph_slam_2_msgs::msg::Topics & msg)
{
  return sam_graph_slam_2_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<sam_graph_slam_2_msgs::msg::Topics>()
{
  return "sam_graph_slam_2_msgs::msg::Topics";
}

template<>
inline const char * name<sam_graph_slam_2_msgs::msg::Topics>()
{
  return "sam_graph_slam_2_msgs/msg/Topics";
}

template<>
struct has_fixed_size<sam_graph_slam_2_msgs::msg::Topics>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<sam_graph_slam_2_msgs::msg::Topics>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<sam_graph_slam_2_msgs::msg::Topics>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__TRAITS_HPP_
