// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__FUNCTIONS_H_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "sam_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "sam_msgs/msg/detail/consumed_charge_feedback__struct.h"

/// Initialize msg/ConsumedChargeFeedback message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * sam_msgs__msg__ConsumedChargeFeedback
 * )) before or use
 * sam_msgs__msg__ConsumedChargeFeedback__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeFeedback__init(sam_msgs__msg__ConsumedChargeFeedback * msg);

/// Finalize msg/ConsumedChargeFeedback message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeFeedback__fini(sam_msgs__msg__ConsumedChargeFeedback * msg);

/// Create msg/ConsumedChargeFeedback message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * sam_msgs__msg__ConsumedChargeFeedback__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__ConsumedChargeFeedback *
sam_msgs__msg__ConsumedChargeFeedback__create();

/// Destroy msg/ConsumedChargeFeedback message.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeFeedback__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeFeedback__destroy(sam_msgs__msg__ConsumedChargeFeedback * msg);

/// Check for msg/ConsumedChargeFeedback message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeFeedback__are_equal(const sam_msgs__msg__ConsumedChargeFeedback * lhs, const sam_msgs__msg__ConsumedChargeFeedback * rhs);

/// Copy a msg/ConsumedChargeFeedback message.
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
sam_msgs__msg__ConsumedChargeFeedback__copy(
  const sam_msgs__msg__ConsumedChargeFeedback * input,
  sam_msgs__msg__ConsumedChargeFeedback * output);

/// Initialize array of msg/ConsumedChargeFeedback messages.
/**
 * It allocates the memory for the number of elements and calls
 * sam_msgs__msg__ConsumedChargeFeedback__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeFeedback__Sequence__init(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array, size_t size);

/// Finalize array of msg/ConsumedChargeFeedback messages.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeFeedback__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeFeedback__Sequence__fini(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array);

/// Create array of msg/ConsumedChargeFeedback messages.
/**
 * It allocates the memory for the array and calls
 * sam_msgs__msg__ConsumedChargeFeedback__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
sam_msgs__msg__ConsumedChargeFeedback__Sequence *
sam_msgs__msg__ConsumedChargeFeedback__Sequence__create(size_t size);

/// Destroy array of msg/ConsumedChargeFeedback messages.
/**
 * It calls
 * sam_msgs__msg__ConsumedChargeFeedback__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
void
sam_msgs__msg__ConsumedChargeFeedback__Sequence__destroy(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array);

/// Check for msg/ConsumedChargeFeedback message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_sam_msgs
bool
sam_msgs__msg__ConsumedChargeFeedback__Sequence__are_equal(const sam_msgs__msg__ConsumedChargeFeedback__Sequence * lhs, const sam_msgs__msg__ConsumedChargeFeedback__Sequence * rhs);

/// Copy an array of msg/ConsumedChargeFeedback messages.
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
sam_msgs__msg__ConsumedChargeFeedback__Sequence__copy(
  const sam_msgs__msg__ConsumedChargeFeedback__Sequence * input,
  sam_msgs__msg__ConsumedChargeFeedback__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__FUNCTIONS_H_
