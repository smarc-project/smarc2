// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_mission_msgs:srv/UTMLatLon.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_H_
#define SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'utm_points'
#include "geometry_msgs/msg/detail/point_stamped__struct.h"
// Member 'lat_lon_points'
#include "geographic_msgs/msg/detail/geo_point__struct.h"

/// Struct defined in srv/UTMLatLon in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__srv__UTMLatLon_Request
{
  geometry_msgs__msg__PointStamped__Sequence utm_points;
  geographic_msgs__msg__GeoPoint__Sequence lat_lon_points;
} smarc_mission_msgs__srv__UTMLatLon_Request;

// Struct for a sequence of smarc_mission_msgs__srv__UTMLatLon_Request.
typedef struct smarc_mission_msgs__srv__UTMLatLon_Request__Sequence
{
  smarc_mission_msgs__srv__UTMLatLon_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__srv__UTMLatLon_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'lat_lon_points'
// already included above
// #include "geographic_msgs/msg/detail/geo_point__struct.h"
// Member 'utm_points'
// already included above
// #include "geometry_msgs/msg/detail/point_stamped__struct.h"

/// Struct defined in srv/UTMLatLon in the package smarc_mission_msgs.
typedef struct smarc_mission_msgs__srv__UTMLatLon_Response
{
  geographic_msgs__msg__GeoPoint__Sequence lat_lon_points;
  geometry_msgs__msg__PointStamped__Sequence utm_points;
} smarc_mission_msgs__srv__UTMLatLon_Response;

// Struct for a sequence of smarc_mission_msgs__srv__UTMLatLon_Response.
typedef struct smarc_mission_msgs__srv__UTMLatLon_Response__Sequence
{
  smarc_mission_msgs__srv__UTMLatLon_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_mission_msgs__srv__UTMLatLon_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_H_
