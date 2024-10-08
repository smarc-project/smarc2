// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/SensorStatus.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/sensor_status__functions.h"

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
smarc_msgs__msg__SensorStatus__init(smarc_msgs__msg__SensorStatus * msg)
{
  if (!msg) {
    return false;
  }
  // sensor_status
  // service_name
  if (!rosidl_runtime_c__String__init(&msg->service_name)) {
    smarc_msgs__msg__SensorStatus__fini(msg);
    return false;
  }
  // diagnostics_message
  if (!rosidl_runtime_c__String__init(&msg->diagnostics_message)) {
    smarc_msgs__msg__SensorStatus__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__SensorStatus__fini(smarc_msgs__msg__SensorStatus * msg)
{
  if (!msg) {
    return;
  }
  // sensor_status
  // service_name
  rosidl_runtime_c__String__fini(&msg->service_name);
  // diagnostics_message
  rosidl_runtime_c__String__fini(&msg->diagnostics_message);
}

bool
smarc_msgs__msg__SensorStatus__are_equal(const smarc_msgs__msg__SensorStatus * lhs, const smarc_msgs__msg__SensorStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // sensor_status
  if (lhs->sensor_status != rhs->sensor_status) {
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
smarc_msgs__msg__SensorStatus__copy(
  const smarc_msgs__msg__SensorStatus * input,
  smarc_msgs__msg__SensorStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // sensor_status
  output->sensor_status = input->sensor_status;
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

smarc_msgs__msg__SensorStatus *
smarc_msgs__msg__SensorStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SensorStatus * msg = (smarc_msgs__msg__SensorStatus *)allocator.allocate(sizeof(smarc_msgs__msg__SensorStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__SensorStatus));
  bool success = smarc_msgs__msg__SensorStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__SensorStatus__destroy(smarc_msgs__msg__SensorStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__SensorStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__SensorStatus__Sequence__init(smarc_msgs__msg__SensorStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SensorStatus * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__SensorStatus *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__SensorStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__SensorStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__SensorStatus__fini(&data[i - 1]);
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
smarc_msgs__msg__SensorStatus__Sequence__fini(smarc_msgs__msg__SensorStatus__Sequence * array)
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
      smarc_msgs__msg__SensorStatus__fini(&array->data[i]);
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

smarc_msgs__msg__SensorStatus__Sequence *
smarc_msgs__msg__SensorStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SensorStatus__Sequence * array = (smarc_msgs__msg__SensorStatus__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__SensorStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__SensorStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__SensorStatus__Sequence__destroy(smarc_msgs__msg__SensorStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__SensorStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__SensorStatus__Sequence__are_equal(const smarc_msgs__msg__SensorStatus__Sequence * lhs, const smarc_msgs__msg__SensorStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__SensorStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__SensorStatus__Sequence__copy(
  const smarc_msgs__msg__SensorStatus__Sequence * input,
  smarc_msgs__msg__SensorStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__SensorStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__SensorStatus * data =
      (smarc_msgs__msg__SensorStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__SensorStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__SensorStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__SensorStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
