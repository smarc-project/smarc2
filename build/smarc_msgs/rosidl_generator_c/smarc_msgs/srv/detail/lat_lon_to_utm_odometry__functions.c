// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/srv/detail/lat_lon_to_utm_odometry__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `lat_lon_odom`
#include "smarc_msgs/msg/detail/lat_lon_odometry__functions.h"

bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__init(smarc_msgs__srv__LatLonToUTMOdometry_Request * msg)
{
  if (!msg) {
    return false;
  }
  // lat_lon_odom
  if (!smarc_msgs__msg__LatLonOdometry__init(&msg->lat_lon_odom)) {
    smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(smarc_msgs__srv__LatLonToUTMOdometry_Request * msg)
{
  if (!msg) {
    return;
  }
  // lat_lon_odom
  smarc_msgs__msg__LatLonOdometry__fini(&msg->lat_lon_odom);
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__are_equal(const smarc_msgs__srv__LatLonToUTMOdometry_Request * lhs, const smarc_msgs__srv__LatLonToUTMOdometry_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // lat_lon_odom
  if (!smarc_msgs__msg__LatLonOdometry__are_equal(
      &(lhs->lat_lon_odom), &(rhs->lat_lon_odom)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__copy(
  const smarc_msgs__srv__LatLonToUTMOdometry_Request * input,
  smarc_msgs__srv__LatLonToUTMOdometry_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // lat_lon_odom
  if (!smarc_msgs__msg__LatLonOdometry__copy(
      &(input->lat_lon_odom), &(output->lat_lon_odom)))
  {
    return false;
  }
  return true;
}

smarc_msgs__srv__LatLonToUTMOdometry_Request *
smarc_msgs__srv__LatLonToUTMOdometry_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Request * msg = (smarc_msgs__srv__LatLonToUTMOdometry_Request *)allocator.allocate(sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request));
  bool success = smarc_msgs__srv__LatLonToUTMOdometry_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Request__destroy(smarc_msgs__srv__LatLonToUTMOdometry_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__init(smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Request * data = NULL;

  if (size) {
    data = (smarc_msgs__srv__LatLonToUTMOdometry_Request *)allocator.zero_allocate(size, sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__srv__LatLonToUTMOdometry_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(&data[i - 1]);
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
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__fini(smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * array)
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
      smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(&array->data[i]);
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

smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence *
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * array = (smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence *)allocator.allocate(sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__destroy(smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__are_equal(const smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * lhs, const smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__srv__LatLonToUTMOdometry_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence__copy(
  const smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * input,
  smarc_msgs__srv__LatLonToUTMOdometry_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__srv__LatLonToUTMOdometry_Request * data =
      (smarc_msgs__srv__LatLonToUTMOdometry_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__srv__LatLonToUTMOdometry_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__srv__LatLonToUTMOdometry_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__srv__LatLonToUTMOdometry_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `odom`
#include "nav_msgs/msg/detail/odometry__functions.h"

bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__init(smarc_msgs__srv__LatLonToUTMOdometry_Response * msg)
{
  if (!msg) {
    return false;
  }
  // odom
  if (!nav_msgs__msg__Odometry__init(&msg->odom)) {
    smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(smarc_msgs__srv__LatLonToUTMOdometry_Response * msg)
{
  if (!msg) {
    return;
  }
  // odom
  nav_msgs__msg__Odometry__fini(&msg->odom);
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__are_equal(const smarc_msgs__srv__LatLonToUTMOdometry_Response * lhs, const smarc_msgs__srv__LatLonToUTMOdometry_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // odom
  if (!nav_msgs__msg__Odometry__are_equal(
      &(lhs->odom), &(rhs->odom)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__copy(
  const smarc_msgs__srv__LatLonToUTMOdometry_Response * input,
  smarc_msgs__srv__LatLonToUTMOdometry_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // odom
  if (!nav_msgs__msg__Odometry__copy(
      &(input->odom), &(output->odom)))
  {
    return false;
  }
  return true;
}

smarc_msgs__srv__LatLonToUTMOdometry_Response *
smarc_msgs__srv__LatLonToUTMOdometry_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Response * msg = (smarc_msgs__srv__LatLonToUTMOdometry_Response *)allocator.allocate(sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response));
  bool success = smarc_msgs__srv__LatLonToUTMOdometry_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Response__destroy(smarc_msgs__srv__LatLonToUTMOdometry_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__init(smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Response * data = NULL;

  if (size) {
    data = (smarc_msgs__srv__LatLonToUTMOdometry_Response *)allocator.zero_allocate(size, sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__srv__LatLonToUTMOdometry_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(&data[i - 1]);
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
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__fini(smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * array)
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
      smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(&array->data[i]);
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

smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence *
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * array = (smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence *)allocator.allocate(sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__destroy(smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__are_equal(const smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * lhs, const smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__srv__LatLonToUTMOdometry_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence__copy(
  const smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * input,
  smarc_msgs__srv__LatLonToUTMOdometry_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__srv__LatLonToUTMOdometry_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__srv__LatLonToUTMOdometry_Response * data =
      (smarc_msgs__srv__LatLonToUTMOdometry_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__srv__LatLonToUTMOdometry_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__srv__LatLonToUTMOdometry_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__srv__LatLonToUTMOdometry_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
