// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'lat_lon_pose'
#include "geographic_msgs/msg/detail/geo_pose__struct.h"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist_with_covariance__struct.h"

/// Struct defined in msg/LatLonOdometry in the package smarc_msgs.
/**
  * This represents an estimate of a position and velocity in free space.  
 */
typedef struct smarc_msgs__msg__LatLonOdometry
{
  std_msgs__msg__Header header;
  geographic_msgs__msg__GeoPose lat_lon_pose;
  /// Row-major representation of the 6x6 covariance matrix
  /// The orientation parameters use a fixed-axis representation.
  /// In order, the parameters are:
  /// (x, y, z, rotation about X axis, rotation about Y axis, rotation about Z axis)
  double covariance[36];
  geometry_msgs__msg__TwistWithCovariance twist;
} smarc_msgs__msg__LatLonOdometry;

// Struct for a sequence of smarc_msgs__msg__LatLonOdometry.
typedef struct smarc_msgs__msg__LatLonOdometry__Sequence
{
  smarc_msgs__msg__LatLonOdometry * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__LatLonOdometry__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_H_
