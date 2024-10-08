// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/uavcan_node_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
sam_msgs__msg__UavcanNodeStatus__init(sam_msgs__msg__UavcanNodeStatus * msg)
{
  if (!msg) {
    return false;
  }
  // uptime_sec
  // health
  // mode
  // sub_mode
  // vendor_specific_status_code
  return true;
}

void
sam_msgs__msg__UavcanNodeStatus__fini(sam_msgs__msg__UavcanNodeStatus * msg)
{
  if (!msg) {
    return;
  }
  // uptime_sec
  // health
  // mode
  // sub_mode
  // vendor_specific_status_code
}

bool
sam_msgs__msg__UavcanNodeStatus__are_equal(const sam_msgs__msg__UavcanNodeStatus * lhs, const sam_msgs__msg__UavcanNodeStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // uptime_sec
  if (lhs->uptime_sec != rhs->uptime_sec) {
    return false;
  }
  // health
  if (lhs->health != rhs->health) {
    return false;
  }
  // mode
  if (lhs->mode != rhs->mode) {
    return false;
  }
  // sub_mode
  if (lhs->sub_mode != rhs->sub_mode) {
    return false;
  }
  // vendor_specific_status_code
  if (lhs->vendor_specific_status_code != rhs->vendor_specific_status_code) {
    return false;
  }
  return true;
}

bool
sam_msgs__msg__UavcanNodeStatus__copy(
  const sam_msgs__msg__UavcanNodeStatus * input,
  sam_msgs__msg__UavcanNodeStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // uptime_sec
  output->uptime_sec = input->uptime_sec;
  // health
  output->health = input->health;
  // mode
  output->mode = input->mode;
  // sub_mode
  output->sub_mode = input->sub_mode;
  // vendor_specific_status_code
  output->vendor_specific_status_code = input->vendor_specific_status_code;
  return true;
}

sam_msgs__msg__UavcanNodeStatus *
sam_msgs__msg__UavcanNodeStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__UavcanNodeStatus * msg = (sam_msgs__msg__UavcanNodeStatus *)allocator.allocate(sizeof(sam_msgs__msg__UavcanNodeStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__msg__UavcanNodeStatus));
  bool success = sam_msgs__msg__UavcanNodeStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__msg__UavcanNodeStatus__destroy(sam_msgs__msg__UavcanNodeStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__msg__UavcanNodeStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__msg__UavcanNodeStatus__Sequence__init(sam_msgs__msg__UavcanNodeStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__UavcanNodeStatus * data = NULL;

  if (size) {
    data = (sam_msgs__msg__UavcanNodeStatus *)allocator.zero_allocate(size, sizeof(sam_msgs__msg__UavcanNodeStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__msg__UavcanNodeStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__msg__UavcanNodeStatus__fini(&data[i - 1]);
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
sam_msgs__msg__UavcanNodeStatus__Sequence__fini(sam_msgs__msg__UavcanNodeStatus__Sequence * array)
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
      sam_msgs__msg__UavcanNodeStatus__fini(&array->data[i]);
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

sam_msgs__msg__UavcanNodeStatus__Sequence *
sam_msgs__msg__UavcanNodeStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__UavcanNodeStatus__Sequence * array = (sam_msgs__msg__UavcanNodeStatus__Sequence *)allocator.allocate(sizeof(sam_msgs__msg__UavcanNodeStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__msg__UavcanNodeStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__msg__UavcanNodeStatus__Sequence__destroy(sam_msgs__msg__UavcanNodeStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__msg__UavcanNodeStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__msg__UavcanNodeStatus__Sequence__are_equal(const sam_msgs__msg__UavcanNodeStatus__Sequence * lhs, const sam_msgs__msg__UavcanNodeStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__msg__UavcanNodeStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__msg__UavcanNodeStatus__Sequence__copy(
  const sam_msgs__msg__UavcanNodeStatus__Sequence * input,
  sam_msgs__msg__UavcanNodeStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__msg__UavcanNodeStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__msg__UavcanNodeStatus * data =
      (sam_msgs__msg__UavcanNodeStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__msg__UavcanNodeStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__msg__UavcanNodeStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__msg__UavcanNodeStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
