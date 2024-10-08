// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from dead_reckoning_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'DR_ODOM_TOPIC'.
/**
  * Dead reckoning topics
  *
  * DR node
  * Type: Odometry
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_TOPIC = "dr/odom";

/// Constant 'DR_DEPTH_POSE_TOPIC'.
/**
  * Type: PoseWithCovarianceStamped
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_DEPTH_POSE_TOPIC = "dr/depth_pose";

/// Constant 'DR_GPS_ODOM_TOPIC'.
/**
  * Type: Odometry
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_GPS_ODOM_TOPIC = "dr/gps_odom";

/// Constant 'DR_ROLL_TOPIC'.
/**
  * IMU
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ROLL_TOPIC = "dr/roll";

/// Constant 'DR_PITCH_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_PITCH_TOPIC = "dr/pitch";

/// Constant 'DR_YAW_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_YAW_TOPIC = "dr/yaw";

/// Constant 'DR_DEPTH_TOPIC'.
/**
  * DEPTH
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_DEPTH_TOPIC = "dr/depth";

/// Constant 'DR_COMPASS_HEADING_TOPIC'.
/**
  * Other
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_COMPASS_HEADING_TOPIC = "dr/compass_heading";

/// Constant 'DR_LAT_LON_TOPIC'.
/**
  * Type: GeoPoint
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_LAT_LON_TOPIC = "dr/lat_lon";

/// Constant 'DR_ODOM_X_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_X_TOPIC = "dr/x";

/// Constant 'DR_ODOM_Y_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_Y_TOPIC = "dr/y";

/// Constant 'DR_ODOM_Z_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_Z_TOPIC = "dr/z";

/// Constant 'DR_ODOM_U_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_U_TOPIC = "dr/u";

/// Constant 'DR_ODOM_V_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_V_TOPIC = "dr/v";

/// Constant 'DR_ODOM_W_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_W_TOPIC = "dr/w";

/// Constant 'DR_ODOM_P_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_P_TOPIC = "dr/p";

/// Constant 'DR_ODOM_Q_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_Q_TOPIC = "dr/q";

/// Constant 'DR_ODOM_R_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_R_TOPIC = "dr/r";

/// Constant 'DR_ODOM_ALT_TOPIC'.
/**
  * Type: Float64
 */
static const char * const dead_reckoning_msgs__msg__Topics__DR_ODOM_ALT_TOPIC = "dr/alt";

/// Struct defined in msg/Topics in the package dead_reckoning_msgs.
/**
  * This is a file that defines all the topics of dead reckoning.
  * The goal is to have one location that all cpp/py scripts
  * can easily access and thus avoid having 100 parameters for topics all
  * over the place, repeated for all subs/pubs...
  * It is assumed that the nodes will namespace as needed.
 */
typedef struct dead_reckoning_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} dead_reckoning_msgs__msg__Topics;

// Struct for a sequence of dead_reckoning_msgs__msg__Topics.
typedef struct dead_reckoning_msgs__msg__Topics__Sequence
{
  dead_reckoning_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} dead_reckoning_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
