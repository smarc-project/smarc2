// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from sam_msgs:msg/ConsumedChargeArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__FUNCTIONS_H_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "sam_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "sam_msgs/msg/detail/consumed_charge_array__struct.h"

/// Initialize msg/ConsumedChargeArray message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * sam_msgs__msg__ConsumedChargeArray
 * )) before or use
 * sam_msgs__msg__ConsumedChargeArray__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeArray__init(sam_msgs__msg__ConsumedChargeArray * msg);

/// Finalize msg/ConsumedChargeArray message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeArray__fini(sam_msgs__msg__ConsumedChargeArray * msg);

/// Create msg/ConsumedChargeArray message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * sam_msgs__msg__ConsumedChargeArray__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__ConsumedChargeArray *
sam_msgs__msg__ConsumedChargeArray__create();

/// Destroy msg/ConsumedChargeArray message.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeArray__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeArray__destroy(sam_msgs__msg__ConsumedChargeArray * msg);

/// Check for msg/ConsumedChargeArray message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeArray__are_equal(const sam_msgs__msg__ConsumedChargeArray * lhs, const sam_msgs__msg__ConsumedChargeArray * rhs);

/// Copy a msg/ConsumedChargeArray message.
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
sam_msgs__msg__ConsumedChargeArray__copy(
  const sam_msgs__msg__ConsumedChargeArray * input,
  sam_msgs__msg__ConsumedChargeArray * output);

/// Initialize array of msg/ConsumedChargeArray messages.
/**
 * It allocates the memory for the number of elements and calls
 * sam_msgs__msg__ConsumedChargeArray__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeArray__Sequence__init(sam_msgs__msg__ConsumedChargeArray__Sequence * array, size_t size);

/// Finalize array of msg/ConsumedChargeArray messages.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeArray__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeArray__Sequence__fini(sam_msgs__msg__ConsumedChargeArray__Sequence * array);

/// Create array of msg/ConsumedChargeArray messages.
/**
 * It allocates the memory for the array and calls
 * sam_msgs__msg__ConsumedChargeArray__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__ConsumedChargeArray__Sequence *
sam_msgs__msg__ConsumedChargeArray__Sequence__create(size_t size);

/// Destroy array of msg/ConsumedChargeArray messages.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeArray__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeArray__Sequence__destroy(sam_msgs__msg__ConsumedChargeArray__Sequence * array);

/// Check for msg/ConsumedChargeArray message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeArray__Sequence__are_equal(const sam_msgs__msg__ConsumedChargeArray__Sequence * lhs, const sam_msgs__msg__ConsumedChargeArray__Sequence * rhs);

/// Copy an array of msg/ConsumedChargeArray messages.
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
sam_msgs__msg__ConsumedChargeArray__Sequence__copy(
  const sam_msgs__msg__ConsumedChargeArray__Sequence * input,
  sam_msgs__msg__ConsumedChargeArray__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__FUNCTIONS_H_
