// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/execution_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'execution_queue'
#include "smarc_msgs/msg/detail/sm_task__traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ExecutionStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: currently_executing
  {
    out << "currently_executing: ";
    rosidl_generator_traits::value_to_yaml(msg.currently_executing, out);
    out << ", ";
  }

  // member: execution_queue
  {
    if (msg.execution_queue.size() == 0) {
      out << "execution_queue: []";
    } else {
      out << "execution_queue: [";
      size_t pending_items = msg.execution_queue.size();
      for (auto item : msg.execution_queue) {
        to_flow_style_yaml(item, out);
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
  const ExecutionStatus & msg,
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

  // member: currently_executing
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "currently_executing: ";
    rosidl_generator_traits::value_to_yaml(msg.currently_executing, out);
    out << "\n";
  }

  // member: execution_queue
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.execution_queue.size() == 0) {
      out << "execution_queue: []\n";
    } else {
      out << "execution_queue:\n";
      for (auto item : msg.execution_queue) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecutionStatus & msg, bool use_flow_style = false)
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
  const smarc_msgs::msg::ExecutionStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::ExecutionStatus & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::ExecutionStatus>()
{
  return "smarc_msgs::msg::ExecutionStatus";
}

template<>
inline const char * name<smarc_msgs::msg::ExecutionStatus>()
{
  return "smarc_msgs/msg/ExecutionStatus";
}

template<>
struct has_fixed_size<smarc_msgs::msg::ExecutionStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::msg::ExecutionStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::msg::ExecutionStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__TRAITS_HPP_
