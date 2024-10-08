// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/LatLonStamped.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/lat_lon_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
smarc_msgs__msg__LatLonStamped__init(smarc_msgs__msg__LatLonStamped * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    smarc_msgs__msg__LatLonStamped__fini(msg);
    return false;
  }
  // latitude
  // longitude
  return true;
}

void
smarc_msgs__msg__LatLonStamped__fini(smarc_msgs__msg__LatLonStamped * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // latitude
  // longitude
}

bool
smarc_msgs__msg__LatLonStamped__are_equal(const smarc_msgs__msg__LatLonStamped * lhs, const smarc_msgs__msg__LatLonStamped * rhs)
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
  // latitude
  if (lhs->latitude != rhs->latitude) {
    return false;
  }
  // longitude
  if (lhs->longitude != rhs->longitude) {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__LatLonStamped__copy(
  const smarc_msgs__msg__LatLonStamped * input,
  smarc_msgs__msg__LatLonStamped * output)
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
  // latitude
  output->latitude = input->latitude;
  // longitude
  output->longitude = input->longitude;
  return true;
}

smarc_msgs__msg__LatLonStamped *
smarc_msgs__msg__LatLonStamped__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonStamped * msg = (smarc_msgs__msg__LatLonStamped *)allocator.allocate(sizeof(smarc_msgs__msg__LatLonStamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__LatLonStamped));
  bool success = smarc_msgs__msg__LatLonStamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__LatLonStamped__destroy(smarc_msgs__msg__LatLonStamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__LatLonStamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__LatLonStamped__Sequence__init(smarc_msgs__msg__LatLonStamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonStamped * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__LatLonStamped *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__LatLonStamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__LatLonStamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__LatLonStamped__fini(&data[i - 1]);
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
smarc_msgs__msg__LatLonStamped__Sequence__fini(smarc_msgs__msg__LatLonStamped__Sequence * array)
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
      smarc_msgs__msg__LatLonStamped__fini(&array->data[i]);
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

smarc_msgs__msg__LatLonStamped__Sequence *
smarc_msgs__msg__LatLonStamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonStamped__Sequence * array = (smarc_msgs__msg__LatLonStamped__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__LatLonStamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__LatLonStamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__LatLonStamped__Sequence__destroy(smarc_msgs__msg__LatLonStamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__LatLonStamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__LatLonStamped__Sequence__are_equal(const smarc_msgs__msg__LatLonStamped__Sequence * lhs, const smarc_msgs__msg__LatLonStamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__LatLonStamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__LatLonStamped__Sequence__copy(
  const smarc_msgs__msg__LatLonStamped__Sequence * input,
  smarc_msgs__msg__LatLonStamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__LatLonStamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__LatLonStamped * data =
      (smarc_msgs__msg__LatLonStamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__LatLonStamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__LatLonStamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__LatLonStamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
