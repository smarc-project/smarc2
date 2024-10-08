// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_mission_msgs:action/GotoWaypoint.idl
// generated code does not contain a copyright notice
#include "smarc_mission_msgs/action/detail/goto_waypoint__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `waypoint`
#include "smarc_mission_msgs/msg/detail/goto_waypoint__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_Goal__init(smarc_mission_msgs__action__GotoWaypoint_Goal * msg)
{
  if (!msg) {
    return false;
  }
  // waypoint
  if (!smarc_mission_msgs__msg__GotoWaypoint__init(&msg->waypoint)) {
    smarc_mission_msgs__action__GotoWaypoint_Goal__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Goal__fini(smarc_mission_msgs__action__GotoWaypoint_Goal * msg)
{
  if (!msg) {
    return;
  }
  // waypoint
  smarc_mission_msgs__msg__GotoWaypoint__fini(&msg->waypoint);
}

bool
smarc_mission_msgs__action__GotoWaypoint_Goal__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Goal * lhs, const smarc_mission_msgs__action__GotoWaypoint_Goal * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // waypoint
  if (!smarc_mission_msgs__msg__GotoWaypoint__are_equal(
      &(lhs->waypoint), &(rhs->waypoint)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Goal__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Goal * input,
  smarc_mission_msgs__action__GotoWaypoint_Goal * output)
{
  if (!input || !output) {
    return false;
  }
  // waypoint
  if (!smarc_mission_msgs__msg__GotoWaypoint__copy(
      &(input->waypoint), &(output->waypoint)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_Goal *
smarc_mission_msgs__action__GotoWaypoint_Goal__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Goal * msg = (smarc_mission_msgs__action__GotoWaypoint_Goal *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Goal), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_Goal));
  bool success = smarc_mission_msgs__action__GotoWaypoint_Goal__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_Goal__destroy(smarc_mission_msgs__action__GotoWaypoint_Goal * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_Goal__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Goal * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_Goal *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_Goal), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_Goal__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_Goal__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_Goal__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence *
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Goal__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_Goal__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_Goal);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_Goal * data =
      (smarc_mission_msgs__action__GotoWaypoint_Goal *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_Goal__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_Goal__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Goal__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
smarc_mission_msgs__action__GotoWaypoint_Result__init(smarc_mission_msgs__action__GotoWaypoint_Result * msg)
{
  if (!msg) {
    return false;
  }
  // reached_waypoint
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Result__fini(smarc_mission_msgs__action__GotoWaypoint_Result * msg)
{
  if (!msg) {
    return;
  }
  // reached_waypoint
}

bool
smarc_mission_msgs__action__GotoWaypoint_Result__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Result * lhs, const smarc_mission_msgs__action__GotoWaypoint_Result * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // reached_waypoint
  if (lhs->reached_waypoint != rhs->reached_waypoint) {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Result__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Result * input,
  smarc_mission_msgs__action__GotoWaypoint_Result * output)
{
  if (!input || !output) {
    return false;
  }
  // reached_waypoint
  output->reached_waypoint = input->reached_waypoint;
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_Result *
smarc_mission_msgs__action__GotoWaypoint_Result__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Result * msg = (smarc_mission_msgs__action__GotoWaypoint_Result *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Result), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_Result));
  bool success = smarc_mission_msgs__action__GotoWaypoint_Result__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_Result__destroy(smarc_mission_msgs__action__GotoWaypoint_Result * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_Result__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Result * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_Result *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_Result), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_Result__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_Result__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_Result__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_Result__Sequence *
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_Result__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Result__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Result__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Result__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_Result__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_Result);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_Result * data =
      (smarc_mission_msgs__action__GotoWaypoint_Result *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_Result__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_Result__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Result__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `time_remaining`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `feedback_message`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__init(smarc_mission_msgs__action__GotoWaypoint_Feedback * msg)
{
  if (!msg) {
    return false;
  }
  // time_remaining
  if (!builtin_interfaces__msg__Time__init(&msg->time_remaining)) {
    smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(msg);
    return false;
  }
  // feedback_message
  if (!rosidl_runtime_c__String__init(&msg->feedback_message)) {
    smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(msg);
    return false;
  }
  // distance_remaining
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(smarc_mission_msgs__action__GotoWaypoint_Feedback * msg)
{
  if (!msg) {
    return;
  }
  // time_remaining
  builtin_interfaces__msg__Time__fini(&msg->time_remaining);
  // feedback_message
  rosidl_runtime_c__String__fini(&msg->feedback_message);
  // distance_remaining
}

bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Feedback * lhs, const smarc_mission_msgs__action__GotoWaypoint_Feedback * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // time_remaining
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->time_remaining), &(rhs->time_remaining)))
  {
    return false;
  }
  // feedback_message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->feedback_message), &(rhs->feedback_message)))
  {
    return false;
  }
  // distance_remaining
  if (lhs->distance_remaining != rhs->distance_remaining) {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Feedback * input,
  smarc_mission_msgs__action__GotoWaypoint_Feedback * output)
{
  if (!input || !output) {
    return false;
  }
  // time_remaining
  if (!builtin_interfaces__msg__Time__copy(
      &(input->time_remaining), &(output->time_remaining)))
  {
    return false;
  }
  // feedback_message
  if (!rosidl_runtime_c__String__copy(
      &(input->feedback_message), &(output->feedback_message)))
  {
    return false;
  }
  // distance_remaining
  output->distance_remaining = input->distance_remaining;
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_Feedback *
smarc_mission_msgs__action__GotoWaypoint_Feedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Feedback * msg = (smarc_mission_msgs__action__GotoWaypoint_Feedback *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Feedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_Feedback));
  bool success = smarc_mission_msgs__action__GotoWaypoint_Feedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_Feedback__destroy(smarc_mission_msgs__action__GotoWaypoint_Feedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Feedback * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_Feedback *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_Feedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_Feedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence *
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_Feedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_Feedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_Feedback * data =
      (smarc_mission_msgs__action__GotoWaypoint_Feedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `goal`
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__init(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(msg);
    return false;
  }
  // goal
  if (!smarc_mission_msgs__action__GotoWaypoint_Goal__init(&msg->goal)) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // goal
  smarc_mission_msgs__action__GotoWaypoint_Goal__fini(&msg->goal);
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__are_equal(const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * lhs, const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // goal
  if (!smarc_mission_msgs__action__GotoWaypoint_Goal__are_equal(
      &(lhs->goal), &(rhs->goal)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__copy(
  const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * input,
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // goal
  if (!smarc_mission_msgs__action__GotoWaypoint_Goal__copy(
      &(input->goal), &(output->goal)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request *
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * msg = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request));
  bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__destroy(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence *
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request * data =
      (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `stamp`
// already included above
// #include "builtin_interfaces/msg/detail/time__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__init(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__are_equal(const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * lhs, const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__copy(
  const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * input,
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response *
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * msg = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response));
  bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__destroy(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence *
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response * data =
      (smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_SendGoal_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__init(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__are_equal(const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * lhs, const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__copy(
  const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * input,
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_GetResult_Request *
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * msg = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Request *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request));
  bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__destroy(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Request *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence *
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Request * data =
      (smarc_mission_msgs__action__GotoWaypoint_GetResult_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `result`
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__init(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * msg)
{
  if (!msg) {
    return false;
  }
  // status
  // result
  if (!smarc_mission_msgs__action__GotoWaypoint_Result__init(&msg->result)) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * msg)
{
  if (!msg) {
    return;
  }
  // status
  // result
  smarc_mission_msgs__action__GotoWaypoint_Result__fini(&msg->result);
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__are_equal(const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * lhs, const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // status
  if (lhs->status != rhs->status) {
    return false;
  }
  // result
  if (!smarc_mission_msgs__action__GotoWaypoint_Result__are_equal(
      &(lhs->result), &(rhs->result)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__copy(
  const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * input,
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // status
  output->status = input->status;
  // result
  if (!smarc_mission_msgs__action__GotoWaypoint_Result__copy(
      &(input->result), &(output->result)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_GetResult_Response *
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * msg = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Response *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response));
  bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__destroy(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Response *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence *
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_GetResult_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_GetResult_Response * data =
      (smarc_mission_msgs__action__GotoWaypoint_GetResult_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_GetResult_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `feedback`
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__functions.h"

bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__init(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(msg);
    return false;
  }
  // feedback
  if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__init(&msg->feedback)) {
    smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // feedback
  smarc_mission_msgs__action__GotoWaypoint_Feedback__fini(&msg->feedback);
}

bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__are_equal(const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * lhs, const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // feedback
  if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__are_equal(
      &(lhs->feedback), &(rhs->feedback)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__copy(
  const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * input,
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // feedback
  if (!smarc_mission_msgs__action__GotoWaypoint_Feedback__copy(
      &(input->feedback), &(output->feedback)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage *
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * msg = (smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage));
  bool success = smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__destroy(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__init(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__fini(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence *
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * array = (smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__destroy(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__are_equal(const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * lhs, const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence__copy(
  const smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * input,
  smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage * data =
      (smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__action__GotoWaypoint_FeedbackMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
