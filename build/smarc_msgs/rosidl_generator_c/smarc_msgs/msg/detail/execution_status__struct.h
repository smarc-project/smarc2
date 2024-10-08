// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_H_

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
// Member 'execution_queue'
#include "smarc_msgs/msg/detail/sm_task__struct.h"

/// Struct defined in msg/ExecutionStatus in the package smarc_msgs.
/**
  * if true then the head of the execution_queue is currently being executed.
 */
typedef struct smarc_msgs__msg__ExecutionStatus
{
  std_msgs__msg__Header header;
  bool currently_executing;
  smarc_msgs__msg__SMTask__Sequence execution_queue;
} smarc_msgs__msg__ExecutionStatus;

// Struct for a sequence of smarc_msgs__msg__ExecutionStatus.
typedef struct smarc_msgs__msg__ExecutionStatus__Sequence
{
  smarc_msgs__msg__ExecutionStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__ExecutionStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_H_
