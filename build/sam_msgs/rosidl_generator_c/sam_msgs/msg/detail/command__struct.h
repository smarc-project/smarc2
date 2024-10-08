// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from sam_msgs:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_H_
#define SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'COMMAND_TYPE_UNITLESS'.
/**
  * Whether the units are linear or angular depends on the actuator type.
  *
  * [-1, 1]
 */
enum
{
  sam_msgs__msg__Command__COMMAND_TYPE_UNITLESS = 0
};

/// Constant 'COMMAND_TYPE_POSITION'.
/**
  * meter or radian
 */
enum
{
  sam_msgs__msg__Command__COMMAND_TYPE_POSITION = 1
};

/// Constant 'COMMAND_TYPE_FORCE'.
/**
  * Newton or Newton metre
 */
enum
{
  sam_msgs__msg__Command__COMMAND_TYPE_FORCE = 2
};

/// Constant 'COMMAND_TYPE_SPEED'.
/**
  * meter per second or radian per second
 */
enum
{
  sam_msgs__msg__Command__COMMAND_TYPE_SPEED = 3
};

/// Struct defined in msg/Command in the package sam_msgs.
/**
  * Nested type.
  * Single actuator command.
 */
typedef struct sam_msgs__msg__Command
{
  uint8_t actuator_id;
  uint8_t command_type;
  /// Value of the above type
  float command_value;
} sam_msgs__msg__Command;

// Struct for a sequence of sam_msgs__msg__Command.
typedef struct sam_msgs__msg__Command__Sequence
{
  sam_msgs__msg__Command * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} sam_msgs__msg__Command__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_H_
