// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:msg/ThrusterAngles.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/thruster_angles__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
sam_msgs__msg__ThrusterAngles__init(sam_msgs__msg__ThrusterAngles * msg)
{
  if (!msg) {
    return false;
  }
  // thruster_vertical_radians
  // thruster_horizontal_radians
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    sam_msgs__msg__ThrusterAngles__fini(msg);
    return false;
  }
  return true;
}

void
sam_msgs__msg__ThrusterAngles__fini(sam_msgs__msg__ThrusterAngles * msg)
{
  if (!msg) {
    return;
  }
  // thruster_vertical_radians
  // thruster_horizontal_radians
  // header
  std_msgs__msg__Header__fini(&msg->header);
}

bool
sam_msgs__msg__ThrusterAngles__are_equal(const sam_msgs__msg__ThrusterAngles * lhs, const sam_msgs__msg__ThrusterAngles * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // thruster_vertical_radians
  if (lhs->thruster_vertical_radians != rhs->thruster_vertical_radians) {
    return false;
  }
  // thruster_horizontal_radians
  if (lhs->thruster_horizontal_radians != rhs->thruster_horizontal_radians) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  return true;
}

bool
sam_msgs__msg__ThrusterAngles__copy(
  const sam_msgs__msg__ThrusterAngles * input,
  sam_msgs__msg__ThrusterAngles * output)
{
  if (!input || !output) {
    return false;
  }
  // thruster_vertical_radians
  output->thruster_vertical_radians = input->thruster_vertical_radians;
  // thruster_horizontal_radians
  output->thruster_horizontal_radians = input->thruster_horizontal_radians;
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  return true;
}

sam_msgs__msg__ThrusterAngles *
sam_msgs__msg__ThrusterAngles__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ThrusterAngles * msg = (sam_msgs__msg__ThrusterAngles *)allocator.allocate(sizeof(sam_msgs__msg__ThrusterAngles), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__msg__ThrusterAngles));
  bool success = sam_msgs__msg__ThrusterAngles__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__msg__ThrusterAngles__destroy(sam_msgs__msg__ThrusterAngles * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__msg__ThrusterAngles__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__msg__ThrusterAngles__Sequence__init(sam_msgs__msg__ThrusterAngles__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ThrusterAngles * data = NULL;

  if (size) {
    data = (sam_msgs__msg__ThrusterAngles *)allocator.zero_allocate(size, sizeof(sam_msgs__msg__ThrusterAngles), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__msg__ThrusterAngles__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__msg__ThrusterAngles__fini(&data[i - 1]);
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
sam_msgs__msg__ThrusterAngles__Sequence__fini(sam_msgs__msg__ThrusterAngles__Sequence * array)
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
      sam_msgs__msg__ThrusterAngles__fini(&array->data[i]);
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

sam_msgs__msg__ThrusterAngles__Sequence *
sam_msgs__msg__ThrusterAngles__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ThrusterAngles__Sequence * array = (sam_msgs__msg__ThrusterAngles__Sequence *)allocator.allocate(sizeof(sam_msgs__msg__ThrusterAngles__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__msg__ThrusterAngles__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__msg__ThrusterAngles__Sequence__destroy(sam_msgs__msg__ThrusterAngles__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__msg__ThrusterAngles__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__msg__ThrusterAngles__Sequence__are_equal(const sam_msgs__msg__ThrusterAngles__Sequence * lhs, const sam_msgs__msg__ThrusterAngles__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__msg__ThrusterAngles__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__msg__ThrusterAngles__Sequence__copy(
  const sam_msgs__msg__ThrusterAngles__Sequence * input,
  sam_msgs__msg__ThrusterAngles__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__msg__ThrusterAngles);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__msg__ThrusterAngles * data =
      (sam_msgs__msg__ThrusterAngles *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__msg__ThrusterAngles__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__msg__ThrusterAngles__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__msg__ThrusterAngles__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
