// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/ThrusterFeedback.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/thruster_feedback__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `rpm`
#include "smarc_msgs/msg/detail/thruster_rpm__functions.h"
// Member `dc`
#include "smarc_msgs/msg/detail/thruster_dc__functions.h"

bool
smarc_msgs__msg__ThrusterFeedback__init(smarc_msgs__msg__ThrusterFeedback * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    smarc_msgs__msg__ThrusterFeedback__fini(msg);
    return false;
  }
  // rpm
  if (!smarc_msgs__msg__ThrusterRPM__init(&msg->rpm)) {
    smarc_msgs__msg__ThrusterFeedback__fini(msg);
    return false;
  }
  // dc
  if (!smarc_msgs__msg__ThrusterDC__init(&msg->dc)) {
    smarc_msgs__msg__ThrusterFeedback__fini(msg);
    return false;
  }
  // current
  // torque
  return true;
}

void
smarc_msgs__msg__ThrusterFeedback__fini(smarc_msgs__msg__ThrusterFeedback * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // rpm
  smarc_msgs__msg__ThrusterRPM__fini(&msg->rpm);
  // dc
  smarc_msgs__msg__ThrusterDC__fini(&msg->dc);
  // current
  // torque
}

bool
smarc_msgs__msg__ThrusterFeedback__are_equal(const smarc_msgs__msg__ThrusterFeedback * lhs, const smarc_msgs__msg__ThrusterFeedback * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // rpm
  if (!smarc_msgs__msg__ThrusterRPM__are_equal(
      &(lhs->rpm), &(rhs->rpm)))
  {
    return false;
  }
  // dc
  if (!smarc_msgs__msg__ThrusterDC__are_equal(
      &(lhs->dc), &(rhs->dc)))
  {
    return false;
  }
  // current
  if (lhs->current != rhs->current) {
    return false;
  }
  // torque
  if (lhs->torque != rhs->torque) {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__ThrusterFeedback__copy(
  const smarc_msgs__msg__ThrusterFeedback * input,
  smarc_msgs__msg__ThrusterFeedback * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // rpm
  if (!smarc_msgs__msg__ThrusterRPM__copy(
      &(input->rpm), &(output->rpm)))
  {
    return false;
  }
  // dc
  if (!smarc_msgs__msg__ThrusterDC__copy(
      &(input->dc), &(output->dc)))
  {
    return false;
  }
  // current
  output->current = input->current;
  // torque
  output->torque = input->torque;
  return true;
}

smarc_msgs__msg__ThrusterFeedback *
smarc_msgs__msg__ThrusterFeedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterFeedback * msg = (smarc_msgs__msg__ThrusterFeedback *)allocator.allocate(sizeof(smarc_msgs__msg__ThrusterFeedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__ThrusterFeedback));
  bool success = smarc_msgs__msg__ThrusterFeedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__ThrusterFeedback__destroy(smarc_msgs__msg__ThrusterFeedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__ThrusterFeedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__ThrusterFeedback__Sequence__init(smarc_msgs__msg__ThrusterFeedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterFeedback * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__ThrusterFeedback *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__ThrusterFeedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__ThrusterFeedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__ThrusterFeedback__fini(&data[i - 1]);
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
smarc_msgs__msg__ThrusterFeedback__Sequence__fini(smarc_msgs__msg__ThrusterFeedback__Sequence * array)
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
      smarc_msgs__msg__ThrusterFeedback__fini(&array->data[i]);
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

smarc_msgs__msg__ThrusterFeedback__Sequence *
smarc_msgs__msg__ThrusterFeedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterFeedback__Sequence * array = (smarc_msgs__msg__ThrusterFeedback__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__ThrusterFeedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__ThrusterFeedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__ThrusterFeedback__Sequence__destroy(smarc_msgs__msg__ThrusterFeedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__ThrusterFeedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__ThrusterFeedback__Sequence__are_equal(const smarc_msgs__msg__ThrusterFeedback__Sequence * lhs, const smarc_msgs__msg__ThrusterFeedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__ThrusterFeedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__ThrusterFeedback__Sequence__copy(
  const smarc_msgs__msg__ThrusterFeedback__Sequence * input,
  smarc_msgs__msg__ThrusterFeedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__ThrusterFeedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__ThrusterFeedback * data =
      (smarc_msgs__msg__ThrusterFeedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__ThrusterFeedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__ThrusterFeedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__ThrusterFeedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
