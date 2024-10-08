// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/StringPair.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/string_pair__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `first`
// Member `second`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_msgs__msg__StringPair__init(smarc_msgs__msg__StringPair * msg)
{
  if (!msg) {
    return false;
  }
  // first
  if (!rosidl_runtime_c__String__init(&msg->first)) {
    smarc_msgs__msg__StringPair__fini(msg);
    return false;
  }
  // second
  if (!rosidl_runtime_c__String__init(&msg->second)) {
    smarc_msgs__msg__StringPair__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__StringPair__fini(smarc_msgs__msg__StringPair * msg)
{
  if (!msg) {
    return;
  }
  // first
  rosidl_runtime_c__String__fini(&msg->first);
  // second
  rosidl_runtime_c__String__fini(&msg->second);
}

bool
smarc_msgs__msg__StringPair__are_equal(const smarc_msgs__msg__StringPair * lhs, const smarc_msgs__msg__StringPair * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // first
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->first), &(rhs->first)))
  {
    return false;
  }
  // second
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->second), &(rhs->second)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__StringPair__copy(
  const smarc_msgs__msg__StringPair * input,
  smarc_msgs__msg__StringPair * output)
{
  if (!input || !output) {
    return false;
  }
  // first
  if (!rosidl_runtime_c__String__copy(
      &(input->first), &(output->first)))
  {
    return false;
  }
  // second
  if (!rosidl_runtime_c__String__copy(
      &(input->second), &(output->second)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__StringPair *
smarc_msgs__msg__StringPair__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringPair * msg = (smarc_msgs__msg__StringPair *)allocator.allocate(sizeof(smarc_msgs__msg__StringPair), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__StringPair));
  bool success = smarc_msgs__msg__StringPair__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__StringPair__destroy(smarc_msgs__msg__StringPair * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__StringPair__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__StringPair__Sequence__init(smarc_msgs__msg__StringPair__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringPair * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__StringPair *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__StringPair), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__StringPair__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__StringPair__fini(&data[i - 1]);
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
smarc_msgs__msg__StringPair__Sequence__fini(smarc_msgs__msg__StringPair__Sequence * array)
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
      smarc_msgs__msg__StringPair__fini(&array->data[i]);
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

smarc_msgs__msg__StringPair__Sequence *
smarc_msgs__msg__StringPair__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringPair__Sequence * array = (smarc_msgs__msg__StringPair__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__StringPair__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__StringPair__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__StringPair__Sequence__destroy(smarc_msgs__msg__StringPair__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__StringPair__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__StringPair__Sequence__are_equal(const smarc_msgs__msg__StringPair__Sequence * lhs, const smarc_msgs__msg__StringPair__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__StringPair__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__StringPair__Sequence__copy(
  const smarc_msgs__msg__StringPair__Sequence * input,
  smarc_msgs__msg__StringPair__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__StringPair);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__StringPair * data =
      (smarc_msgs__msg__StringPair *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__StringPair__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__StringPair__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__StringPair__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
