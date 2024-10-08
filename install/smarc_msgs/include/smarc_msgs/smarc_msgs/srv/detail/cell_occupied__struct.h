// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:srv/CellOccupied.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_H_
#define SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/CellOccupied in the package smarc_msgs.
typedef struct smarc_msgs__srv__CellOccupied_Request
{
  float x;
  float y;
} smarc_msgs__srv__CellOccupied_Request;

// Struct for a sequence of smarc_msgs__srv__CellOccupied_Request.
typedef struct smarc_msgs__srv__CellOccupied_Request__Sequence
{
  smarc_msgs__srv__CellOccupied_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__CellOccupied_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/CellOccupied in the package smarc_msgs.
typedef struct smarc_msgs__srv__CellOccupied_Response
{
  uint8_t cost;
} smarc_msgs__srv__CellOccupied_Response;

// Struct for a sequence of smarc_msgs__srv__CellOccupied_Response.
typedef struct smarc_msgs__srv__CellOccupied_Response__Sequence
{
  smarc_msgs__srv__CellOccupied_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__srv__CellOccupied_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_H_
