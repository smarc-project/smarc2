// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:msg/CircuitStatusStampedArray.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/circuit_status_stamped_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `array`
#include "sam_msgs/msg/detail/circuit_status_stamped__functions.h"

bool
sam_msgs__msg__CircuitStatusStampedArray__init(sam_msgs__msg__CircuitStatusStampedArray * msg)
{
  if (!msg) {
    return false;
  }
  // array
  if (!sam_msgs__msg__CircuitStatusStamped__Sequence__init(&msg->array, 0)) {
    sam_msgs__msg__CircuitStatusStampedArray__fini(msg);
    return false;
  }
  return true;
}

void
sam_msgs__msg__CircuitStatusStampedArray__fini(sam_msgs__msg__CircuitStatusStampedArray * msg)
{
  if (!msg) {
    return;
  }
  // array
  sam_msgs__msg__CircuitStatusStamped__Sequence__fini(&msg->array);
}

bool
sam_msgs__msg__CircuitStatusStampedArray__are_equal(const sam_msgs__msg__CircuitStatusStampedArray * lhs, const sam_msgs__msg__CircuitStatusStampedArray * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // array
  if (!sam_msgs__msg__CircuitStatusStamped__Sequence__are_equal(
      &(lhs->array), &(rhs->array)))
  {
    return false;
  }
  return true;
}

bool
sam_msgs__msg__CircuitStatusStampedArray__copy(
  const sam_msgs__msg__CircuitStatusStampedArray * input,
  sam_msgs__msg__CircuitStatusStampedArray * output)
{
  if (!input || !output) {
    return false;
  }
  // array
  if (!sam_msgs__msg__CircuitStatusStamped__Sequence__copy(
      &(input->array), &(output->array)))
  {
    return false;
  }
  return true;
}

sam_msgs__msg__CircuitStatusStampedArray *
sam_msgs__msg__CircuitStatusStampedArray__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__CircuitStatusStampedArray * msg = (sam_msgs__msg__CircuitStatusStampedArray *)allocator.allocate(sizeof(sam_msgs__msg__CircuitStatusStampedArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__msg__CircuitStatusStampedArray));
  bool success = sam_msgs__msg__CircuitStatusStampedArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__msg__CircuitStatusStampedArray__destroy(sam_msgs__msg__CircuitStatusStampedArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__msg__CircuitStatusStampedArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__msg__CircuitStatusStampedArray__Sequence__init(sam_msgs__msg__CircuitStatusStampedArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__CircuitStatusStampedArray * data = NULL;

  if (size) {
    data = (sam_msgs__msg__CircuitStatusStampedArray *)allocator.zero_allocate(size, sizeof(sam_msgs__msg__CircuitStatusStampedArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__msg__CircuitStatusStampedArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__msg__CircuitStatusStampedArray__fini(&data[i - 1]);
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
sam_msgs__msg__CircuitStatusStampedArray__Sequence__fini(sam_msgs__msg__CircuitStatusStampedArray__Sequence * array)
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
      sam_msgs__msg__CircuitStatusStampedArray__fini(&array->data[i]);
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

sam_msgs__msg__CircuitStatusStampedArray__Sequence *
sam_msgs__msg__CircuitStatusStampedArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__CircuitStatusStampedArray__Sequence * array = (sam_msgs__msg__CircuitStatusStampedArray__Sequence *)allocator.allocate(sizeof(sam_msgs__msg__CircuitStatusStampedArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__msg__CircuitStatusStampedArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__msg__CircuitStatusStampedArray__Sequence__destroy(sam_msgs__msg__CircuitStatusStampedArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__msg__CircuitStatusStampedArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__msg__CircuitStatusStampedArray__Sequence__are_equal(const sam_msgs__msg__CircuitStatusStampedArray__Sequence * lhs, const sam_msgs__msg__CircuitStatusStampedArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__msg__CircuitStatusStampedArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__msg__CircuitStatusStampedArray__Sequence__copy(
  const sam_msgs__msg__CircuitStatusStampedArray__Sequence * input,
  sam_msgs__msg__CircuitStatusStampedArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__msg__CircuitStatusStampedArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__msg__CircuitStatusStampedArray * data =
      (sam_msgs__msg__CircuitStatusStampedArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__msg__CircuitStatusStampedArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__msg__CircuitStatusStampedArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__msg__CircuitStatusStampedArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
