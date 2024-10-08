// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__FUNCTIONS_H_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "sam_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "sam_msgs/msg/detail/uavcan_node_status__struct.h"

/// Initialize msg/UavcanNodeStatus message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * sam_msgs__msg__UavcanNodeStatus
 * )) before or use
 * sam_msgs__msg__UavcanNodeStatus__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__init(sam_msgs__msg__UavcanNodeStatus * msg);

/// Finalize msg/UavcanNodeStatus message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__UavcanNodeStatus__fini(sam_msgs__msg__UavcanNodeStatus * msg);

/// Create msg/UavcanNodeStatus message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * sam_msgs__msg__UavcanNodeStatus__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__UavcanNodeStatus *
sam_msgs__msg__UavcanNodeStatus__create();

/// Destroy msg/UavcanNodeStatus message.
/**
 * It calls
 * sam_msgs__msg__UavcanNodeStatus__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__UavcanNodeStatus__destroy(sam_msgs__msg__UavcanNodeStatus * msg);

/// Check for msg/UavcanNodeStatus message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__are_equal(const sam_msgs__msg__UavcanNodeStatus * lhs, const sam_msgs__msg__UavcanNodeStatus * rhs);

/// Copy a msg/UavcanNodeStatus message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__copy(
  const sam_msgs__msg__UavcanNodeStatus * input,
  sam_msgs__msg__UavcanNodeStatus * output);

/// Initialize array of msg/UavcanNodeStatus messages.
/**
 * It allocates the memory for the number of elements and calls
 * sam_msgs__msg__UavcanNodeStatus__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__Sequence__init(sam_msgs__msg__UavcanNodeStatus__Sequence * array, size_t size);

/// Finalize array of msg/UavcanNodeStatus messages.
/**
 * It calls
 * sam_msgs__msg__UavcanNodeStatus__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__UavcanNodeStatus__Sequence__fini(sam_msgs__msg__UavcanNodeStatus__Sequence * array);

/// Create array of msg/UavcanNodeStatus messages.
/**
 * It allocates the memory for the array and calls
 * sam_msgs__msg__UavcanNodeStatus__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__UavcanNodeStatus__Sequence *
sam_msgs__msg__UavcanNodeStatus__Sequence__create(size_t size);

/// Destroy array of msg/UavcanNodeStatus messages.
/**
 * It calls
 * sam_msgs__msg__UavcanNodeStatus__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__UavcanNodeStatus__Sequence__destroy(sam_msgs__msg__UavcanNodeStatus__Sequence * array);

/// Check for msg/UavcanNodeStatus message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__Sequence__are_equal(const sam_msgs__msg__UavcanNodeStatus__Sequence * lhs, const sam_msgs__msg__UavcanNodeStatus__Sequence * rhs);

/// Copy an array of msg/UavcanNodeStatus messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__UavcanNodeStatus__Sequence__copy(
  const sam_msgs__msg__UavcanNodeStatus__Sequence * input,
  sam_msgs__msg__UavcanNodeStatus__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__FUNCTIONS_H_
