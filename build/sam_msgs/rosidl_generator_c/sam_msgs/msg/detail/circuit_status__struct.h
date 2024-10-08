// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/CircuitStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'ERROR_FLAG_OVERVOLTAGE'.
enum
{
  sam_msgs__msg__CircuitStatus__ERROR_FLAG_OVERVOLTAGE = 1
};

/// Constant 'ERROR_FLAG_UNDERVOLTAGE'.
enum
{
  sam_msgs__msg__CircuitStatus__ERROR_FLAG_UNDERVOLTAGE = 2
};

/// Constant 'ERROR_FLAG_OVERCURRENT'.
enum
{
  sam_msgs__msg__CircuitStatus__ERROR_FLAG_OVERCURRENT = 4
};

/// Constant 'ERROR_FLAG_UNDERCURRENT'.
enum
{
  sam_msgs__msg__CircuitStatus__ERROR_FLAG_UNDERCURRENT = 8
};

/// Struct defined in msg/CircuitStatus in the package sam_msgs.
/**
  * From uavcan CiruitStatus msg: Generic electrical circuit info.
 */
typedef struct sam_msgs__msg__CircuitStatus
{
  uint8_t error_flags;
  uint16_t circuit_id;
  float voltage;
  float current;
} sam_msgs__msg__CircuitStatus;

// Struct for a sequence of sam_msgs__msg__CircuitStatus.
typedef struct sam_msgs__msg__CircuitStatus__Sequence
{
  sam_msgs__msg__CircuitStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__CircuitStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_H_
