// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'MAX_BROADCASTING_PERIOD_MS'.
/**
  * Publication period may vary within these limits.
  * It is NOT recommended to change it at run time.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MAX_BROADCASTING_PERIOD_MS = 1000
};

/// Constant 'MIN_BROADCASTING_PERIOD_MS'.
enum
{
  sam_msgs__msg__UavcanNodeStatus__MIN_BROADCASTING_PERIOD_MS = 2
};

/// Constant 'OFFLINE_TIMEOUT_MS'.
/**
  * If a node fails to publish this message in this amount of time, it should be considered offline.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__OFFLINE_TIMEOUT_MS = 3000
};

/// Constant 'HEALTH_OK'.
/**
  * Abstract node health.
  *
  * The node is functioning properly.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__HEALTH_OK = 0
};

/// Constant 'HEALTH_WARNING'.
/**
  * A critical parameter went out of range or the node encountered a minor failure.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__HEALTH_WARNING = 1
};

/// Constant 'HEALTH_ERROR'.
/**
  * The node encountered a major failure.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__HEALTH_ERROR = 2
};

/// Constant 'HEALTH_CRITICAL'.
/**
  * The node suffered a fatal malfunction.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__HEALTH_CRITICAL = 3
};

/// Constant 'MODE_OPERATIONAL'.
/**
  * Current mode.
  *
  * Mode OFFLINE can be actually reported by the node to explicitly inform other network
  * participants that the sending node is about to shutdown. In this case other nodes will not
  * have to wait OFFLINE_TIMEOUT_MS before they detect that the node is no longer available.
  *
  * Reserved values can be used in future revisions of the specification.
  *
  * Node is performing its main functions.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MODE_OPERATIONAL = 0
};

/// Constant 'MODE_INITIALIZATION'.
/**
  * Node is initializing; this mode is entered immediately after startup.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MODE_INITIALIZATION = 1
};

/// Constant 'MODE_MAINTENANCE'.
/**
  * Node is under maintenance.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MODE_MAINTENANCE = 2
};

/// Constant 'MODE_SOFTWARE_UPDATE'.
/**
  * Node is in the process of updating its software.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MODE_SOFTWARE_UPDATE = 3
};

/// Constant 'MODE_OFFLINE'.
/**
  * Node is no longer available.
 */
enum
{
  sam_msgs__msg__UavcanNodeStatus__MODE_OFFLINE = 7
};

/// Struct defined in msg/UavcanNodeStatus in the package sam_msgs.
/**
  * Abstract node status information.
  *
  * Any UAVCAN node is required to publish this message periodically.
 */
typedef struct sam_msgs__msg__UavcanNodeStatus
{
  /// Uptime counter should never overflow.
  /// Other nodes may detect that a remote node has restarted when this value goes backwards.
  uint32_t uptime_sec;
  uint8_t health;
  uint8_t mode;
  /// Not used currently, keep zero when publishing, ignore when receiving.
  uint8_t sub_mode;
  /// Optional, vendor-specific node status code, e.g. a fault code or a status bitmask.
  uint16_t vendor_specific_status_code;
} sam_msgs__msg__UavcanNodeStatus;

// Struct for a sequence of sam_msgs__msg__UavcanNodeStatus.
typedef struct sam_msgs__msg__UavcanNodeStatus__Sequence
{
  sam_msgs__msg__UavcanNodeStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__UavcanNodeStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_H_
