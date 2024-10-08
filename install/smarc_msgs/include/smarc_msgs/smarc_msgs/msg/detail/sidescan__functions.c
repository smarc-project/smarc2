// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/sidescan__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `port_channel`
// Member `starboard_channel`
// Member `port_channel_angle_high`
// Member `port_channel_angle_low`
// Member `starboard_channel_angle_high`
// Member `starboard_channel_angle_low`
// Member `extra_channel`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
smarc_msgs__msg__Sidescan__init(smarc_msgs__msg__Sidescan * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // type
  // time
  // frequency_id
  // gain
  // decimation
  // max_duration
  // port_channel
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->port_channel, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // starboard_channel
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->starboard_channel, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // port_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->port_channel_angle_high, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // port_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->port_channel_angle_low, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // starboard_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->starboard_channel_angle_high, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // starboard_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->starboard_channel_angle_low, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  // extra_channel
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->extra_channel, 0)) {
    smarc_msgs__msg__Sidescan__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__Sidescan__fini(smarc_msgs__msg__Sidescan * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // type
  // time
  // frequency_id
  // gain
  // decimation
  // max_duration
  // port_channel
  rosidl_runtime_c__uint8__Sequence__fini(&msg->port_channel);
  // starboard_channel
  rosidl_runtime_c__uint8__Sequence__fini(&msg->starboard_channel);
  // port_channel_angle_high
  rosidl_runtime_c__uint8__Sequence__fini(&msg->port_channel_angle_high);
  // port_channel_angle_low
  rosidl_runtime_c__uint8__Sequence__fini(&msg->port_channel_angle_low);
  // starboard_channel_angle_high
  rosidl_runtime_c__uint8__Sequence__fini(&msg->starboard_channel_angle_high);
  // starboard_channel_angle_low
  rosidl_runtime_c__uint8__Sequence__fini(&msg->starboard_channel_angle_low);
  // extra_channel
  rosidl_runtime_c__uint8__Sequence__fini(&msg->extra_channel);
}

bool
smarc_msgs__msg__Sidescan__are_equal(const smarc_msgs__msg__Sidescan * lhs, const smarc_msgs__msg__Sidescan * rhs)
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
  // type
  if (lhs->type != rhs->type) {
    return false;
  }
  // time
  if (lhs->time != rhs->time) {
    return false;
  }
  // frequency_id
  if (lhs->frequency_id != rhs->frequency_id) {
    return false;
  }
  // gain
  if (lhs->gain != rhs->gain) {
    return false;
  }
  // decimation
  if (lhs->decimation != rhs->decimation) {
    return false;
  }
  // max_duration
  if (lhs->max_duration != rhs->max_duration) {
    return false;
  }
  // port_channel
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->port_channel), &(rhs->port_channel)))
  {
    return false;
  }
  // starboard_channel
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->starboard_channel), &(rhs->starboard_channel)))
  {
    return false;
  }
  // port_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->port_channel_angle_high), &(rhs->port_channel_angle_high)))
  {
    return false;
  }
  // port_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->port_channel_angle_low), &(rhs->port_channel_angle_low)))
  {
    return false;
  }
  // starboard_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->starboard_channel_angle_high), &(rhs->starboard_channel_angle_high)))
  {
    return false;
  }
  // starboard_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->starboard_channel_angle_low), &(rhs->starboard_channel_angle_low)))
  {
    return false;
  }
  // extra_channel
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->extra_channel), &(rhs->extra_channel)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__Sidescan__copy(
  const smarc_msgs__msg__Sidescan * input,
  smarc_msgs__msg__Sidescan * output)
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
  // type
  output->type = input->type;
  // time
  output->time = input->time;
  // frequency_id
  output->frequency_id = input->frequency_id;
  // gain
  output->gain = input->gain;
  // decimation
  output->decimation = input->decimation;
  // max_duration
  output->max_duration = input->max_duration;
  // port_channel
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->port_channel), &(output->port_channel)))
  {
    return false;
  }
  // starboard_channel
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->starboard_channel), &(output->starboard_channel)))
  {
    return false;
  }
  // port_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->port_channel_angle_high), &(output->port_channel_angle_high)))
  {
    return false;
  }
  // port_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->port_channel_angle_low), &(output->port_channel_angle_low)))
  {
    return false;
  }
  // starboard_channel_angle_high
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->starboard_channel_angle_high), &(output->starboard_channel_angle_high)))
  {
    return false;
  }
  // starboard_channel_angle_low
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->starboard_channel_angle_low), &(output->starboard_channel_angle_low)))
  {
    return false;
  }
  // extra_channel
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->extra_channel), &(output->extra_channel)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__Sidescan *
smarc_msgs__msg__Sidescan__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__Sidescan * msg = (smarc_msgs__msg__Sidescan *)allocator.allocate(sizeof(smarc_msgs__msg__Sidescan), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__Sidescan));
  bool success = smarc_msgs__msg__Sidescan__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__Sidescan__destroy(smarc_msgs__msg__Sidescan * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__Sidescan__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__Sidescan__Sequence__init(smarc_msgs__msg__Sidescan__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__Sidescan * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__Sidescan *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__Sidescan), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__Sidescan__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__Sidescan__fini(&data[i - 1]);
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
smarc_msgs__msg__Sidescan__Sequence__fini(smarc_msgs__msg__Sidescan__Sequence * array)
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
      smarc_msgs__msg__Sidescan__fini(&array->data[i]);
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

smarc_msgs__msg__Sidescan__Sequence *
smarc_msgs__msg__Sidescan__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__Sidescan__Sequence * array = (smarc_msgs__msg__Sidescan__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__Sidescan__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__Sidescan__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__Sidescan__Sequence__destroy(smarc_msgs__msg__Sidescan__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__Sidescan__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__Sidescan__Sequence__are_equal(const smarc_msgs__msg__Sidescan__Sequence * lhs, const smarc_msgs__msg__Sidescan__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__Sidescan__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__Sidescan__Sequence__copy(
  const smarc_msgs__msg__Sidescan__Sequence * input,
  smarc_msgs__msg__Sidescan__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__Sidescan);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__Sidescan * data =
      (smarc_msgs__msg__Sidescan *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__Sidescan__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__Sidescan__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__Sidescan__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
