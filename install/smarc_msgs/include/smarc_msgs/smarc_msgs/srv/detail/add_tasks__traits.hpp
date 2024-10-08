// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:srv/AddTasks.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASKS__TRAITS_HPP_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASKS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/srv/detail/add_tasks__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'tasks'
#include "smarc_msgs/msg/detail/sm_task__traits.hpp"

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddTasks_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: tasks
  {
    if (msg.tasks.size() == 0) {
      out << "tasks: []";
    } else {
      out << "tasks: [";
      size_t pending_items = msg.tasks.size();
      for (auto item : msg.tasks) {
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
  const AddTasks_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: tasks
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tasks.size() == 0) {
      out << "tasks: []\n";
    } else {
      out << "tasks:\n";
      for (auto item : msg.tasks) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const AddTasks_Request & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::AddTasks_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::AddTasks_Request & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::AddTasks_Request>()
{
  return "smarc_msgs::srv::AddTasks_Request";
}

template<>
inline const char * name<smarc_msgs::srv::AddTasks_Request>()
{
  return "smarc_msgs/srv/AddTasks_Request";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTasks_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTasks_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::srv::AddTasks_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace smarc_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const AddTasks_Response & msg,
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
  const AddTasks_Response & msg,
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

inline std::string to_yaml(const AddTasks_Response & msg, bool use_flow_style = false)
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
  const smarc_msgs::srv::AddTasks_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::srv::AddTasks_Response & msg)
{
  return smarc_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::srv::AddTasks_Response>()
{
  return "smarc_msgs::srv::AddTasks_Response";
}

template<>
inline const char * name<smarc_msgs::srv::AddTasks_Response>()
{
  return "smarc_msgs/srv/AddTasks_Response";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTasks_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTasks_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smarc_msgs::srv::AddTasks_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_msgs::srv::AddTasks>()
{
  return "smarc_msgs::srv::AddTasks";
}

template<>
inline const char * name<smarc_msgs::srv::AddTasks>()
{
  return "smarc_msgs/srv/AddTasks";
}

template<>
struct has_fixed_size<smarc_msgs::srv::AddTasks>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_msgs::srv::AddTasks_Request>::value &&
    has_fixed_size<smarc_msgs::srv::AddTasks_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_msgs::srv::AddTasks>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_msgs::srv::AddTasks_Request>::value &&
    has_bounded_size<smarc_msgs::srv::AddTasks_Response>::value
  >
{
};

template<>
struct is_service<smarc_msgs::srv::AddTasks>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_msgs::srv::AddTasks_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_msgs::srv::AddTasks_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASKS__TRAITS_HPP_
