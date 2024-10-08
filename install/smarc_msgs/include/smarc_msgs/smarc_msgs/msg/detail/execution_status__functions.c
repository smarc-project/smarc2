// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/execution_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `execution_queue`
#include "smarc_msgs/msg/detail/sm_task__functions.h"

bool
smarc_msgs__msg__ExecutionStatus__init(smarc_msgs__msg__ExecutionStatus * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    smarc_msgs__msg__ExecutionStatus__fini(msg);
    return false;
  }
  // currently_executing
  // execution_queue
  if (!smarc_msgs__msg__SMTask__Sequence__init(&msg->execution_queue, 0)) {
    smarc_msgs__msg__ExecutionStatus__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__ExecutionStatus__fini(smarc_msgs__msg__ExecutionStatus * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // currently_executing
  // execution_queue
  smarc_msgs__msg__SMTask__Sequence__fini(&msg->execution_queue);
}

bool
smarc_msgs__msg__ExecutionStatus__are_equal(const smarc_msgs__msg__ExecutionStatus * lhs, const smarc_msgs__msg__ExecutionStatus * rhs)
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
  // currently_executing
  if (lhs->currently_executing != rhs->currently_executing) {
    return false;
  }
  // execution_queue
  if (!smarc_msgs__msg__SMTask__Sequence__are_equal(
      &(lhs->execution_queue), &(rhs->execution_queue)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__ExecutionStatus__copy(
  const smarc_msgs__msg__ExecutionStatus * input,
  smarc_msgs__msg__ExecutionStatus * output)
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
  // currently_executing
  output->currently_executing = input->currently_executing;
  // execution_queue
  if (!smarc_msgs__msg__SMTask__Sequence__copy(
      &(input->execution_queue), &(output->execution_queue)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__ExecutionStatus *
smarc_msgs__msg__ExecutionStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ExecutionStatus * msg = (smarc_msgs__msg__ExecutionStatus *)allocator.allocate(sizeof(smarc_msgs__msg__ExecutionStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__ExecutionStatus));
  bool success = smarc_msgs__msg__ExecutionStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__ExecutionStatus__destroy(smarc_msgs__msg__ExecutionStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__ExecutionStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__ExecutionStatus__Sequence__init(smarc_msgs__msg__ExecutionStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ExecutionStatus * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__ExecutionStatus *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__ExecutionStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__ExecutionStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__ExecutionStatus__fini(&data[i - 1]);
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
smarc_msgs__msg__ExecutionStatus__Sequence__fini(smarc_msgs__msg__ExecutionStatus__Sequence * array)
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
      smarc_msgs__msg__ExecutionStatus__fini(&array->data[i]);
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

smarc_msgs__msg__ExecutionStatus__Sequence *
smarc_msgs__msg__ExecutionStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ExecutionStatus__Sequence * array = (smarc_msgs__msg__ExecutionStatus__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__ExecutionStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__ExecutionStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__ExecutionStatus__Sequence__destroy(smarc_msgs__msg__ExecutionStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__ExecutionStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__ExecutionStatus__Sequence__are_equal(const smarc_msgs__msg__ExecutionStatus__Sequence * lhs, const smarc_msgs__msg__ExecutionStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__ExecutionStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__ExecutionStatus__Sequence__copy(
  const smarc_msgs__msg__ExecutionStatus__Sequence * input,
  smarc_msgs__msg__ExecutionStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__ExecutionStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__ExecutionStatus * data =
      (smarc_msgs__msg__ExecutionStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__ExecutionStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__ExecutionStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__ExecutionStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
