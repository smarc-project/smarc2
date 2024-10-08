// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_control_msgs:msg/ControlError.idl
// generated code does not contain a copyright notice
#include "smarc_control_msgs/msg/detail/control_error__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smarc_control_msgs__msg__ControlError__init(smarc_control_msgs__msg__ControlError * msg)
{
  if (!msg) {
    return false;
  }
  // x
  // y
  // z
  // roll
  // pitch
  // yaw
  // heading
  // distance
  return true;
}

void
smarc_control_msgs__msg__ControlError__fini(smarc_control_msgs__msg__ControlError * msg)
{
  if (!msg) {
    return;
  }
  // x
  // y
  // z
  // roll
  // pitch
  // yaw
  // heading
  // distance
}

bool
smarc_control_msgs__msg__ControlError__are_equal(const smarc_control_msgs__msg__ControlError * lhs, const smarc_control_msgs__msg__ControlError * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // roll
  if (lhs->roll != rhs->roll) {
    return false;
  }
  // pitch
  if (lhs->pitch != rhs->pitch) {
    return false;
  }
  // yaw
  if (lhs->yaw != rhs->yaw) {
    return false;
  }
  // heading
  if (lhs->heading != rhs->heading) {
    return false;
  }
  // distance
  if (lhs->distance != rhs->distance) {
    return false;
  }
  return true;
}

bool
smarc_control_msgs__msg__ControlError__copy(
  const smarc_control_msgs__msg__ControlError * input,
  smarc_control_msgs__msg__ControlError * output)
{
  if (!input || !output) {
    return false;
  }
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // roll
  output->roll = input->roll;
  // pitch
  output->pitch = input->pitch;
  // yaw
  output->yaw = input->yaw;
  // heading
  output->heading = input->heading;
  // distance
  output->distance = input->distance;
  return true;
}

smarc_control_msgs__msg__ControlError *
smarc_control_msgs__msg__ControlError__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_control_msgs__msg__ControlError * msg = (smarc_control_msgs__msg__ControlError *)allocator.allocate(sizeof(smarc_control_msgs__msg__ControlError), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_control_msgs__msg__ControlError));
  bool success = smarc_control_msgs__msg__ControlError__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_control_msgs__msg__ControlError__destroy(smarc_control_msgs__msg__ControlError * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_control_msgs__msg__ControlError__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_control_msgs__msg__ControlError__Sequence__init(smarc_control_msgs__msg__ControlError__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_control_msgs__msg__ControlError * data = NULL;

  if (size) {
    data = (smarc_control_msgs__msg__ControlError *)allocator.zero_allocate(size, sizeof(smarc_control_msgs__msg__ControlError), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_control_msgs__msg__ControlError__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_control_msgs__msg__ControlError__fini(&data[i - 1]);
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
smarc_control_msgs__msg__ControlError__Sequence__fini(smarc_control_msgs__msg__ControlError__Sequence * array)
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
      smarc_control_msgs__msg__ControlError__fini(&array->data[i]);
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

smarc_control_msgs__msg__ControlError__Sequence *
smarc_control_msgs__msg__ControlError__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_control_msgs__msg__ControlError__Sequence * array = (smarc_control_msgs__msg__ControlError__Sequence *)allocator.allocate(sizeof(smarc_control_msgs__msg__ControlError__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_control_msgs__msg__ControlError__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_control_msgs__msg__ControlError__Sequence__destroy(smarc_control_msgs__msg__ControlError__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_control_msgs__msg__ControlError__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_control_msgs__msg__ControlError__Sequence__are_equal(const smarc_control_msgs__msg__ControlError__Sequence * lhs, const smarc_control_msgs__msg__ControlError__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_control_msgs__msg__ControlError__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_control_msgs__msg__ControlError__Sequence__copy(
  const smarc_control_msgs__msg__ControlError__Sequence * input,
  smarc_control_msgs__msg__ControlError__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_control_msgs__msg__ControlError);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_control_msgs__msg__ControlError * data =
      (smarc_control_msgs__msg__ControlError *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_control_msgs__msg__ControlError__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_control_msgs__msg__ControlError__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_control_msgs__msg__ControlError__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
