// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_graph_slam_2_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
#define SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'MAP_LINE_DEPTH_TOPIC'.
/**
  * MAP
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__MAP_LINE_DEPTH_TOPIC = "map/line_depth";

/// Constant 'MAP_POINT_FEATURE_TOPIC'.
static const char * const sam_graph_slam_2_msgs__msg__Topics__MAP_POINT_FEATURE_TOPIC = "map/point_features";

/// Constant 'MAP_LINE_FEATURE_TOPIC'.
static const char * const sam_graph_slam_2_msgs__msg__Topics__MAP_LINE_FEATURE_TOPIC = "map/line_features";

/// Constant 'MAP_MARKED_LINE_SPHERES_TOPIC'.
static const char * const sam_graph_slam_2_msgs__msg__Topics__MAP_MARKED_LINE_SPHERES_TOPIC = "map/marked_lines_spheres";

/// Constant 'MAP_MARKED_LINE_LINES_TOPIC'.
static const char * const sam_graph_slam_2_msgs__msg__Topics__MAP_MARKED_LINE_LINES_TOPIC = "map/marked_lines_lines";

/// Constant 'DETECTOR_HYPOTH_TOPIC'.
/**
  * Detector
  *
  * Msg type: Detection2DArray
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__DETECTOR_HYPOTH_TOPIC = "payload/sidescan/detection_hypothesis";

/// Constant 'DETECTOR_MARKER_TOPIC'.
/**
  * Msg type:MarkerArray
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__DETECTOR_MARKER_TOPIC = "payload/sidescan/detection_markers";

/// Constant 'DETECTOR_RAW_SSS_TOPIC'.
/**
  * Msg type: Image
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__DETECTOR_RAW_SSS_TOPIC = "payload/sidescan/image";

/// Constant 'DETECTOR_MARKED_SSS_TOPIC'.
/**
  * Msg Type: Image
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__DETECTOR_MARKED_SSS_TOPIC = "payload/sidescan/detection_hypothesis_image";

/// Constant 'DR_ODOM_TOPIC'.
/**
  * Dead reckoning
  *
  * This is only intended for use with the temporary DR, defined in pipeline_slam_dr_gt_publisher
 */
static const char * const sam_graph_slam_2_msgs__msg__Topics__DR_ODOM_TOPIC = "graph_dr/dr_odom";

/// Constant 'GT_ODOM_TOPIC'.
static const char * const sam_graph_slam_2_msgs__msg__Topics__GT_ODOM_TOPIC = "graph_dr/gt_odom";

/// Struct defined in msg/Topics in the package sam_graph_slam_2_msgs.
/**
  * This is a file that defines all the topics of sam_graph_slam_2.
  * This package is relevant to localization in semi-structured environments with detectable point or line features.
  * Specifically involving the algae farm.
  * It is assumed that the nodes will namespace as needed.
 */
typedef struct sam_graph_slam_2_msgs__msg__Topics
{
  uint8_t structure_needs_at_least_one_member;
} sam_graph_slam_2_msgs__msg__Topics;

// Struct for a sequence of sam_graph_slam_2_msgs__msg__Topics.
typedef struct sam_graph_slam_2_msgs__msg__Topics__Sequence
{
  sam_graph_slam_2_msgs__msg__Topics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_graph_slam_2_msgs__msg__Topics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_H_
