// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_H_
#define SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'IS_FULL'.
/**
  * Battery is full right now
 */
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Request__IS_FULL = 1
};

/// Constant 'WAS_FULL'.
/**
  * Battery was full when Sam started
 */
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Request__WAS_FULL = 2
};

/// Constant 'ADD_CHARGE'.
/**
  * Add enclosed charge
 */
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Request__ADD_CHARGE = 3
};

/// Constant 'ON_MAINS'.
/**
  * Powered externally
 */
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Request__ON_MAINS = 4
};

/// Struct defined in srv/UavcanUpdateBattery in the package sam_msgs.
typedef struct sam_msgs__srv__UavcanUpdateBattery_Request
{
  uint8_t node_id;
  uint8_t command;
  /// Ah (can be negative)
  float charge;
} sam_msgs__srv__UavcanUpdateBattery_Request;

// Struct for a sequence of sam_msgs__srv__UavcanUpdateBattery_Request.
typedef struct sam_msgs__srv__UavcanUpdateBattery_Request__Sequence
{
  sam_msgs__srv__UavcanUpdateBattery_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__srv__UavcanUpdateBattery_Request__Sequence;


// Constants defined in the message

/// Constant 'UPDATE_SUCCESSFULL'.
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Response__UPDATE_SUCCESSFULL = 1
};

/// Constant 'UPDATE_FAILED'.
enum
{
  sam_msgs__srv__UavcanUpdateBattery_Response__UPDATE_FAILED = 0
};

/// Struct defined in srv/UavcanUpdateBattery in the package sam_msgs.
typedef struct sam_msgs__srv__UavcanUpdateBattery_Response
{
  uint8_t success;
} sam_msgs__srv__UavcanUpdateBattery_Response;

// Struct for a sequence of sam_msgs__srv__UavcanUpdateBattery_Response.
typedef struct sam_msgs__srv__UavcanUpdateBattery_Response__Sequence
{
  sam_msgs__srv__UavcanUpdateBattery_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__srv__UavcanUpdateBattery_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_H_
