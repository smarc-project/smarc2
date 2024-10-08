// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:srv/AddTask.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASK__TRAITS_HPP_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/srv/detail/add_task__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'task'
#include "smarc_msgs/msg/detail/sm_task__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddTask_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: task
  {
    out << "task: ";
    to_flow_style_yaml(msg.task, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddTask_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task:\n";
    to_block_style_yaml(msg.task, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddTask_Request & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::AddTask_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::AddTask_Request & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::AddTask_Request>()
{
  return "smarc_msgs::srv::AddTask_Request";
}

template<>
inline const char * name<smarc_msgs::srv::AddTask_Request>()
{
  return "smarc_msgs/srv/AddTask_Request";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTask_Request>
  : std::integral_constant<bool, has_fixed_size<smarc_msgs::msg::SMTask>::value> {};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTask_Request>
  : std::integral_constant<bool, has_bounded_size<smarc_msgs::msg::SMTask>::value> {};

template<>
struct is_message<smarc_msgs::srv::AddTask_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddTask_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const AddTask_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddTask_Response & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::AddTask_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::AddTask_Response & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::AddTask_Response>()
{
  return "smarc_msgs::srv::AddTask_Response";
}

template<>
inline const char * name<smarc_msgs::srv::AddTask_Response>()
{
  return "smarc_msgs/srv/AddTask_Response";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTask_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTask_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_msgs::srv::AddTask_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_msgs::srv::AddTask>()
{
  return "smarc_msgs::srv::AddTask";
}

template<>
inline const char * name<smarc_msgs::srv::AddTask>()
{
  return "smarc_msgs/srv/AddTask";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTask>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_msgs::srv::AddTask_Request>::value &&
    has_fixed_size<smarc_msgs::srv::AddTask_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTask>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_msgs::srv::AddTask_Request>::value &&
    has_bounded_size<smarc_msgs::srv::AddTask_Response>::value
  >
{
};

template<>
struct is_service<smarc_msgs::srv::AddTask>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_msgs::srv::AddTask_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_msgs::srv::AddTask_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASK__TRAITS_HPP_
