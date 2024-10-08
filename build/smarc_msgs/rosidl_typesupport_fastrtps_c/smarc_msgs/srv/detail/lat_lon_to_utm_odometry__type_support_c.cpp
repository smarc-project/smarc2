// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smarc_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.h"
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__functions.h"
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

#include "smarc_msgs/msg/detail/lat_lon_odometry__functions.h"  // lat_lon_odom

// forward declare type support functions
size_t get_serialized_size_smarc_msgs__msg__LatLonOdometry(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_smarc_msgs__msg__LatLonOdometry(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, msg, LatLonOdometry)();


using _LatLonToUTMOdometry_Request__ros_msg_type = smarc_msgs__srv__LatLonToUTMOdometry_Request;

static bool _LatLonToUTMOdometry_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _LatLonToUTMOdometry_Request__ros_msg_type * ros_message = static_cast<const _LatLonToUTMOdometry_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: lat_lon_odom
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, smarc_msgs, msg, LatLonOdometry
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->lat_lon_odom, cdr))
    {
      return false;
    }
  }

  return true;
}

static bool _LatLonToUTMOdometry_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _LatLonToUTMOdometry_Request__ros_msg_type * ros_message = static_cast<_LatLonToUTMOdometry_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: lat_lon_odom
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, smarc_msgs, msg, LatLonOdometry
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->lat_lon_odom))
    {
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t get_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _LatLonToUTMOdometry_Request__ros_msg_type * ros_message = static_cast<const _LatLonToUTMOdometry_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name lat_lon_odom

  current_alignment += get_serialized_size_smarc_msgs__msg__LatLonOdometry(
    &(ros_message->lat_lon_odom), current_alignment);

  return current_alignment - initial_alignment;
}

static uint32_t _LatLonToUTMOdometry_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t max_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Request(
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

  // member: lat_lon_odom
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_smarc_msgs__msg__LatLonOdometry(
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
    using DataType = smarc_msgs__srv__LatLonToUTMOdometry_Request;
    is_plain =
      (
      offsetof(DataType, lat_lon_odom) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _LatLonToUTMOdometry_Request__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Request(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_LatLonToUTMOdometry_Request = {
  "smarc_msgs::srv",
  "LatLonToUTMOdometry_Request",
  _LatLonToUTMOdometry_Request__cdr_serialize,
  _LatLonToUTMOdometry_Request__cdr_deserialize,
  _LatLonToUTMOdometry_Request__get_serialized_size,
  _LatLonToUTMOdometry_Request__max_serialized_size
};

static rosidl_message_type_support_t _LatLonToUTMOdometry_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_LatLonToUTMOdometry_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, srv, LatLonToUTMOdometry_Request)() {
  return &_LatLonToUTMOdometry_Request__type_support;
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
// #include "smarc_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.h"
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__functions.h"
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

#include "nav_msgs/msg/detail/odometry__functions.h"  // odom

// forward declare type support functions
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
size_t get_serialized_size_nav_msgs__msg__Odometry(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
size_t max_serialized_size_nav_msgs__msg__Odometry(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_smarc_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, nav_msgs, msg, Odometry)();


using _LatLonToUTMOdometry_Response__ros_msg_type = smarc_msgs__srv__LatLonToUTMOdometry_Response;

static bool _LatLonToUTMOdometry_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _LatLonToUTMOdometry_Response__ros_msg_type * ros_message = static_cast<const _LatLonToUTMOdometry_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: odom
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, nav_msgs, msg, Odometry
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->odom, cdr))
    {
      return false;
    }
  }

  return true;
}

static bool _LatLonToUTMOdometry_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _LatLonToUTMOdometry_Response__ros_msg_type * ros_message = static_cast<_LatLonToUTMOdometry_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: odom
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, nav_msgs, msg, Odometry
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->odom))
    {
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t get_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _LatLonToUTMOdometry_Response__ros_msg_type * ros_message = static_cast<const _LatLonToUTMOdometry_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name odom

  current_alignment += get_serialized_size_nav_msgs__msg__Odometry(
    &(ros_message->odom), current_alignment);

  return current_alignment - initial_alignment;
}

static uint32_t _LatLonToUTMOdometry_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smarc_msgs
size_t max_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Response(
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

  // member: odom
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_nav_msgs__msg__Odometry(
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
    using DataType = smarc_msgs__srv__LatLonToUTMOdometry_Response;
    is_plain =
      (
      offsetof(DataType, odom) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _LatLonToUTMOdometry_Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smarc_msgs__srv__LatLonToUTMOdometry_Response(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_LatLonToUTMOdometry_Response = {
  "smarc_msgs::srv",
  "LatLonToUTMOdometry_Response",
  _LatLonToUTMOdometry_Response__cdr_serialize,
  _LatLonToUTMOdometry_Response__cdr_deserialize,
  _LatLonToUTMOdometry_Response__get_serialized_size,
  _LatLonToUTMOdometry_Response__max_serialized_size
};

static rosidl_message_type_support_t _LatLonToUTMOdometry_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_LatLonToUTMOdometry_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, srv, LatLonToUTMOdometry_Response)() {
  return &_LatLonToUTMOdometry_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "smarc_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smarc_msgs/srv/lat_lon_to_utm_odometry.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t LatLonToUTMOdometry__callbacks = {
  "smarc_msgs::srv",
  "LatLonToUTMOdometry",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, srv, LatLonToUTMOdometry_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, srv, LatLonToUTMOdometry_Response)(),
};

static rosidl_service_type_support_t LatLonToUTMOdometry__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &LatLonToUTMOdometry__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smarc_msgs, srv, LatLonToUTMOdometry)() {
  return &LatLonToUTMOdometry__handle;
}

#if defined(__cplusplus)
}
#endif
