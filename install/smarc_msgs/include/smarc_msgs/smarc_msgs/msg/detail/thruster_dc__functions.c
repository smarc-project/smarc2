// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/ThrusterDC.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/thruster_dc__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smarc_msgs__msg__ThrusterDC__init(smarc_msgs__msg__ThrusterDC * msg)
{
  if (!msg) {
    return false;
  }
  // dc
  return true;
}

void
smarc_msgs__msg__ThrusterDC__fini(smarc_msgs__msg__ThrusterDC * msg)
{
  if (!msg) {
    return;
  }
  // dc
}

bool
smarc_msgs__msg__ThrusterDC__are_equal(const smarc_msgs__msg__ThrusterDC * lhs, const smarc_msgs__msg__ThrusterDC * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // dc
  if (lhs->dc != rhs->dc) {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__ThrusterDC__copy(
  const smarc_msgs__msg__ThrusterDC * input,
  smarc_msgs__msg__ThrusterDC * output)
{
  if (!input || !output) {
    return false;
  }
  // dc
  output->dc = input->dc;
  return true;
}

smarc_msgs__msg__ThrusterDC *
smarc_msgs__msg__ThrusterDC__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterDC * msg = (smarc_msgs__msg__ThrusterDC *)allocator.allocate(sizeof(smarc_msgs__msg__ThrusterDC), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__ThrusterDC));
  bool success = smarc_msgs__msg__ThrusterDC__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__ThrusterDC__destroy(smarc_msgs__msg__ThrusterDC * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__ThrusterDC__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__ThrusterDC__Sequence__init(smarc_msgs__msg__ThrusterDC__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterDC * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__ThrusterDC *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__ThrusterDC), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__ThrusterDC__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__ThrusterDC__fini(&data[i - 1]);
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
smarc_msgs__msg__ThrusterDC__Sequence__fini(smarc_msgs__msg__ThrusterDC__Sequence * array)
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
      smarc_msgs__msg__ThrusterDC__fini(&array->data[i]);
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

smarc_msgs__msg__ThrusterDC__Sequence *
smarc_msgs__msg__ThrusterDC__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ThrusterDC__Sequence * array = (smarc_msgs__msg__ThrusterDC__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__ThrusterDC__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__ThrusterDC__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__ThrusterDC__Sequence__destroy(smarc_msgs__msg__ThrusterDC__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__ThrusterDC__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__ThrusterDC__Sequence__are_equal(const smarc_msgs__msg__ThrusterDC__Sequence * lhs, const smarc_msgs__msg__ThrusterDC__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__ThrusterDC__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__ThrusterDC__Sequence__copy(
  const smarc_msgs__msg__ThrusterDC__Sequence * input,
  smarc_msgs__msg__ThrusterDC__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__ThrusterDC);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__ThrusterDC * data =
      (smarc_msgs__msg__ThrusterDC *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__ThrusterDC__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__ThrusterDC__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__ThrusterDC__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
