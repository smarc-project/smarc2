// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/uavcan_node_status__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "sam_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "sam_msgs/msg/detail/uavcan_node_status__struct.h"
#include "sam_msgs/msg/detail/uavcan_node_status__functions.h"
#include "fastcdr/Cdr.h"

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

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _UavcanNodeStatus__ros_msg_type = sam_msgs__msg__UavcanNodeStatus;

static bool _UavcanNodeStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _UavcanNodeStatus__ros_msg_type * ros_message = static_cast<const _UavcanNodeStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: uptime_sec
  {
    cdr << ros_message->uptime_sec;
  }

  // Field name: health
  {
    cdr << ros_message->health;
  }

  // Field name: mode
  {
    cdr << ros_message->mode;
  }

  // Field name: sub_mode
  {
    cdr << ros_message->sub_mode;
  }

  // Field name: vendor_specific_status_code
  {
    cdr << ros_message->vendor_specific_status_code;
  }

  return true;
}

static bool _UavcanNodeStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _UavcanNodeStatus__ros_msg_type * ros_message = static_cast<_UavcanNodeStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: uptime_sec
  {
    cdr >> ros_message->uptime_sec;
  }

  // Field name: health
  {
    cdr >> ros_message->health;
  }

  // Field name: mode
  {
    cdr >> ros_message->mode;
  }

  // Field name: sub_mode
  {
    cdr >> ros_message->sub_mode;
  }

  // Field name: vendor_specific_status_code
  {
    cdr >> ros_message->vendor_specific_status_code;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t get_serialized_size_sam_msgs__msg__UavcanNodeStatus(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _UavcanNodeStatus__ros_msg_type * ros_message = static_cast<const _UavcanNodeStatus__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name uptime_sec
  {
    size_t item_size = sizeof(ros_message->uptime_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name health
  {
    size_t item_size = sizeof(ros_message->health);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name mode
  {
    size_t item_size = sizeof(ros_message->mode);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name sub_mode
  {
    size_t item_size = sizeof(ros_message->sub_mode);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name vendor_specific_status_code
  {
    size_t item_size = sizeof(ros_message->vendor_specific_status_code);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _UavcanNodeStatus__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_sam_msgs__msg__UavcanNodeStatus(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t max_serialized_size_sam_msgs__msg__UavcanNodeStatus(
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

  // member: uptime_sec
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: health
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: mode
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: sub_mode
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: vendor_specific_status_code
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
    using DataType = sam_msgs__msg__UavcanNodeStatus;
    is_plain =
      (
      offsetof(DataType, vendor_specific_status_code) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _UavcanNodeStatus__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_sam_msgs__msg__UavcanNodeStatus(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_UavcanNodeStatus = {
  "sam_msgs::msg",
  "UavcanNodeStatus",
  _UavcanNodeStatus__cdr_serialize,
  _UavcanNodeStatus__cdr_deserialize,
  _UavcanNodeStatus__get_serialized_size,
  _UavcanNodeStatus__max_serialized_size
};

static rosidl_message_type_support_t _UavcanNodeStatus__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_UavcanNodeStatus,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, msg, UavcanNodeStatus)() {
  return &_UavcanNodeStatus__type_support;
}

#if defined(__cplusplus)
}
#endif
