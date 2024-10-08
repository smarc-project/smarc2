// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/uavcan_node_status_named__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "sam_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.h"
#include "sam_msgs/msg/detail/uavcan_node_status_named__functions.h"
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

#include "rosidl_runtime_c/string.h"  // name
#include "rosidl_runtime_c/string_functions.h"  // name
#include "sam_msgs/msg/detail/uavcan_node_status__functions.h"  // ns

// forward declare type support functions
size_t get_serialized_size_sam_msgs__msg__UavcanNodeStatus(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_sam_msgs__msg__UavcanNodeStatus(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, msg, UavcanNodeStatus)();


using _UavcanNodeStatusNamed__ros_msg_type = sam_msgs__msg__UavcanNodeStatusNamed;

static bool _UavcanNodeStatusNamed__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _UavcanNodeStatusNamed__ros_msg_type * ros_message = static_cast<const _UavcanNodeStatusNamed__ros_msg_type *>(untyped_ros_message);
  // Field name: id
  {
    cdr << ros_message->id;
  }

  // Field name: name
  {
    const rosidl_runtime_c__String * str = &ros_message->name;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: ns
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, sam_msgs, msg, UavcanNodeStatus
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->ns, cdr))
    {
      return false;
    }
  }

  return true;
}

static bool _UavcanNodeStatusNamed__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _UavcanNodeStatusNamed__ros_msg_type * ros_message = static_cast<_UavcanNodeStatusNamed__ros_msg_type *>(untyped_ros_message);
  // Field name: id
  {
    cdr >> ros_message->id;
  }

  // Field name: name
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->name.data) {
      rosidl_runtime_c__String__init(&ros_message->name);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->name,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'name'\n");
      return false;
    }
  }

  // Field name: ns
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, sam_msgs, msg, UavcanNodeStatus
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->ns))
    {
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t get_serialized_size_sam_msgs__msg__UavcanNodeStatusNamed(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _UavcanNodeStatusNamed__ros_msg_type * ros_message = static_cast<const _UavcanNodeStatusNamed__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name id
  {
    size_t item_size = sizeof(ros_message->id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name name
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->name.size + 1);
  // field.name ns

  current_alignment += get_serialized_size_sam_msgs__msg__UavcanNodeStatus(
    &(ros_message->ns), current_alignment);

  return current_alignment - initial_alignment;
}

static uint32_t _UavcanNodeStatusNamed__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_sam_msgs__msg__UavcanNodeStatusNamed(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t max_serialized_size_sam_msgs__msg__UavcanNodeStatusNamed(
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

  // member: id
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: name
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: ns
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_sam_msgs__msg__UavcanNodeStatus(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = sam_msgs__msg__UavcanNodeStatusNamed;
    is_plain =
      (
      offsetof(DataType, ns) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _UavcanNodeStatusNamed__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_sam_msgs__msg__UavcanNodeStatusNamed(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_UavcanNodeStatusNamed = {
  "sam_msgs::msg",
  "UavcanNodeStatusNamed",
  _UavcanNodeStatusNamed__cdr_serialize,
  _UavcanNodeStatusNamed__cdr_deserialize,
  _UavcanNodeStatusNamed__get_serialized_size,
  _UavcanNodeStatusNamed__max_serialized_size
};

static rosidl_message_type_support_t _UavcanNodeStatusNamed__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_UavcanNodeStatusNamed,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, msg, UavcanNodeStatusNamed)() {
  return &_UavcanNodeStatusNamed__type_support;
}

#if defined(__cplusplus)
}
#endif
