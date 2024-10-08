// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from sam_msgs:msg/CircuitStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__FUNCTIONS_H_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "sam_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "sam_msgs/msg/detail/circuit_status__struct.h"

/// Initialize msg/CircuitStatus message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * sam_msgs__msg__CircuitStatus
 * )) before or use
 * sam_msgs__msg__CircuitStatus__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__CircuitStatus__init(sam_msgs__msg__CircuitStatus * msg);

/// Finalize msg/CircuitStatus message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__CircuitStatus__fini(sam_msgs__msg__CircuitStatus * msg);

/// Create msg/CircuitStatus message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * sam_msgs__msg__CircuitStatus__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__CircuitStatus *
sam_msgs__msg__CircuitStatus__create();

/// Destroy msg/CircuitStatus message.
/**
 * It calls
 * sam_msgs__msg__CircuitStatus__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__CircuitStatus__destroy(sam_msgs__msg__CircuitStatus * msg);

/// Check for msg/CircuitStatus message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__CircuitStatus__are_equal(const sam_msgs__msg__CircuitStatus * lhs, const sam_msgs__msg__CircuitStatus * rhs);

/// Copy a msg/CircuitStatus message.
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
sam_msgs__msg__CircuitStatus__copy(
  const sam_msgs__msg__CircuitStatus * input,
  sam_msgs__msg__CircuitStatus * output);

/// Initialize array of msg/CircuitStatus messages.
/**
 * It allocates the memory for the number of elements and calls
 * sam_msgs__msg__CircuitStatus__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__CircuitStatus__Sequence__init(sam_msgs__msg__CircuitStatus__Sequence * array, size_t size);

/// Finalize array of msg/CircuitStatus messages.
/**
 * It calls
 * sam_msgs__msg__CircuitStatus__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__CircuitStatus__Sequence__fini(sam_msgs__msg__CircuitStatus__Sequence * array);

/// Create array of msg/CircuitStatus messages.
/**
 * It allocates the memory for the array and calls
 * sam_msgs__msg__CircuitStatus__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__CircuitStatus__Sequence *
sam_msgs__msg__CircuitStatus__Sequence__create(size_t size);

/// Destroy array of msg/CircuitStatus messages.
/**
 * It calls
 * sam_msgs__msg__CircuitStatus__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__CircuitStatus__Sequence__destroy(sam_msgs__msg__CircuitStatus__Sequence * array);

/// Check for msg/CircuitStatus message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__CircuitStatus__Sequence__are_equal(const sam_msgs__msg__CircuitStatus__Sequence * lhs, const sam_msgs__msg__CircuitStatus__Sequence * rhs);

/// Copy an array of msg/CircuitStatus messages.
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
sam_msgs__msg__CircuitStatus__Sequence__copy(
  const sam_msgs__msg__CircuitStatus__Sequence * input,
  sam_msgs__msg__CircuitStatus__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__FUNCTIONS_H_
