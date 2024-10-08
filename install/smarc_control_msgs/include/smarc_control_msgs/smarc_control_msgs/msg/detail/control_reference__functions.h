// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from smarc_control_msgs:msg/ControlReference.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__FUNCTIONS_H_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "smarc_control_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "smarc_control_msgs/msg/detail/control_reference__struct.h"

/// Initialize msg/ControlReference message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_control_msgs__msg__ControlReference
 * )) before or use
 * smarc_control_msgs__msg__ControlReference__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__init(smarc_control_msgs__msg__ControlReference * msg);

/// Finalize msg/ControlReference message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
void
smarc_control_msgs__msg__ControlReference__fini(smarc_control_msgs__msg__ControlReference * msg);

/// Create msg/ControlReference message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_control_msgs__msg__ControlReference__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
smarc_control_msgs__msg__ControlReference *
smarc_control_msgs__msg__ControlReference__create();

/// Destroy msg/ControlReference message.
/**
 * It calls
 * smarc_control_msgs__msg__ControlReference__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
void
smarc_control_msgs__msg__ControlReference__destroy(smarc_control_msgs__msg__ControlReference * msg);

/// Check for msg/ControlReference message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__are_equal(const smarc_control_msgs__msg__ControlReference * lhs, const smarc_control_msgs__msg__ControlReference * rhs);

/// Copy a msg/ControlReference message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__copy(
  const smarc_control_msgs__msg__ControlReference * input,
  smarc_control_msgs__msg__ControlReference * output);

/// Initialize array of msg/ControlReference messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_control_msgs__msg__ControlReference__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__Sequence__init(smarc_control_msgs__msg__ControlReference__Sequence * array, size_t size);

/// Finalize array of msg/ControlReference messages.
/**
 * It calls
 * smarc_control_msgs__msg__ControlReference__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
void
smarc_control_msgs__msg__ControlReference__Sequence__fini(smarc_control_msgs__msg__ControlReference__Sequence * array);

/// Create array of msg/ControlReference messages.
/**
 * It allocates the memory for the array and calls
 * smarc_control_msgs__msg__ControlReference__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
smarc_control_msgs__msg__ControlReference__Sequence *
smarc_control_msgs__msg__ControlReference__Sequence__create(size_t size);

/// Destroy array of msg/ControlReference messages.
/**
 * It calls
 * smarc_control_msgs__msg__ControlReference__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
void
smarc_control_msgs__msg__ControlReference__Sequence__destroy(smarc_control_msgs__msg__ControlReference__Sequence * array);

/// Check for msg/ControlReference message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__Sequence__are_equal(const smarc_control_msgs__msg__ControlReference__Sequence * lhs, const smarc_control_msgs__msg__ControlReference__Sequence * rhs);

/// Copy an array of msg/ControlReference messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_control_msgs
bool
smarc_control_msgs__msg__ControlReference__Sequence__copy(
  const smarc_control_msgs__msg__ControlReference__Sequence * input,
  smarc_control_msgs__msg__ControlReference__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_REFERENCE__FUNCTIONS_H_
