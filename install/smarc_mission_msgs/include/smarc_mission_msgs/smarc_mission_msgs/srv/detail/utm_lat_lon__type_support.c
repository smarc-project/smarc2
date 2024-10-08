// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from smarc_mission_msgs:srv/UTMLatLon.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "smarc_mission_msgs/srv/detail/utm_lat_lon__rosidl_typesupport_introspection_c.h"
#include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "smarc_mission_msgs/srv/detail/utm_lat_lon__functions.h"
#include "smarc_mission_msgs/srv/detail/utm_lat_lon__struct.h"


// Include directives for member types
// Member `utm_points`
#include "geometry_msgs/msg/point_stamped.h"
// Member `utm_points`
#include "geometry_msgs/msg/detail/point_stamped__rosidl_typesupport_introspection_c.h"
// Member `lat_lon_points`
#include "geographic_msgs/msg/geo_point.h"
// Member `lat_lon_points`
#include "geographic_msgs/msg/detail/geo_point__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_mission_msgs__srv__UTMLatLon_Request__init(message_memory);
}

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_fini_function(void * message_memory)
{
  smarc_mission_msgs__srv__UTMLatLon_Request__fini(message_memory);
}

size_t smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Request__utm_points(
  const void * untyped_member)
{
  const geometry_msgs__msg__PointStamped__Sequence * member =
    (const geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__utm_points(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__PointStamped__Sequence * member =
    (const geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__utm_points(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__PointStamped__Sequence * member =
    (geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Request__utm_points(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__PointStamped * item =
    ((const geometry_msgs__msg__PointStamped *)
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__utm_points(untyped_member, index));
  geometry_msgs__msg__PointStamped * value =
    (geometry_msgs__msg__PointStamped *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Request__utm_points(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__PointStamped * item =
    ((geometry_msgs__msg__PointStamped *)
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__utm_points(untyped_member, index));
  const geometry_msgs__msg__PointStamped * value =
    (const geometry_msgs__msg__PointStamped *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Request__utm_points(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__PointStamped__Sequence * member =
    (geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  geometry_msgs__msg__PointStamped__Sequence__fini(member);
  return geometry_msgs__msg__PointStamped__Sequence__init(member, size);
}

size_t smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Request__lat_lon_points(
  const void * untyped_member)
{
  const geographic_msgs__msg__GeoPoint__Sequence * member =
    (const geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__lat_lon_points(
  const void * untyped_member, size_t index)
{
  const geographic_msgs__msg__GeoPoint__Sequence * member =
    (const geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__lat_lon_points(
  void * untyped_member, size_t index)
{
  geographic_msgs__msg__GeoPoint__Sequence * member =
    (geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Request__lat_lon_points(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geographic_msgs__msg__GeoPoint * item =
    ((const geographic_msgs__msg__GeoPoint *)
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__lat_lon_points(untyped_member, index));
  geographic_msgs__msg__GeoPoint * value =
    (geographic_msgs__msg__GeoPoint *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Request__lat_lon_points(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geographic_msgs__msg__GeoPoint * item =
    ((geographic_msgs__msg__GeoPoint *)
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__lat_lon_points(untyped_member, index));
  const geographic_msgs__msg__GeoPoint * value =
    (const geographic_msgs__msg__GeoPoint *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Request__lat_lon_points(
  void * untyped_member, size_t size)
{
  geographic_msgs__msg__GeoPoint__Sequence * member =
    (geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  geographic_msgs__msg__GeoPoint__Sequence__fini(member);
  return geographic_msgs__msg__GeoPoint__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_member_array[2] = {
  {
    "utm_points",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__UTMLatLon_Request, utm_points),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Request__utm_points,  // size() function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__utm_points,  // get_const(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__utm_points,  // get(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Request__utm_points,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Request__utm_points,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Request__utm_points  // resize(index) function pointer
  },
  {
    "lat_lon_points",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__UTMLatLon_Request, lat_lon_points),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Request__lat_lon_points,  // size() function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Request__lat_lon_points,  // get_const(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Request__lat_lon_points,  // get(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Request__lat_lon_points,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Request__lat_lon_points,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Request__lat_lon_points  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_members = {
  "smarc_mission_msgs__srv",  // message namespace
  "UTMLatLon_Request",  // message name
  2,  // number of fields
  sizeof(smarc_mission_msgs__srv__UTMLatLon_Request),
  smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_member_array,  // message members
  smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Request)() {
  smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PointStamped)();
  smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geographic_msgs, msg, GeoPoint)();
  if (!smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_mission_msgs__srv__UTMLatLon_Request__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "smarc_mission_msgs/srv/detail/utm_lat_lon__rosidl_typesupport_introspection_c.h"
// already included above
// #include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/utm_lat_lon__functions.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/utm_lat_lon__struct.h"


// Include directives for member types
// Member `lat_lon_points`
// already included above
// #include "geographic_msgs/msg/geo_point.h"
// Member `lat_lon_points`
// already included above
// #include "geographic_msgs/msg/detail/geo_point__rosidl_typesupport_introspection_c.h"
// Member `utm_points`
// already included above
// #include "geometry_msgs/msg/point_stamped.h"
// Member `utm_points`
// already included above
// #include "geometry_msgs/msg/detail/point_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  smarc_mission_msgs__srv__UTMLatLon_Response__init(message_memory);
}

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_fini_function(void * message_memory)
{
  smarc_mission_msgs__srv__UTMLatLon_Response__fini(message_memory);
}

size_t smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Response__lat_lon_points(
  const void * untyped_member)
{
  const geographic_msgs__msg__GeoPoint__Sequence * member =
    (const geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__lat_lon_points(
  const void * untyped_member, size_t index)
{
  const geographic_msgs__msg__GeoPoint__Sequence * member =
    (const geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__lat_lon_points(
  void * untyped_member, size_t index)
{
  geographic_msgs__msg__GeoPoint__Sequence * member =
    (geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Response__lat_lon_points(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geographic_msgs__msg__GeoPoint * item =
    ((const geographic_msgs__msg__GeoPoint *)
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__lat_lon_points(untyped_member, index));
  geographic_msgs__msg__GeoPoint * value =
    (geographic_msgs__msg__GeoPoint *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Response__lat_lon_points(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geographic_msgs__msg__GeoPoint * item =
    ((geographic_msgs__msg__GeoPoint *)
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__lat_lon_points(untyped_member, index));
  const geographic_msgs__msg__GeoPoint * value =
    (const geographic_msgs__msg__GeoPoint *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Response__lat_lon_points(
  void * untyped_member, size_t size)
{
  geographic_msgs__msg__GeoPoint__Sequence * member =
    (geographic_msgs__msg__GeoPoint__Sequence *)(untyped_member);
  geographic_msgs__msg__GeoPoint__Sequence__fini(member);
  return geographic_msgs__msg__GeoPoint__Sequence__init(member, size);
}

size_t smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Response__utm_points(
  const void * untyped_member)
{
  const geometry_msgs__msg__PointStamped__Sequence * member =
    (const geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return member->size;
}

const void * smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__utm_points(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__PointStamped__Sequence * member =
    (const geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void * smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__utm_points(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__PointStamped__Sequence * member =
    (geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Response__utm_points(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__PointStamped * item =
    ((const geometry_msgs__msg__PointStamped *)
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__utm_points(untyped_member, index));
  geometry_msgs__msg__PointStamped * value =
    (geometry_msgs__msg__PointStamped *)(untyped_value);
  *value = *item;
}

void smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Response__utm_points(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__PointStamped * item =
    ((geometry_msgs__msg__PointStamped *)
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__utm_points(untyped_member, index));
  const geometry_msgs__msg__PointStamped * value =
    (const geometry_msgs__msg__PointStamped *)(untyped_value);
  *item = *value;
}

bool smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Response__utm_points(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__PointStamped__Sequence * member =
    (geometry_msgs__msg__PointStamped__Sequence *)(untyped_member);
  geometry_msgs__msg__PointStamped__Sequence__fini(member);
  return geometry_msgs__msg__PointStamped__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_member_array[2] = {
  {
    "lat_lon_points",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__UTMLatLon_Response, lat_lon_points),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Response__lat_lon_points,  // size() function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__lat_lon_points,  // get_const(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__lat_lon_points,  // get(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Response__lat_lon_points,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Response__lat_lon_points,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Response__lat_lon_points  // resize(index) function pointer
  },
  {
    "utm_points",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smarc_mission_msgs__srv__UTMLatLon_Response, utm_points),  // bytes offset in struct
    NULL,  // default value
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__size_function__UTMLatLon_Response__utm_points,  // size() function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_const_function__UTMLatLon_Response__utm_points,  // get_const(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__get_function__UTMLatLon_Response__utm_points,  // get(index) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__fetch_function__UTMLatLon_Response__utm_points,  // fetch(index, &value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__assign_function__UTMLatLon_Response__utm_points,  // assign(index, value) function pointer
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__resize_function__UTMLatLon_Response__utm_points  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_members = {
  "smarc_mission_msgs__srv",  // message namespace
  "UTMLatLon_Response",  // message name
  2,  // number of fields
  sizeof(smarc_mission_msgs__srv__UTMLatLon_Response),
  smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_member_array,  // message members
  smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Response)() {
  smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geographic_msgs, msg, GeoPoint)();
  smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PointStamped)();
  if (!smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &smarc_mission_msgs__srv__UTMLatLon_Response__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "smarc_mission_msgs/srv/detail/utm_lat_lon__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_members = {
  "smarc_mission_msgs__srv",  // service namespace
  "UTMLatLon",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_Request_message_type_support_handle,
  NULL  // response message
  // smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_Response_message_type_support_handle
};

static rosidl_service_type_support_t smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_type_support_handle = {
  0,
  &smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_smarc_mission_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon)() {
  if (!smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_type_support_handle.typesupport_identifier) {
    smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, smarc_mission_msgs, srv, UTMLatLon_Response)()->data;
  }

  return &smarc_mission_msgs__srv__detail__utm_lat_lon__rosidl_typesupport_introspection_c__UTMLatLon_service_type_support_handle;
}
