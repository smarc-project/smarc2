// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from smarc_mission_msgs:action/Empty.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__FUNCTIONS_H_
#define SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "smarc_mission_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "smarc_mission_msgs/action/detail/empty__struct.h"

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_Goal
 * )) before or use
 * smarc_mission_msgs__action__Empty_Goal__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__init(smarc_mission_msgs__action__Empty_Goal * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Goal__fini(smarc_mission_msgs__action__Empty_Goal * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_Goal__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Goal *
smarc_mission_msgs__action__Empty_Goal__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Goal__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Goal__destroy(smarc_mission_msgs__action__Empty_Goal * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__are_equal(const smarc_mission_msgs__action__Empty_Goal * lhs, const smarc_mission_msgs__action__Empty_Goal * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__copy(
  const smarc_mission_msgs__action__Empty_Goal * input,
  smarc_mission_msgs__action__Empty_Goal * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_Goal__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__Sequence__init(smarc_mission_msgs__action__Empty_Goal__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Goal__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Goal__Sequence__fini(smarc_mission_msgs__action__Empty_Goal__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_Goal__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Goal__Sequence *
smarc_mission_msgs__action__Empty_Goal__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Goal__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Goal__Sequence__destroy(smarc_mission_msgs__action__Empty_Goal__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__Sequence__are_equal(const smarc_mission_msgs__action__Empty_Goal__Sequence * lhs, const smarc_mission_msgs__action__Empty_Goal__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Goal__Sequence__copy(
  const smarc_mission_msgs__action__Empty_Goal__Sequence * input,
  smarc_mission_msgs__action__Empty_Goal__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_Result
 * )) before or use
 * smarc_mission_msgs__action__Empty_Result__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__init(smarc_mission_msgs__action__Empty_Result * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Result__fini(smarc_mission_msgs__action__Empty_Result * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_Result__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Result *
smarc_mission_msgs__action__Empty_Result__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Result__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Result__destroy(smarc_mission_msgs__action__Empty_Result * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__are_equal(const smarc_mission_msgs__action__Empty_Result * lhs, const smarc_mission_msgs__action__Empty_Result * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__copy(
  const smarc_mission_msgs__action__Empty_Result * input,
  smarc_mission_msgs__action__Empty_Result * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_Result__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__Sequence__init(smarc_mission_msgs__action__Empty_Result__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Result__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Result__Sequence__fini(smarc_mission_msgs__action__Empty_Result__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_Result__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Result__Sequence *
smarc_mission_msgs__action__Empty_Result__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Result__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Result__Sequence__destroy(smarc_mission_msgs__action__Empty_Result__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__Sequence__are_equal(const smarc_mission_msgs__action__Empty_Result__Sequence * lhs, const smarc_mission_msgs__action__Empty_Result__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Result__Sequence__copy(
  const smarc_mission_msgs__action__Empty_Result__Sequence * input,
  smarc_mission_msgs__action__Empty_Result__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_Feedback
 * )) before or use
 * smarc_mission_msgs__action__Empty_Feedback__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__init(smarc_mission_msgs__action__Empty_Feedback * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Feedback__fini(smarc_mission_msgs__action__Empty_Feedback * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_Feedback__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Feedback *
smarc_mission_msgs__action__Empty_Feedback__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Feedback__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Feedback__destroy(smarc_mission_msgs__action__Empty_Feedback * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__are_equal(const smarc_mission_msgs__action__Empty_Feedback * lhs, const smarc_mission_msgs__action__Empty_Feedback * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__copy(
  const smarc_mission_msgs__action__Empty_Feedback * input,
  smarc_mission_msgs__action__Empty_Feedback * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_Feedback__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__Sequence__init(smarc_mission_msgs__action__Empty_Feedback__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Feedback__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Feedback__Sequence__fini(smarc_mission_msgs__action__Empty_Feedback__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_Feedback__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_Feedback__Sequence *
smarc_mission_msgs__action__Empty_Feedback__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_Feedback__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_Feedback__Sequence__destroy(smarc_mission_msgs__action__Empty_Feedback__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__Sequence__are_equal(const smarc_mission_msgs__action__Empty_Feedback__Sequence * lhs, const smarc_mission_msgs__action__Empty_Feedback__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_Feedback__Sequence__copy(
  const smarc_mission_msgs__action__Empty_Feedback__Sequence * input,
  smarc_mission_msgs__action__Empty_Feedback__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_SendGoal_Request
 * )) before or use
 * smarc_mission_msgs__action__Empty_SendGoal_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__init(smarc_mission_msgs__action__Empty_SendGoal_Request * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Request__fini(smarc_mission_msgs__action__Empty_SendGoal_Request * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_SendGoal_Request *
smarc_mission_msgs__action__Empty_SendGoal_Request__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Request__destroy(smarc_mission_msgs__action__Empty_SendGoal_Request * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__are_equal(const smarc_mission_msgs__action__Empty_SendGoal_Request * lhs, const smarc_mission_msgs__action__Empty_SendGoal_Request * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__copy(
  const smarc_mission_msgs__action__Empty_SendGoal_Request * input,
  smarc_mission_msgs__action__Empty_SendGoal_Request * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__init(smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__fini(smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence *
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__destroy(smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__are_equal(const smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * lhs, const smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence__copy(
  const smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * input,
  smarc_mission_msgs__action__Empty_SendGoal_Request__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_SendGoal_Response
 * )) before or use
 * smarc_mission_msgs__action__Empty_SendGoal_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__init(smarc_mission_msgs__action__Empty_SendGoal_Response * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Response__fini(smarc_mission_msgs__action__Empty_SendGoal_Response * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_SendGoal_Response *
smarc_mission_msgs__action__Empty_SendGoal_Response__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Response__destroy(smarc_mission_msgs__action__Empty_SendGoal_Response * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__are_equal(const smarc_mission_msgs__action__Empty_SendGoal_Response * lhs, const smarc_mission_msgs__action__Empty_SendGoal_Response * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__copy(
  const smarc_mission_msgs__action__Empty_SendGoal_Response * input,
  smarc_mission_msgs__action__Empty_SendGoal_Response * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__init(smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__fini(smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence *
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__destroy(smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__are_equal(const smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * lhs, const smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence__copy(
  const smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * input,
  smarc_mission_msgs__action__Empty_SendGoal_Response__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_GetResult_Request
 * )) before or use
 * smarc_mission_msgs__action__Empty_GetResult_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__init(smarc_mission_msgs__action__Empty_GetResult_Request * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Request__fini(smarc_mission_msgs__action__Empty_GetResult_Request * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_GetResult_Request *
smarc_mission_msgs__action__Empty_GetResult_Request__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Request__destroy(smarc_mission_msgs__action__Empty_GetResult_Request * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__are_equal(const smarc_mission_msgs__action__Empty_GetResult_Request * lhs, const smarc_mission_msgs__action__Empty_GetResult_Request * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__copy(
  const smarc_mission_msgs__action__Empty_GetResult_Request * input,
  smarc_mission_msgs__action__Empty_GetResult_Request * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__init(smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__fini(smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence *
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__destroy(smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__are_equal(const smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * lhs, const smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Request__Sequence__copy(
  const smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * input,
  smarc_mission_msgs__action__Empty_GetResult_Request__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_GetResult_Response
 * )) before or use
 * smarc_mission_msgs__action__Empty_GetResult_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__init(smarc_mission_msgs__action__Empty_GetResult_Response * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Response__fini(smarc_mission_msgs__action__Empty_GetResult_Response * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_GetResult_Response *
smarc_mission_msgs__action__Empty_GetResult_Response__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Response__destroy(smarc_mission_msgs__action__Empty_GetResult_Response * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__are_equal(const smarc_mission_msgs__action__Empty_GetResult_Response * lhs, const smarc_mission_msgs__action__Empty_GetResult_Response * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__copy(
  const smarc_mission_msgs__action__Empty_GetResult_Response * input,
  smarc_mission_msgs__action__Empty_GetResult_Response * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__init(smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__fini(smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence *
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__destroy(smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__are_equal(const smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * lhs, const smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_GetResult_Response__Sequence__copy(
  const smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * input,
  smarc_mission_msgs__action__Empty_GetResult_Response__Sequence * output);

/// Initialize action/Empty message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__action__Empty_FeedbackMessage
 * )) before or use
 * smarc_mission_msgs__action__Empty_FeedbackMessage__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__init(smarc_mission_msgs__action__Empty_FeedbackMessage * msg);

/// Finalize action/Empty message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_FeedbackMessage__fini(smarc_mission_msgs__action__Empty_FeedbackMessage * msg);

/// Create action/Empty message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_FeedbackMessage *
smarc_mission_msgs__action__Empty_FeedbackMessage__create();

/// Destroy action/Empty message.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_FeedbackMessage__destroy(smarc_mission_msgs__action__Empty_FeedbackMessage * msg);

/// Check for action/Empty message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__are_equal(const smarc_mission_msgs__action__Empty_FeedbackMessage * lhs, const smarc_mission_msgs__action__Empty_FeedbackMessage * rhs);

/// Copy a action/Empty message.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__copy(
  const smarc_mission_msgs__action__Empty_FeedbackMessage * input,
  smarc_mission_msgs__action__Empty_FeedbackMessage * output);

/// Initialize array of action/Empty messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__init(smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * array, size_t size);

/// Finalize array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__fini(smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * array);

/// Create array of action/Empty messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence *
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__create(size_t size);

/// Destroy array of action/Empty messages.
/**
 * It calls
 * smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__destroy(smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * array);

/// Check for action/Empty message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__are_equal(const smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * lhs, const smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * rhs);

/// Copy an array of action/Empty messages.
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
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence__copy(
  const smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * input,
  smarc_mission_msgs__action__Empty_FeedbackMessage__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__FUNCTIONS_H_
