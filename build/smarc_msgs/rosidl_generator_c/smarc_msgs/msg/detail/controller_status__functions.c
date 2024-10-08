// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/ControllerStatus.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/controller_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `service_name`
// Member `diagnostics_message`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_msgs__msg__ControllerStatus__init(smarc_msgs__msg__ControllerStatus * msg)
{
  if (!msg) {
    return false;
  }
  // control_status
  // service_name
  if (!rosidl_runtime_c__String__init(&msg->service_name)) {
    smarc_msgs__msg__ControllerStatus__fini(msg);
    return false;
  }
  // diagnostics_message
  if (!rosidl_runtime_c__String__init(&msg->diagnostics_message)) {
    smarc_msgs__msg__ControllerStatus__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__ControllerStatus__fini(smarc_msgs__msg__ControllerStatus * msg)
{
  if (!msg) {
    return;
  }
  // control_status
  // service_name
  rosidl_runtime_c__String__fini(&msg->service_name);
  // diagnostics_message
  rosidl_runtime_c__String__fini(&msg->diagnostics_message);
}

bool
smarc_msgs__msg__ControllerStatus__are_equal(const smarc_msgs__msg__ControllerStatus * lhs, const smarc_msgs__msg__ControllerStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // control_status
  if (lhs->control_status != rhs->control_status) {
    return false;
  }
  // service_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->service_name), &(rhs->service_name)))
  {
    return false;
  }
  // diagnostics_message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->diagnostics_message), &(rhs->diagnostics_message)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__ControllerStatus__copy(
  const smarc_msgs__msg__ControllerStatus * input,
  smarc_msgs__msg__ControllerStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // control_status
  output->control_status = input->control_status;
  // service_name
  if (!rosidl_runtime_c__String__copy(
      &(input->service_name), &(output->service_name)))
  {
    return false;
  }
  // diagnostics_message
  if (!rosidl_runtime_c__String__copy(
      &(input->diagnostics_message), &(output->diagnostics_message)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__ControllerStatus *
smarc_msgs__msg__ControllerStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ControllerStatus * msg = (smarc_msgs__msg__ControllerStatus *)allocator.allocate(sizeof(smarc_msgs__msg__ControllerStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__ControllerStatus));
  bool success = smarc_msgs__msg__ControllerStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__ControllerStatus__destroy(smarc_msgs__msg__ControllerStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__ControllerStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__ControllerStatus__Sequence__init(smarc_msgs__msg__ControllerStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ControllerStatus * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__ControllerStatus *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__ControllerStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__ControllerStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__ControllerStatus__fini(&data[i - 1]);
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
smarc_msgs__msg__ControllerStatus__Sequence__fini(smarc_msgs__msg__ControllerStatus__Sequence * array)
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
      smarc_msgs__msg__ControllerStatus__fini(&array->data[i]);
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

smarc_msgs__msg__ControllerStatus__Sequence *
smarc_msgs__msg__ControllerStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__ControllerStatus__Sequence * array = (smarc_msgs__msg__ControllerStatus__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__ControllerStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__ControllerStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__ControllerStatus__Sequence__destroy(smarc_msgs__msg__ControllerStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__ControllerStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__ControllerStatus__Sequence__are_equal(const smarc_msgs__msg__ControllerStatus__Sequence * lhs, const smarc_msgs__msg__ControllerStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__ControllerStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__ControllerStatus__Sequence__copy(
  const smarc_msgs__msg__ControllerStatus__Sequence * input,
  smarc_msgs__msg__ControllerStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__ControllerStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__ControllerStatus * data =
      (smarc_msgs__msg__ControllerStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__ControllerStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__ControllerStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__ControllerStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
