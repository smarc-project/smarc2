// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "sam_msgs/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.hpp"

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

namespace sam_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
cdr_serialize(
  const sam_msgs::msg::UavcanNodeStatusNamed & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  sam_msgs::msg::UavcanNodeStatusNamed & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
get_serialized_size(
  const sam_msgs::msg::UavcanNodeStatusNamed & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
max_serialized_size_UavcanNodeStatusNamed(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace sam_msgs

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, sam_msgs, msg, UavcanNodeStatusNamed)();

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
