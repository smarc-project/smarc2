// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice
#include "sam_msgs/srv/detail/uavcan_update_battery__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "sam_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "sam_msgs/srv/detail/uavcan_update_battery__struct.h"
#include "sam_msgs/srv/detail/uavcan_update_battery__functions.h"
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


using _UavcanUpdateBattery_Request__ros_msg_type = sam_msgs__srv__UavcanUpdateBattery_Request;

static bool _UavcanUpdateBattery_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _UavcanUpdateBattery_Request__ros_msg_type * ros_message = static_cast<const _UavcanUpdateBattery_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: node_id
  {
    cdr << ros_message->node_id;
  }

  // Field name: command
  {
    cdr << ros_message->command;
  }

  // Field name: charge
  {
    cdr << ros_message->charge;
  }

  return true;
}

static bool _UavcanUpdateBattery_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _UavcanUpdateBattery_Request__ros_msg_type * ros_message = static_cast<_UavcanUpdateBattery_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: node_id
  {
    cdr >> ros_message->node_id;
  }

  // Field name: command
  {
    cdr >> ros_message->command;
  }

  // Field name: charge
  {
    cdr >> ros_message->charge;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t get_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _UavcanUpdateBattery_Request__ros_msg_type * ros_message = static_cast<const _UavcanUpdateBattery_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name node_id
  {
    size_t item_size = sizeof(ros_message->node_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name command
  {
    size_t item_size = sizeof(ros_message->command);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name charge
  {
    size_t item_size = sizeof(ros_message->charge);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _UavcanUpdateBattery_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t max_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Request(
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

  // member: node_id
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: command
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: charge
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = sam_msgs__srv__UavcanUpdateBattery_Request;
    is_plain =
      (
      offsetof(DataType, charge) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _UavcanUpdateBattery_Request__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Request(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_UavcanUpdateBattery_Request = {
  "sam_msgs::srv",
  "UavcanUpdateBattery_Request",
  _UavcanUpdateBattery_Request__cdr_serialize,
  _UavcanUpdateBattery_Request__cdr_deserialize,
  _UavcanUpdateBattery_Request__get_serialized_size,
  _UavcanUpdateBattery_Request__max_serialized_size
};

static rosidl_message_type_support_t _UavcanUpdateBattery_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_UavcanUpdateBattery_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, srv, UavcanUpdateBattery_Request)() {
  return &_UavcanUpdateBattery_Request__type_support;
}

#if defined(__cplusplus)
}
#endif

// already included above
// #include <cassert>
// already included above
// #include <limits>
// already included above
// #include <string>
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
// already included above
// #include "sam_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "sam_msgs/srv/detail/uavcan_update_battery__struct.h"
// already included above
// #include "sam_msgs/srv/detail/uavcan_update_battery__functions.h"
// already included above
// #include "fastcdr/Cdr.h"

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


using _UavcanUpdateBattery_Response__ros_msg_type = sam_msgs__srv__UavcanUpdateBattery_Response;

static bool _UavcanUpdateBattery_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _UavcanUpdateBattery_Response__ros_msg_type * ros_message = static_cast<const _UavcanUpdateBattery_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    cdr << ros_message->success;
  }

  return true;
}

static bool _UavcanUpdateBattery_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _UavcanUpdateBattery_Response__ros_msg_type * ros_message = static_cast<_UavcanUpdateBattery_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    cdr >> ros_message->success;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t get_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _UavcanUpdateBattery_Response__ros_msg_type * ros_message = static_cast<const _UavcanUpdateBattery_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name success
  {
    size_t item_size = sizeof(ros_message->success);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _UavcanUpdateBattery_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_sam_msgs
size_t max_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Response(
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

  // member: success
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = sam_msgs__srv__UavcanUpdateBattery_Response;
    is_plain =
      (
      offsetof(DataType, success) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _UavcanUpdateBattery_Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_sam_msgs__srv__UavcanUpdateBattery_Response(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_UavcanUpdateBattery_Response = {
  "sam_msgs::srv",
  "UavcanUpdateBattery_Response",
  _UavcanUpdateBattery_Response__cdr_serialize,
  _UavcanUpdateBattery_Response__cdr_deserialize,
  _UavcanUpdateBattery_Response__get_serialized_size,
  _UavcanUpdateBattery_Response__max_serialized_size
};

static rosidl_message_type_support_t _UavcanUpdateBattery_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_UavcanUpdateBattery_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, srv, UavcanUpdateBattery_Response)() {
  return &_UavcanUpdateBattery_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "sam_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "sam_msgs/srv/uavcan_update_battery.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t UavcanUpdateBattery__callbacks = {
  "sam_msgs::srv",
  "UavcanUpdateBattery",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, srv, UavcanUpdateBattery_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, srv, UavcanUpdateBattery_Response)(),
};

static rosidl_service_type_support_t UavcanUpdateBattery__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &UavcanUpdateBattery__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sam_msgs, srv, UavcanUpdateBattery)() {
  return &UavcanUpdateBattery__handle;
}

#if defined(__cplusplus)
}
#endif
