// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from dead_reckoning_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "dead_reckoning_msgs/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "dead_reckoning_msgs/msg/detail/topics__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace dead_reckoning_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_dead_reckoning_msgs
cdr_serialize(
  const dead_reckoning_msgs::msg::Topics & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_dead_reckoning_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  dead_reckoning_msgs::msg::Topics & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_dead_reckoning_msgs
get_serialized_size(
  const dead_reckoning_msgs::msg::Topics & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_dead_reckoning_msgs
max_serialized_size_Topics(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace dead_reckoning_msgs

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_dead_reckoning_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, dead_reckoning_msgs, msg, Topics)();

#ifdef __cplusplus
}
#endif

#endif  // DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
