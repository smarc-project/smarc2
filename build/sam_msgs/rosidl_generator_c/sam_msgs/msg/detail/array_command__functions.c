// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:msg/ArrayCommand.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/array_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `commands`
#include "sam_msgs/msg/detail/command__functions.h"

bool
sam_msgs__msg__ArrayCommand__init(sam_msgs__msg__ArrayCommand * msg)
{
  if (!msg) {
    return false;
  }
  // commands
  if (!sam_msgs__msg__Command__Sequence__init(&msg->commands, 0)) {
    sam_msgs__msg__ArrayCommand__fini(msg);
    return false;
  }
  return true;
}

void
sam_msgs__msg__ArrayCommand__fini(sam_msgs__msg__ArrayCommand * msg)
{
  if (!msg) {
    return;
  }
  // commands
  sam_msgs__msg__Command__Sequence__fini(&msg->commands);
}

bool
sam_msgs__msg__ArrayCommand__are_equal(const sam_msgs__msg__ArrayCommand * lhs, const sam_msgs__msg__ArrayCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // commands
  if (!sam_msgs__msg__Command__Sequence__are_equal(
      &(lhs->commands), &(rhs->commands)))
  {
    return false;
  }
  return true;
}

bool
sam_msgs__msg__ArrayCommand__copy(
  const sam_msgs__msg__ArrayCommand * input,
  sam_msgs__msg__ArrayCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // commands
  if (!sam_msgs__msg__Command__Sequence__copy(
      &(input->commands), &(output->commands)))
  {
    return false;
  }
  return true;
}

sam_msgs__msg__ArrayCommand *
sam_msgs__msg__ArrayCommand__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ArrayCommand * msg = (sam_msgs__msg__ArrayCommand *)allocator.allocate(sizeof(sam_msgs__msg__ArrayCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__msg__ArrayCommand));
  bool success = sam_msgs__msg__ArrayCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__msg__ArrayCommand__destroy(sam_msgs__msg__ArrayCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__msg__ArrayCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__msg__ArrayCommand__Sequence__init(sam_msgs__msg__ArrayCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ArrayCommand * data = NULL;

  if (size) {
    data = (sam_msgs__msg__ArrayCommand *)allocator.zero_allocate(size, sizeof(sam_msgs__msg__ArrayCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__msg__ArrayCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__msg__ArrayCommand__fini(&data[i - 1]);
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
sam_msgs__msg__ArrayCommand__Sequence__fini(sam_msgs__msg__ArrayCommand__Sequence * array)
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
      sam_msgs__msg__ArrayCommand__fini(&array->data[i]);
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

sam_msgs__msg__ArrayCommand__Sequence *
sam_msgs__msg__ArrayCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ArrayCommand__Sequence * array = (sam_msgs__msg__ArrayCommand__Sequence *)allocator.allocate(sizeof(sam_msgs__msg__ArrayCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__msg__ArrayCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__msg__ArrayCommand__Sequence__destroy(sam_msgs__msg__ArrayCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__msg__ArrayCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__msg__ArrayCommand__Sequence__are_equal(const sam_msgs__msg__ArrayCommand__Sequence * lhs, const sam_msgs__msg__ArrayCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__msg__ArrayCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__msg__ArrayCommand__Sequence__copy(
  const sam_msgs__msg__ArrayCommand__Sequence * input,
  sam_msgs__msg__ArrayCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__msg__ArrayCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__msg__ArrayCommand * data =
      (sam_msgs__msg__ArrayCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__msg__ArrayCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__msg__ArrayCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__msg__ArrayCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
