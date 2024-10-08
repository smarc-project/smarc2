// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:srv/AddTasks.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_H_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'tasks'
#include "smarc_msgs/msg/detail/sm_task__struct.h"

/// Struct defined in srv/AddTasks in the package smarc_msgs.
typedef struct smarc_msgs__srv__AddTasks_Request
{
  smarc_msgs__msg__SMTask__Sequence tasks;
} smarc_msgs__srv__AddTasks_Request;

// Struct for a sequence of smarc_msgs__srv__AddTasks_Request.
typedef struct smarc_msgs__srv__AddTasks_Request__Sequence
{
  smarc_msgs__srv__AddTasks_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__AddTasks_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/AddTasks in the package smarc_msgs.
typedef struct smarc_msgs__srv__AddTasks_Response
{
  uint64_t task_id;
} smarc_msgs__srv__AddTasks_Response;

// Struct for a sequence of smarc_msgs__srv__AddTasks_Response.
typedef struct smarc_msgs__srv__AddTasks_Response__Sequence
{
  smarc_msgs__srv__AddTasks_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__AddTasks_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_H_
