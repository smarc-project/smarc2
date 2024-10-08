// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_mission_msgs:msg/BTCommand.idl
// generated code does not contain a copyright notice
#include "smarc_mission_msgs/msg/detail/bt_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `cmd_json`
// Member `fb_json`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_mission_msgs__msg__BTCommand__init(smarc_mission_msgs__msg__BTCommand * msg)
{
  if (!msg) {
    return false;
  }
  // msg_type
  // cmd_json
  if (!rosidl_runtime_c__String__init(&msg->cmd_json)) {
    smarc_mission_msgs__msg__BTCommand__fini(msg);
    return false;
  }
  // fb_json
  if (!rosidl_runtime_c__String__init(&msg->fb_json)) {
    smarc_mission_msgs__msg__BTCommand__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__msg__BTCommand__fini(smarc_mission_msgs__msg__BTCommand * msg)
{
  if (!msg) {
    return;
  }
  // msg_type
  // cmd_json
  rosidl_runtime_c__String__fini(&msg->cmd_json);
  // fb_json
  rosidl_runtime_c__String__fini(&msg->fb_json);
}

bool
smarc_mission_msgs__msg__BTCommand__are_equal(const smarc_mission_msgs__msg__BTCommand * lhs, const smarc_mission_msgs__msg__BTCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // msg_type
  if (lhs->msg_type != rhs->msg_type) {
    return false;
  }
  // cmd_json
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->cmd_json), &(rhs->cmd_json)))
  {
    return false;
  }
  // fb_json
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->fb_json), &(rhs->fb_json)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__msg__BTCommand__copy(
  const smarc_mission_msgs__msg__BTCommand * input,
  smarc_mission_msgs__msg__BTCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // msg_type
  output->msg_type = input->msg_type;
  // cmd_json
  if (!rosidl_runtime_c__String__copy(
      &(input->cmd_json), &(output->cmd_json)))
  {
    return false;
  }
  // fb_json
  if (!rosidl_runtime_c__String__copy(
      &(input->fb_json), &(output->fb_json)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__msg__BTCommand *
smarc_mission_msgs__msg__BTCommand__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__BTCommand * msg = (smarc_mission_msgs__msg__BTCommand *)allocator.allocate(sizeof(smarc_mission_msgs__msg__BTCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__msg__BTCommand));
  bool success = smarc_mission_msgs__msg__BTCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__msg__BTCommand__destroy(smarc_mission_msgs__msg__BTCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__msg__BTCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__msg__BTCommand__Sequence__init(smarc_mission_msgs__msg__BTCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__BTCommand * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__msg__BTCommand *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__msg__BTCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__msg__BTCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__msg__BTCommand__fini(&data[i - 1]);
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
smarc_mission_msgs__msg__BTCommand__Sequence__fini(smarc_mission_msgs__msg__BTCommand__Sequence * array)
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
      smarc_mission_msgs__msg__BTCommand__fini(&array->data[i]);
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

smarc_mission_msgs__msg__BTCommand__Sequence *
smarc_mission_msgs__msg__BTCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__BTCommand__Sequence * array = (smarc_mission_msgs__msg__BTCommand__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__msg__BTCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__msg__BTCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__msg__BTCommand__Sequence__destroy(smarc_mission_msgs__msg__BTCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__msg__BTCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__msg__BTCommand__Sequence__are_equal(const smarc_mission_msgs__msg__BTCommand__Sequence * lhs, const smarc_mission_msgs__msg__BTCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__msg__BTCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__msg__BTCommand__Sequence__copy(
  const smarc_mission_msgs__msg__BTCommand__Sequence * input,
  smarc_mission_msgs__msg__BTCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__msg__BTCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__msg__BTCommand * data =
      (smarc_mission_msgs__msg__BTCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__msg__BTCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__msg__BTCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__msg__BTCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
