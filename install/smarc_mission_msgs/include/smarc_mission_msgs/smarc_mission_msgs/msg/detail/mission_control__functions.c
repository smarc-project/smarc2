// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice
#include "smarc_mission_msgs/msg/detail/mission_control__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `name`
// Member `hash`
// Member `feedback_str`
#include "rosidl_runtime_c/string_functions.h"
// Member `waypoints`
#include "smarc_mission_msgs/msg/detail/goto_waypoint__functions.h"

bool
smarc_mission_msgs__msg__MissionControl__init(smarc_mission_msgs__msg__MissionControl * msg)
{
  if (!msg) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__init(&msg->name)) {
    smarc_mission_msgs__msg__MissionControl__fini(msg);
    return false;
  }
  // hash
  if (!rosidl_runtime_c__String__init(&msg->hash)) {
    smarc_mission_msgs__msg__MissionControl__fini(msg);
    return false;
  }
  // timeout
  // command
  // plan_state
  // feedback_str
  if (!rosidl_runtime_c__String__init(&msg->feedback_str)) {
    smarc_mission_msgs__msg__MissionControl__fini(msg);
    return false;
  }
  // waypoints
  if (!smarc_mission_msgs__msg__GotoWaypoint__Sequence__init(&msg->waypoints, 0)) {
    smarc_mission_msgs__msg__MissionControl__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__msg__MissionControl__fini(smarc_mission_msgs__msg__MissionControl * msg)
{
  if (!msg) {
    return;
  }
  // name
  rosidl_runtime_c__String__fini(&msg->name);
  // hash
  rosidl_runtime_c__String__fini(&msg->hash);
  // timeout
  // command
  // plan_state
  // feedback_str
  rosidl_runtime_c__String__fini(&msg->feedback_str);
  // waypoints
  smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini(&msg->waypoints);
}

bool
smarc_mission_msgs__msg__MissionControl__are_equal(const smarc_mission_msgs__msg__MissionControl * lhs, const smarc_mission_msgs__msg__MissionControl * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->name), &(rhs->name)))
  {
    return false;
  }
  // hash
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->hash), &(rhs->hash)))
  {
    return false;
  }
  // timeout
  if (lhs->timeout != rhs->timeout) {
    return false;
  }
  // command
  if (lhs->command != rhs->command) {
    return false;
  }
  // plan_state
  if (lhs->plan_state != rhs->plan_state) {
    return false;
  }
  // feedback_str
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->feedback_str), &(rhs->feedback_str)))
  {
    return false;
  }
  // waypoints
  if (!smarc_mission_msgs__msg__GotoWaypoint__Sequence__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__msg__MissionControl__copy(
  const smarc_mission_msgs__msg__MissionControl * input,
  smarc_mission_msgs__msg__MissionControl * output)
{
  if (!input || !output) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__copy(
      &(input->name), &(output->name)))
  {
    return false;
  }
  // hash
  if (!rosidl_runtime_c__String__copy(
      &(input->hash), &(output->hash)))
  {
    return false;
  }
  // timeout
  output->timeout = input->timeout;
  // command
  output->command = input->command;
  // plan_state
  output->plan_state = input->plan_state;
  // feedback_str
  if (!rosidl_runtime_c__String__copy(
      &(input->feedback_str), &(output->feedback_str)))
  {
    return false;
  }
  // waypoints
  if (!smarc_mission_msgs__msg__GotoWaypoint__Sequence__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__msg__MissionControl *
smarc_mission_msgs__msg__MissionControl__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__MissionControl * msg = (smarc_mission_msgs__msg__MissionControl *)allocator.allocate(sizeof(smarc_mission_msgs__msg__MissionControl), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__msg__MissionControl));
  bool success = smarc_mission_msgs__msg__MissionControl__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__msg__MissionControl__destroy(smarc_mission_msgs__msg__MissionControl * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__msg__MissionControl__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__msg__MissionControl__Sequence__init(smarc_mission_msgs__msg__MissionControl__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__MissionControl * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__msg__MissionControl *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__msg__MissionControl), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__msg__MissionControl__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__msg__MissionControl__fini(&data[i - 1]);
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
smarc_mission_msgs__msg__MissionControl__Sequence__fini(smarc_mission_msgs__msg__MissionControl__Sequence * array)
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
      smarc_mission_msgs__msg__MissionControl__fini(&array->data[i]);
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

smarc_mission_msgs__msg__MissionControl__Sequence *
smarc_mission_msgs__msg__MissionControl__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__MissionControl__Sequence * array = (smarc_mission_msgs__msg__MissionControl__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__msg__MissionControl__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__msg__MissionControl__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__msg__MissionControl__Sequence__destroy(smarc_mission_msgs__msg__MissionControl__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__msg__MissionControl__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__msg__MissionControl__Sequence__are_equal(const smarc_mission_msgs__msg__MissionControl__Sequence * lhs, const smarc_mission_msgs__msg__MissionControl__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__msg__MissionControl__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__msg__MissionControl__Sequence__copy(
  const smarc_mission_msgs__msg__MissionControl__Sequence * input,
  smarc_mission_msgs__msg__MissionControl__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__msg__MissionControl);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__msg__MissionControl * data =
      (smarc_mission_msgs__msg__MissionControl *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__msg__MissionControl__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__msg__MissionControl__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__msg__MissionControl__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
