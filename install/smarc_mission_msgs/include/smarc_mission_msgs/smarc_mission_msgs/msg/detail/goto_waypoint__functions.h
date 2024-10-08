// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__FUNCTIONS_H_
#define SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "smarc_mission_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.h"

/// Initialize msg/GotoWaypoint message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smarc_mission_msgs__msg__GotoWaypoint
 * )) before or use
 * smarc_mission_msgs__msg__GotoWaypoint__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__msg__GotoWaypoint__init(smarc_mission_msgs__msg__GotoWaypoint * msg);

/// Finalize msg/GotoWaypoint message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__msg__GotoWaypoint__fini(smarc_mission_msgs__msg__GotoWaypoint * msg);

/// Create msg/GotoWaypoint message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smarc_mission_msgs__msg__GotoWaypoint__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__msg__GotoWaypoint *
smarc_mission_msgs__msg__GotoWaypoint__create();

/// Destroy msg/GotoWaypoint message.
/**
 * It calls
 * smarc_mission_msgs__msg__GotoWaypoint__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__msg__GotoWaypoint__destroy(smarc_mission_msgs__msg__GotoWaypoint * msg);

/// Check for msg/GotoWaypoint message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__msg__GotoWaypoint__are_equal(const smarc_mission_msgs__msg__GotoWaypoint * lhs, const smarc_mission_msgs__msg__GotoWaypoint * rhs);

/// Copy a msg/GotoWaypoint message.
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
smarc_mission_msgs__msg__GotoWaypoint__copy(
  const smarc_mission_msgs__msg__GotoWaypoint * input,
  smarc_mission_msgs__msg__GotoWaypoint * output);

/// Initialize array of msg/GotoWaypoint messages.
/**
 * It allocates the memory for the number of elements and calls
 * smarc_mission_msgs__msg__GotoWaypoint__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__msg__GotoWaypoint__Sequence__init(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array, size_t size);

/// Finalize array of msg/GotoWaypoint messages.
/**
 * It calls
 * smarc_mission_msgs__msg__GotoWaypoint__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array);

/// Create array of msg/GotoWaypoint messages.
/**
 * It allocates the memory for the array and calls
 * smarc_mission_msgs__msg__GotoWaypoint__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
smarc_mission_msgs__msg__GotoWaypoint__Sequence *
smarc_mission_msgs__msg__GotoWaypoint__Sequence__create(size_t size);

/// Destroy array of msg/GotoWaypoint messages.
/**
 * It calls
 * smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
void
smarc_mission_msgs__msg__GotoWaypoint__Sequence__destroy(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array);

/// Check for msg/GotoWaypoint message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smarc_mission_msgs
bool
smarc_mission_msgs__msg__GotoWaypoint__Sequence__are_equal(const smarc_mission_msgs__msg__GotoWaypoint__Sequence * lhs, const smarc_mission_msgs__msg__GotoWaypoint__Sequence * rhs);

/// Copy an array of msg/GotoWaypoint messages.
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
smarc_mission_msgs__msg__GotoWaypoint__Sequence__copy(
  const smarc_mission_msgs__msg__GotoWaypoint__Sequence * input,
  smarc_mission_msgs__msg__GotoWaypoint__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__FUNCTIONS_H_
