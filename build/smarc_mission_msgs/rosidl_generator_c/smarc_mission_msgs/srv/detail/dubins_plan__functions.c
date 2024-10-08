// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice
#include "smarc_mission_msgs/srv/detail/dubins_plan__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `waypoints`
#include "geometry_msgs/msg/detail/pose2_d__functions.h"

bool
smarc_mission_msgs__srv__DubinsPlan_Request__init(smarc_mission_msgs__srv__DubinsPlan_Request * msg)
{
  if (!msg) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__init(&msg->waypoints, 0)) {
    smarc_mission_msgs__srv__DubinsPlan_Request__fini(msg);
    return false;
  }
  // step
  // turning_radius
  return true;
}

void
smarc_mission_msgs__srv__DubinsPlan_Request__fini(smarc_mission_msgs__srv__DubinsPlan_Request * msg)
{
  if (!msg) {
    return;
  }
  // waypoints
  geometry_msgs__msg__Pose2D__Sequence__fini(&msg->waypoints);
  // step
  // turning_radius
}

bool
smarc_mission_msgs__srv__DubinsPlan_Request__are_equal(const smarc_mission_msgs__srv__DubinsPlan_Request * lhs, const smarc_mission_msgs__srv__DubinsPlan_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  // step
  if (lhs->step != rhs->step) {
    return false;
  }
  // turning_radius
  if (lhs->turning_radius != rhs->turning_radius) {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__srv__DubinsPlan_Request__copy(
  const smarc_mission_msgs__srv__DubinsPlan_Request * input,
  smarc_mission_msgs__srv__DubinsPlan_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  // step
  output->step = input->step;
  // turning_radius
  output->turning_radius = input->turning_radius;
  return true;
}

smarc_mission_msgs__srv__DubinsPlan_Request *
smarc_mission_msgs__srv__DubinsPlan_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Request * msg = (smarc_mission_msgs__srv__DubinsPlan_Request *)allocator.allocate(sizeof(smarc_mission_msgs__srv__DubinsPlan_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__srv__DubinsPlan_Request));
  bool success = smarc_mission_msgs__srv__DubinsPlan_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__srv__DubinsPlan_Request__destroy(smarc_mission_msgs__srv__DubinsPlan_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__srv__DubinsPlan_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__init(smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Request * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__srv__DubinsPlan_Request *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__srv__DubinsPlan_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__srv__DubinsPlan_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__srv__DubinsPlan_Request__fini(&data[i - 1]);
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
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__fini(smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * array)
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
      smarc_mission_msgs__srv__DubinsPlan_Request__fini(&array->data[i]);
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

smarc_mission_msgs__srv__DubinsPlan_Request__Sequence *
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * array = (smarc_mission_msgs__srv__DubinsPlan_Request__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__srv__DubinsPlan_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__destroy(smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__are_equal(const smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * lhs, const smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__srv__DubinsPlan_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__srv__DubinsPlan_Request__Sequence__copy(
  const smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * input,
  smarc_mission_msgs__srv__DubinsPlan_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__srv__DubinsPlan_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__srv__DubinsPlan_Request * data =
      (smarc_mission_msgs__srv__DubinsPlan_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__srv__DubinsPlan_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__srv__DubinsPlan_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__srv__DubinsPlan_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `waypoints`
// already included above
// #include "geometry_msgs/msg/detail/pose2_d__functions.h"
// Member `original_wp_indices`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
smarc_mission_msgs__srv__DubinsPlan_Response__init(smarc_mission_msgs__srv__DubinsPlan_Response * msg)
{
  if (!msg) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__init(&msg->waypoints, 0)) {
    smarc_mission_msgs__srv__DubinsPlan_Response__fini(msg);
    return false;
  }
  // original_wp_indices
  if (!rosidl_runtime_c__uint16__Sequence__init(&msg->original_wp_indices, 0)) {
    smarc_mission_msgs__srv__DubinsPlan_Response__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__srv__DubinsPlan_Response__fini(smarc_mission_msgs__srv__DubinsPlan_Response * msg)
{
  if (!msg) {
    return;
  }
  // waypoints
  geometry_msgs__msg__Pose2D__Sequence__fini(&msg->waypoints);
  // original_wp_indices
  rosidl_runtime_c__uint16__Sequence__fini(&msg->original_wp_indices);
}

bool
smarc_mission_msgs__srv__DubinsPlan_Response__are_equal(const smarc_mission_msgs__srv__DubinsPlan_Response * lhs, const smarc_mission_msgs__srv__DubinsPlan_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  // original_wp_indices
  if (!rosidl_runtime_c__uint16__Sequence__are_equal(
      &(lhs->original_wp_indices), &(rhs->original_wp_indices)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__srv__DubinsPlan_Response__copy(
  const smarc_mission_msgs__srv__DubinsPlan_Response * input,
  smarc_mission_msgs__srv__DubinsPlan_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // waypoints
  if (!geometry_msgs__msg__Pose2D__Sequence__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  // original_wp_indices
  if (!rosidl_runtime_c__uint16__Sequence__copy(
      &(input->original_wp_indices), &(output->original_wp_indices)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__srv__DubinsPlan_Response *
smarc_mission_msgs__srv__DubinsPlan_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Response * msg = (smarc_mission_msgs__srv__DubinsPlan_Response *)allocator.allocate(sizeof(smarc_mission_msgs__srv__DubinsPlan_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__srv__DubinsPlan_Response));
  bool success = smarc_mission_msgs__srv__DubinsPlan_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__srv__DubinsPlan_Response__destroy(smarc_mission_msgs__srv__DubinsPlan_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__srv__DubinsPlan_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__init(smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Response * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__srv__DubinsPlan_Response *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__srv__DubinsPlan_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__srv__DubinsPlan_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__srv__DubinsPlan_Response__fini(&data[i - 1]);
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
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__fini(smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * array)
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
      smarc_mission_msgs__srv__DubinsPlan_Response__fini(&array->data[i]);
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

smarc_mission_msgs__srv__DubinsPlan_Response__Sequence *
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * array = (smarc_mission_msgs__srv__DubinsPlan_Response__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__srv__DubinsPlan_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__destroy(smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__are_equal(const smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * lhs, const smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__srv__DubinsPlan_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__srv__DubinsPlan_Response__Sequence__copy(
  const smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * input,
  smarc_mission_msgs__srv__DubinsPlan_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__srv__DubinsPlan_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__srv__DubinsPlan_Response * data =
      (smarc_mission_msgs__srv__DubinsPlan_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__srv__DubinsPlan_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__srv__DubinsPlan_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__srv__DubinsPlan_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
