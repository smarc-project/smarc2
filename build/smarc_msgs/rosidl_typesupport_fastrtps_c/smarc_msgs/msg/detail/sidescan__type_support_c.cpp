// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/sidescan__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smarc_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smarc_msgs/msg/detail/sidescan__struct.h"
#include "smarc_msgs/msg/detail/sidescan__functions.h"
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

#include "rosidl_runtime_c/primitives_sequence.h"  // extra_channel, port_channel, port_channel_angle_high, port_channel_angle_low, starboard_channel, starboard_channel_angle_high, starboard_channel_angle_low
#include "rosidl_runtime_c/primitives_sequence_functions.h"  // extra_channel, port_channel, port_channel_angle_high, port_channel_angle_low, starboard_channel, starboard_channel_angle_high, starboard_channel_angle_low
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _Sidescan__ros_msg_type = smarc_msgs__msg__Sidescan;

static bool _Sidescan__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Sidescan__ros_msg_type * ros_message = static_cast<const _Sidescan__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->header, cdr))
    {
      return false;
    }
  }

  // Field name: type
  {
    cdr << ros_message->type;
  }

  // Field name: time
  {
    cdr << ros_message->time;
  }

  // Field name: frequency_id
  {
    cdr << ros_message->frequency_id;
  }

  // Field name: gain
  {
    cdr << ros_message->gain;
  }

  // Field name: decimation
  {
    cdr << ros_message->decimation;
  }

  // Field name: max_duration
  {
    cdr << ros_message->max_duration;
  }

  // Field name: port_channel
  {
    size_t size = ros_message->port_channel.size;
    auto array_ptr = ros_message->port_channel.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: starboard_channel
  {
    size_t size = ros_message->starboard_channel.size;
    auto array_ptr = ros_message->starboard_channel.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: port_channel_angle_high
  {
    size_t size = ros_message->port_channel_angle_high.size;
    auto array_ptr = ros_message->port_channel_angle_high.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: port_channel_angle_low
  {
    size_t size = ros_message->port_channel_angle_low.size;
    auto array_ptr = ros_message->port_channel_angle_low.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: starboard_channel_angle_high
  {
    size_t size = ros_message->starboard_channel_angle_high.size;
    auto array_ptr = ros_message->starboard_channel_angle_high.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: starboard_channel_angle_low
  {
    size_t size = ros_message->starboard_channel_angle_low.size;
    auto array_ptr = ros_message->starboard_channel_angle_low.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: extra_channel
  {
    size_t size = ros_message->extra_channel.size;
    auto array_ptr = ros_message->extra_channel.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  return true;
}

static bool _Sidescan__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Sidescan__ros_msg_type * ros_message = static_cast<_Sidescan__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->header))
    {
      return false;
    }
  }

  // Field name: type
  {
    cdr >> ros_message->type;
  }

  // Field name: time
  {
    cdr >> ros_message->time;
  }

  // Field name: frequency_id
  {
    cdr >> ros_message->frequency_id;
  }

  // Field name: gain
  {
    cdr >> ros_message->gain;
  }

  // Field name: decimation
  {
    cdr >> ros_message->decimation;
  }

  // Field name: max_duration
  {
    cdr >> ros_message->max_duration;
  }

  // Field name: port_channel
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->port_channel.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->port_channel);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->port_channel, size)) {
      fprintf(stderr, "failed to create array for field 'port_channel'");
      return false;
    }
    auto array_ptr = ros_message->port_channel.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: starboard_channel
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->starboard_channel.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->starboard_channel);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->starboard_channel, size)) {
      fprintf(stderr, "failed to create array for field 'starboard_channel'");
      return false;
    }
    auto array_ptr = ros_message->starboard_channel.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: port_channel_angle_high
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->port_channel_angle_high.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->port_channel_angle_high);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->port_channel_angle_high, size)) {
      fprintf(stderr, "failed to create array for field 'port_channel_angle_high'");
      return false;
    }
    auto array_ptr = ros_message->port_channel_angle_high.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: port_channel_angle_low
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->port_channel_angle_low.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->port_channel_angle_low);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->port_channel_angle_low, size)) {
      fprintf(stderr, "failed to create array for field 'port_channel_angle_low'");
      return false;
    }
    auto array_ptr = ros_message->port_channel_angle_low.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: starboard_channel_angle_high
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->starboard_channel_angle_high.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->starboard_channel_angle_high);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->starboard_channel_angle_high, size)) {
      fprintf(stderr, "failed to create array for field 'starboard_channel_angle_high'");
      return false;
    }
    auto array_ptr = ros_message->starboard_channel_angle_high.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: starboard_channel_angle_low
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->starboard_channel_angle_low.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->starboard_channel_angle_low);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->starboard_channel_angle_low, size)) {
      fprintf(stderr, "failed to create array for field 'starboard_channel_angle_low'");
      return false;
    }
    auto array_ptr = ros_message->starboard_channel_angle_low.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: extra_channel
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->extra_channel.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->extra_channel);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->extra_channel, size)) {
      fprintf(stderr, "failed to create array for field 'extra_channel'");
      return false;
    }
    auto array_ptr = ros_message->extra_channel.data;
    cdr.deserializeArray(array_ptr, size);
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t get_serialized_size_smarc_msgs__msg__Sidescan(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Sidescan__ros_msg_type * ros_message = static_cast<const _Sidescan__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name header

  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);
  // field.name type
  {
    size_t item_size = sizeof(ros_message->type);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name time
  {
    size_t item_size = sizeof(ros_message->time);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name frequency_id
  {
    size_t item_size = sizeof(ros_message->frequency_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name gain
  {
    size_t item_size = sizeof(ros_message->gain);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name decimation
  {
    size_t item_size = sizeof(ros_message->decimation);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name max_duration
  {
    size_t item_size = sizeof(ros_message->max_duration);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name port_channel
  {
    size_t array_size = ros_message->port_channel.size;
    auto array_ptr = ros_message->port_channel.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name starboard_channel
  {
    size_t array_size = ros_message->starboard_channel.size;
    auto array_ptr = ros_message->starboard_channel.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name port_channel_angle_high
  {
    size_t array_size = ros_message->port_channel_angle_high.size;
    auto array_ptr = ros_message->port_channel_angle_high.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name port_channel_angle_low
  {
    size_t array_size = ros_message->port_channel_angle_low.size;
    auto array_ptr = ros_message->port_channel_angle_low.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name starboard_channel_angle_high
  {
    size_t array_size = ros_message->starboard_channel_angle_high.size;
    auto array_ptr = ros_message->starboard_channel_angle_high.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name starboard_channel_angle_low
  {
    size_t array_size = ros_message->starboard_channel_angle_low.size;
    auto array_ptr = ros_message->starboard_channel_angle_low.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name extra_channel
  {
    size_t array_size = ros_message->extra_channel.size;
    auto array_ptr = ros_message->extra_channel.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Sidescan__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smarc_msgs__msg__Sidescan(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t max_serialized_size_smarc_msgs__msg__Sidescan(
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

  // member: header
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: type
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: time
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: frequency_id
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: gain
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: decimation
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: max_duration
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: port_channel
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: starboard_channel
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: port_channel_angle_high
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: port_channel_angle_low
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: starboard_channel_angle_high
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: starboard_channel_angle_low
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: extra_channel
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = smarc_msgs__msg__Sidescan;
    is_plain =
      (
      offsetof(DataType, extra_channel) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Sidescan__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smarc_msgs__msg__Sidescan(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Sidescan = {
  "smarc_msgs::msg",
  "Sidescan",
  _Sidescan__cdr_serialize,
  _Sidescan__cdr_deserialize,
  _Sidescan__get_serialized_size,
  _Sidescan__max_serialized_size
};

static rosidl_message_type_support_t _Sidescan__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Sidescan,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, msg, Sidescan)() {
  return &_Sidescan__type_support;
}

#if defined(__cplusplus)
}
#endif
