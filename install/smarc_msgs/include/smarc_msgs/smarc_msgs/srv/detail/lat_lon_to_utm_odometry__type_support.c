// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c.h"
#include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__functions.h"
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.h"


// Include directives for member types
// Member `lat_lon_odom`
#include "smarc_msgs/msg/lat_lon_odometry.h"
// Member `lat_lon_odom`
#include "smarc_msgs/msg/detail/lat_lon_odometry__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__srv__LatLonToUTMOdometry_Request__init(message_memory);
}

void smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_fini_function(void * message_memory)
{
  smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_member_array[1] = {
  {
    "lat_lon_odom",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__srv__LatLonToUTMOdometry_Request, lat_lon_odom),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_members = {
  "smarc_msgs__srv",  // message namespace
  "LatLonToUTMOdometry_Request",  // message name
  1,  // number of fields
  sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request),
  smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_member_array,  // message members
  smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_type_support_handle = {
  0,
  &smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Request)() {
  smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, msg, LatLonOdometry)();
  if (!smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__srv__LatLonToUTMOdometry_Request__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c.h"
// already included above
// #include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__functions.h"
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__struct.h"


// Include directives for member types
// Member `odom`
#include "nav_msgs/msg/odometry.h"
// Member `odom`
#include "nav_msgs/msg/detail/odometry__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_msgs__srv__LatLonToUTMOdometry_Response__init(message_memory);
}

void smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_fini_function(void * message_memory)
{
  smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_member_array[1] = {
  {
    "odom",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_msgs__srv__LatLonToUTMOdometry_Response, odom),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_members = {
  "smarc_msgs__srv",  // message namespace
  "LatLonToUTMOdometry_Response",  // message name
  1,  // number of fields
  sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response),
  smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_member_array,  // message members
  smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_type_support_handle = {
  0,
  &smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Response)() {
  smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, nav_msgs, msg, Odometry)();
  if (!smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_type_support_handle.typesupport_identifier) {
    smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_msgs__srv__LatLonToUTMOdometry_Response__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "smarc_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_members = {
  "smarc_msgs__srv",  // service namespace
  "LatLonToUTMOdometry",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Request_message_type_support_handle,
  NULL  // response message
  // smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_Response_message_type_support_handle
};

static rosidl_service_type_support_t smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_type_support_handle = {
  0,
  &smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry)() {
  if (!smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_type_support_handle.typesupport_identifier) {
    smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_msgs, srv, LatLonToUTMOdometry_Response)()->data;
  }

  return &smarc_msgs__srv__detail__lat_lon_to_utm_odometry__rosidl_typesupport_introspection_c__LatLonToUTMOdometry_service_type_support_handle;
}
