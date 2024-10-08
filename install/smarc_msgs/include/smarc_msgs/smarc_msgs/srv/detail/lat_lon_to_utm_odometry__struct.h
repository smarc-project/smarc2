// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_H_
#define SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'lat_lon_odom'
#include "smarc_msgs/msg/detail/lat_lon_odometry__struct.h"

/// Struct defined in srv/LatLonToUTMOdometry in the package smarc_msgs.
typedef struct smarc_msgs__srv__LatLonToUTMOdometry_Request
{
  smarc_msgs__msg__LatLonOdometry lat_lon_odom;
} smarc_msgs__srv__LatLonToUTMOdometry_Request;

// Struct for a sequence of smarc_msgs__srv__LatLonToUTMOdometry_Request.
typedef struct smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence
{
  smarc_msgs__srv__LatLonToUTMOdometry_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'odom'
#include "nav_msgs/msg/detail/odometry__struct.h"

/// Struct defined in srv/LatLonToUTMOdometry in the package smarc_msgs.
typedef struct smarc_msgs__srv__LatLonToUTMOdometry_Response
{
  nav_msgs__msg__Odometry odom;
} smarc_msgs__srv__LatLonToUTMOdometry_Response;

// Struct for a sequence of smarc_msgs__srv__LatLonToUTMOdometry_Response.
typedef struct smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence
{
  smarc_msgs__srv__LatLonToUTMOdometry_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_H_
