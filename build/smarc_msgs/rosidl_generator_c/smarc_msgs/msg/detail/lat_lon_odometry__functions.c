// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice
#include "smarc_msgs/msg/detail/lat_lon_odometry__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `lat_lon_pose`
#include "geographic_msgs/msg/detail/geo_pose__functions.h"
// Member `twist`
#include "geometry_msgs/msg/detail/twist_with_covariance__functions.h"

bool
smarc_msgs__msg__LatLonOdometry__init(smarc_msgs__msg__LatLonOdometry * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    smarc_msgs__msg__LatLonOdometry__fini(msg);
    return false;
  }
  // lat_lon_pose
  if (!geographic_msgs__msg__GeoPose__init(&msg->lat_lon_pose)) {
    smarc_msgs__msg__LatLonOdometry__fini(msg);
    return false;
  }
  // covariance
  // twist
  if (!geometry_msgs__msg__TwistWithCovariance__init(&msg->twist)) {
    smarc_msgs__msg__LatLonOdometry__fini(msg);
    return false;
  }
  return true;
}

void
smarc_msgs__msg__LatLonOdometry__fini(smarc_msgs__msg__LatLonOdometry * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // lat_lon_pose
  geographic_msgs__msg__GeoPose__fini(&msg->lat_lon_pose);
  // covariance
  // twist
  geometry_msgs__msg__TwistWithCovariance__fini(&msg->twist);
}

bool
smarc_msgs__msg__LatLonOdometry__are_equal(const smarc_msgs__msg__LatLonOdometry * lhs, const smarc_msgs__msg__LatLonOdometry * rhs)
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
  // lat_lon_pose
  if (!geographic_msgs__msg__GeoPose__are_equal(
      &(lhs->lat_lon_pose), &(rhs->lat_lon_pose)))
  {
    return false;
  }
  // covariance
  for (size_t i = 0; i < 36; ++i) {
    if (lhs->covariance[i] != rhs->covariance[i]) {
      return false;
    }
  }
  // twist
  if (!geometry_msgs__msg__TwistWithCovariance__are_equal(
      &(lhs->twist), &(rhs->twist)))
  {
    return false;
  }
  return true;
}

bool
smarc_msgs__msg__LatLonOdometry__copy(
  const smarc_msgs__msg__LatLonOdometry * input,
  smarc_msgs__msg__LatLonOdometry * output)
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
  // lat_lon_pose
  if (!geographic_msgs__msg__GeoPose__copy(
      &(input->lat_lon_pose), &(output->lat_lon_pose)))
  {
    return false;
  }
  // covariance
  for (size_t i = 0; i < 36; ++i) {
    output->covariance[i] = input->covariance[i];
  }
  // twist
  if (!geometry_msgs__msg__TwistWithCovariance__copy(
      &(input->twist), &(output->twist)))
  {
    return false;
  }
  return true;
}

smarc_msgs__msg__LatLonOdometry *
smarc_msgs__msg__LatLonOdometry__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonOdometry * msg = (smarc_msgs__msg__LatLonOdometry *)allocator.allocate(sizeof(smarc_msgs__msg__LatLonOdometry), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_msgs__msg__LatLonOdometry));
  bool success = smarc_msgs__msg__LatLonOdometry__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_msgs__msg__LatLonOdometry__destroy(smarc_msgs__msg__LatLonOdometry * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_msgs__msg__LatLonOdometry__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_msgs__msg__LatLonOdometry__Sequence__init(smarc_msgs__msg__LatLonOdometry__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonOdometry * data = NULL;

  if (size) {
    data = (smarc_msgs__msg__LatLonOdometry *)allocator.zero_allocate(size, sizeof(smarc_msgs__msg__LatLonOdometry), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_msgs__msg__LatLonOdometry__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_msgs__msg__LatLonOdometry__fini(&data[i - 1]);
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
smarc_msgs__msg__LatLonOdometry__Sequence__fini(smarc_msgs__msg__LatLonOdometry__Sequence * array)
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
      smarc_msgs__msg__LatLonOdometry__fini(&array->data[i]);
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

smarc_msgs__msg__LatLonOdometry__Sequence *
smarc_msgs__msg__LatLonOdometry__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_msgs__msg__LatLonOdometry__Sequence * array = (smarc_msgs__msg__LatLonOdometry__Sequence *)allocator.allocate(sizeof(smarc_msgs__msg__LatLonOdometry__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_msgs__msg__LatLonOdometry__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_msgs__msg__LatLonOdometry__Sequence__destroy(smarc_msgs__msg__LatLonOdometry__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_msgs__msg__LatLonOdometry__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_msgs__msg__LatLonOdometry__Sequence__are_equal(const smarc_msgs__msg__LatLonOdometry__Sequence * lhs, const smarc_msgs__msg__LatLonOdometry__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_msgs__msg__LatLonOdometry__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_msgs__msg__LatLonOdometry__Sequence__copy(
  const smarc_msgs__msg__LatLonOdometry__Sequence * input,
  smarc_msgs__msg__LatLonOdometry__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_msgs__msg__LatLonOdometry);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_msgs__msg__LatLonOdometry * data =
      (smarc_msgs__msg__LatLonOdometry *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_msgs__msg__LatLonOdometry__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_msgs__msg__LatLonOdometry__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_msgs__msg__LatLonOdometry__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
