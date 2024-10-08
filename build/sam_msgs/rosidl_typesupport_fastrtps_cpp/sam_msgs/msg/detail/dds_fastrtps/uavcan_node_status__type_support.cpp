// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/uavcan_node_status__rosidl_typesupport_fastrtps_cpp.hpp"
#include "sam_msgs/msg/detail/uavcan_node_status__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace sam_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
cdr_serialize(
  const sam_msgs::msg::UavcanNodeStatus & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: uptime_sec
  cdr << ros_message.uptime_sec;
  // Member: health
  cdr << ros_message.health;
  // Member: mode
  cdr << ros_message.mode;
  // Member: sub_mode
  cdr << ros_message.sub_mode;
  // Member: vendor_specific_status_code
  cdr << ros_message.vendor_specific_status_code;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  sam_msgs::msg::UavcanNodeStatus & ros_message)
{
  // Member: uptime_sec
  cdr >> ros_message.uptime_sec;

  // Member: health
  cdr >> ros_message.health;

  // Member: mode
  cdr >> ros_message.mode;

  // Member: sub_mode
  cdr >> ros_message.sub_mode;

  // Member: vendor_specific_status_code
  cdr >> ros_message.vendor_specific_status_code;

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
get_serialized_size(
  const sam_msgs::msg::UavcanNodeStatus & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: uptime_sec
  {
    size_t item_size = sizeof(ros_message.uptime_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: health
  {
    size_t item_size = sizeof(ros_message.health);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: mode
  {
    size_t item_size = sizeof(ros_message.mode);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: sub_mode
  {
    size_t item_size = sizeof(ros_message.sub_mode);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: vendor_specific_status_code
  {
    size_t item_size = sizeof(ros_message.vendor_specific_status_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_sam_msgs
max_serialized_size_UavcanNodeStatus(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: uptime_sec
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: health
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: mode
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: sub_mode
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: vendor_specific_status_code
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = sam_msgs::msg::UavcanNodeStatus;
    is_plain =
      (
      offsetof(DataType, vendor_specific_status_code) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _UavcanNodeStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const sam_msgs::msg::UavcanNodeStatus *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _UavcanNodeStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<sam_msgs::msg::UavcanNodeStatus *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _UavcanNodeStatus__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const sam_msgs::msg::UavcanNodeStatus *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _UavcanNodeStatus__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_UavcanNodeStatus(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _UavcanNodeStatus__callbacks = {
  "sam_msgs::msg",
  "UavcanNodeStatus",
  _UavcanNodeStatus__cdr_serialize,
  _UavcanNodeStatus__cdr_deserialize,
  _UavcanNodeStatus__get_serialized_size,
  _UavcanNodeStatus__max_serialized_size
};

static rosidl_message_type_support_t _UavcanNodeStatus__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_UavcanNodeStatus__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace sam_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_sam_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<sam_msgs::msg::UavcanNodeStatus>()
{
  return &sam_msgs::msg::typesupport_fastrtps_cpp::_UavcanNodeStatus__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, sam_msgs, msg, UavcanNodeStatus)() {
  return &sam_msgs::msg::typesupport_fastrtps_cpp::_UavcanNodeStatus__handle;
}

#ifdef __cplusplus
}
#endif
