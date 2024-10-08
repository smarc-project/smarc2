// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "smarc_msgs/msg/detail/lat_lon_odometry__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace smarc_msgs
{

namespace msg
{

namespace rosidl_typesupport_cpp
{

typedef struct _LatLonOdometry_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _LatLonOdometry_type_support_ids_t;

static const _LatLonOdometry_type_support_ids_t _LatLonOdometry_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _LatLonOdometry_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _LatLonOdometry_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _LatLonOdometry_type_support_symbol_names_t _LatLonOdometry_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_msgs, msg, LatLonOdometry)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_msgs, msg, LatLonOdometry)),
  }
};

typedef struct _LatLonOdometry_type_support_data_t
{
  void * data[2];
} _LatLonOdometry_type_support_data_t;

static _LatLonOdometry_type_support_data_t _LatLonOdometry_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _LatLonOdometry_message_typesupport_map = {
  2,
  "smarc_msgs",
  &_LatLonOdometry_message_typesupport_ids.typesupport_identifier[0],
  &_LatLonOdometry_message_typesupport_symbol_names.symbol_name[0],
  &_LatLonOdometry_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t LatLonOdometry_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_LatLonOdometry_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace msg

}  // namespace smarc_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_msgs::msg::LatLonOdometry>()
{
  return &::smarc_msgs::msg::rosidl_typesupport_cpp::LatLonOdometry_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_msgs, msg, LatLonOdometry)() {
  return get_message_type_support_handle<smarc_msgs::msg::LatLonOdometry>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp
