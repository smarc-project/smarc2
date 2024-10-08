// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/StringStamped.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/string_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `time_sent`
// Member `time_received`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `data`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_msgs__msg__StringStamped__init(smarc_msgs__msg__StringStamped * msg)
{
  if (!msg) {
    return false;
  }
  // time_sent
  if (!builtin_interfaces__msg__Time__init(&msg->time_sent)) {
    smarc_msgs__msg__StringStamped__fini(msg);
    return false;
  }
  // time_received
  if (!builtin_interfaces__msg__Time__init(&msg->time_received)) {
    smarc_msgs__msg__StringStamped__fini(msg);
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__init(&msg->data)) {
    smarc_msgs__msg__StringStamped__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__StringStamped__fini(smarc_msgs__msg__StringStamped * msg)
{
  if (!msg) {
    return;
  }
  // time_sent
  builtin_interfaces__msg__Time__fini(&msg->time_sent);
  // time_received
  builtin_interfaces__msg__Time__fini(&msg->time_received);
  // data
  rosidl_runtime_c__String__fini(&msg->data);
}

bool
smarc_msgs__msg__StringStamped__are_equal(const smarc_msgs__msg__StringStamped * lhs, const smarc_msgs__msg__StringStamped * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // time_sent
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->time_sent), &(rhs->time_sent)))
  {
    return false;
  }
  // time_received
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->time_received), &(rhs->time_received)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->data), &(rhs->data)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__StringStamped__copy(
  const smarc_msgs__msg__StringStamped * input,
  smarc_msgs__msg__StringStamped * output)
{
  if (!input || !output) {
    return false;
  }
  // time_sent
  if (!builtin_interfaces__msg__Time__copy(
      &(input->time_sent), &(output->time_sent)))
  {
    return false;
  }
  // time_received
  if (!builtin_interfaces__msg__Time__copy(
      &(input->time_received), &(output->time_received)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__copy(
      &(input->data), &(output->data)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__StringStamped *
smarc_msgs__msg__StringStamped__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringStamped * msg = (smarc_msgs__msg__StringStamped *)allocator.allocate(sizeof(smarc_msgs__msg__StringStamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__StringStamped));
  bool success = smarc_msgs__msg__StringStamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__StringStamped__destroy(smarc_msgs__msg__StringStamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__StringStamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__StringStamped__Sequence__init(smarc_msgs__msg__StringStamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringStamped * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__StringStamped *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__StringStamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__StringStamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__StringStamped__fini(&data[i - 1]);
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
smarc_msgs__msg__StringStamped__Sequence__fini(smarc_msgs__msg__StringStamped__Sequence * array)
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
      smarc_msgs__msg__StringStamped__fini(&array->data[i]);
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

smarc_msgs__msg__StringStamped__Sequence *
smarc_msgs__msg__StringStamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__StringStamped__Sequence * array = (smarc_msgs__msg__StringStamped__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__StringStamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__StringStamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__StringStamped__Sequence__destroy(smarc_msgs__msg__StringStamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__StringStamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__StringStamped__Sequence__are_equal(const smarc_msgs__msg__StringStamped__Sequence * lhs, const smarc_msgs__msg__StringStamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__StringStamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__StringStamped__Sequence__copy(
  const smarc_msgs__msg__StringStamped__Sequence * input,
  smarc_msgs__msg__StringStamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__StringStamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__StringStamped * data =
      (smarc_msgs__msg__StringStamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__StringStamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__StringStamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__StringStamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
