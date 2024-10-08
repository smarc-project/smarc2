// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/SMTask.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/sm_task__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `max_duration`
#include "builtin_interfaces/msg/detail/duration__functions.h"
// Member `action_topic`
// Member `action_arguments`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_msgs__msg__SMTask__init(smarc_msgs__msg__SMTask * msg)
{
  if (!msg) {
    return false;
  }
  // task_id
  // x
  // y
  // depth
  // altitude
  // theta
  // max_duration
  if (!builtin_interfaces__msg__Duration__init(&msg->max_duration)) {
    smarc_msgs__msg__SMTask__fini(msg);
    return false;
  }
  // action_topic
  if (!rosidl_runtime_c__String__init(&msg->action_topic)) {
    smarc_msgs__msg__SMTask__fini(msg);
    return false;
  }
  // action_arguments
  if (!rosidl_runtime_c__String__init(&msg->action_arguments)) {
    smarc_msgs__msg__SMTask__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__SMTask__fini(smarc_msgs__msg__SMTask * msg)
{
  if (!msg) {
    return;
  }
  // task_id
  // x
  // y
  // depth
  // altitude
  // theta
  // max_duration
  builtin_interfaces__msg__Duration__fini(&msg->max_duration);
  // action_topic
  rosidl_runtime_c__String__fini(&msg->action_topic);
  // action_arguments
  rosidl_runtime_c__String__fini(&msg->action_arguments);
}

bool
smarc_msgs__msg__SMTask__are_equal(const smarc_msgs__msg__SMTask * lhs, const smarc_msgs__msg__SMTask * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // task_id
  if (lhs->task_id != rhs->task_id) {
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
  // depth
  if (lhs->depth != rhs->depth) {
    return false;
  }
  // altitude
  if (lhs->altitude != rhs->altitude) {
    return false;
  }
  // theta
  if (lhs->theta != rhs->theta) {
    return false;
  }
  // max_duration
  if (!builtin_interfaces__msg__Duration__are_equal(
      &(lhs->max_duration), &(rhs->max_duration)))
  {
    return false;
  }
  // action_topic
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->action_topic), &(rhs->action_topic)))
  {
    return false;
  }
  // action_arguments
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->action_arguments), &(rhs->action_arguments)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__SMTask__copy(
  const smarc_msgs__msg__SMTask * input,
  smarc_msgs__msg__SMTask * output)
{
  if (!input || !output) {
    return false;
  }
  // task_id
  output->task_id = input->task_id;
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // depth
  output->depth = input->depth;
  // altitude
  output->altitude = input->altitude;
  // theta
  output->theta = input->theta;
  // max_duration
  if (!builtin_interfaces__msg__Duration__copy(
      &(input->max_duration), &(output->max_duration)))
  {
    return false;
  }
  // action_topic
  if (!rosidl_runtime_c__String__copy(
      &(input->action_topic), &(output->action_topic)))
  {
    return false;
  }
  // action_arguments
  if (!rosidl_runtime_c__String__copy(
      &(input->action_arguments), &(output->action_arguments)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__SMTask *
smarc_msgs__msg__SMTask__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SMTask * msg = (smarc_msgs__msg__SMTask *)allocator.allocate(sizeof(smarc_msgs__msg__SMTask), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__SMTask));
  bool success = smarc_msgs__msg__SMTask__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__SMTask__destroy(smarc_msgs__msg__SMTask * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__SMTask__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__SMTask__Sequence__init(smarc_msgs__msg__SMTask__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SMTask * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__SMTask *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__SMTask), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__SMTask__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__SMTask__fini(&data[i - 1]);
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
smarc_msgs__msg__SMTask__Sequence__fini(smarc_msgs__msg__SMTask__Sequence * array)
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
      smarc_msgs__msg__SMTask__fini(&array->data[i]);
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

smarc_msgs__msg__SMTask__Sequence *
smarc_msgs__msg__SMTask__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__SMTask__Sequence * array = (smarc_msgs__msg__SMTask__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__SMTask__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__SMTask__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__SMTask__Sequence__destroy(smarc_msgs__msg__SMTask__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__SMTask__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__SMTask__Sequence__are_equal(const smarc_msgs__msg__SMTask__Sequence * lhs, const smarc_msgs__msg__SMTask__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__SMTask__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__SMTask__Sequence__copy(
  const smarc_msgs__msg__SMTask__Sequence * input,
  smarc_msgs__msg__SMTask__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__SMTask);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__SMTask * data =
      (smarc_msgs__msg__SMTask *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__SMTask__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__SMTask__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__SMTask__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
