// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/DVLBeam.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/dvl_beam__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/detail/pose_stamped__functions.h"

bool
smarc_msgs__msg__DVLBeam__init(smarc_msgs__msg__DVLBeam * msg)
{
  if (!msg) {
    return false;
  }
  // range
  // range_covariance
  // velocity
  // velocity_covariance
  // pose
  if (!geometry_msgs__msg__PoseStamped__init(&msg->pose)) {
    smarc_msgs__msg__DVLBeam__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__DVLBeam__fini(smarc_msgs__msg__DVLBeam * msg)
{
  if (!msg) {
    return;
  }
  // range
  // range_covariance
  // velocity
  // velocity_covariance
  // pose
  geometry_msgs__msg__PoseStamped__fini(&msg->pose);
}

bool
smarc_msgs__msg__DVLBeam__are_equal(const smarc_msgs__msg__DVLBeam * lhs, const smarc_msgs__msg__DVLBeam * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // range
  if (lhs->range != rhs->range) {
    return false;
  }
  // range_covariance
  if (lhs->range_covariance != rhs->range_covariance) {
    return false;
  }
  // velocity
  if (lhs->velocity != rhs->velocity) {
    return false;
  }
  // velocity_covariance
  if (lhs->velocity_covariance != rhs->velocity_covariance) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__DVLBeam__copy(
  const smarc_msgs__msg__DVLBeam * input,
  smarc_msgs__msg__DVLBeam * output)
{
  if (!input || !output) {
    return false;
  }
  // range
  output->range = input->range;
  // range_covariance
  output->range_covariance = input->range_covariance;
  // velocity
  output->velocity = input->velocity;
  // velocity_covariance
  output->velocity_covariance = input->velocity_covariance;
  // pose
  if (!geometry_msgs__msg__PoseStamped__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__DVLBeam *
smarc_msgs__msg__DVLBeam__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__DVLBeam * msg = (smarc_msgs__msg__DVLBeam *)allocator.allocate(sizeof(smarc_msgs__msg__DVLBeam), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__DVLBeam));
  bool success = smarc_msgs__msg__DVLBeam__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__DVLBeam__destroy(smarc_msgs__msg__DVLBeam * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__DVLBeam__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__DVLBeam__Sequence__init(smarc_msgs__msg__DVLBeam__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__DVLBeam * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__DVLBeam *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__DVLBeam), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__DVLBeam__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__DVLBeam__fini(&data[i - 1]);
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
smarc_msgs__msg__DVLBeam__Sequence__fini(smarc_msgs__msg__DVLBeam__Sequence * array)
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
      smarc_msgs__msg__DVLBeam__fini(&array->data[i]);
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

smarc_msgs__msg__DVLBeam__Sequence *
smarc_msgs__msg__DVLBeam__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__DVLBeam__Sequence * array = (smarc_msgs__msg__DVLBeam__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__DVLBeam__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__DVLBeam__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__DVLBeam__Sequence__destroy(smarc_msgs__msg__DVLBeam__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__DVLBeam__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__DVLBeam__Sequence__are_equal(const smarc_msgs__msg__DVLBeam__Sequence * lhs, const smarc_msgs__msg__DVLBeam__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__DVLBeam__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__DVLBeam__Sequence__copy(
  const smarc_msgs__msg__DVLBeam__Sequence * input,
  smarc_msgs__msg__DVLBeam__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__DVLBeam);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__DVLBeam * data =
      (smarc_msgs__msg__DVLBeam *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__DVLBeam__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__DVLBeam__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__DVLBeam__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
