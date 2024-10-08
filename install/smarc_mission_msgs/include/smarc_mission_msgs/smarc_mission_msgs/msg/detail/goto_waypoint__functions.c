// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice
#include "smarc_mission_msgs/msg/detail/goto_waypoint__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/detail/pose_stamped__functions.h"
// Member `name`
#include "rosidl_runtime_c/string_functions.h"

bool
smarc_mission_msgs__msg__GotoWaypoint__init(smarc_mission_msgs__msg__GotoWaypoint * msg)
{
  if (!msg) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__init(&msg->pose)) {
    smarc_mission_msgs__msg__GotoWaypoint__fini(msg);
    return false;
  }
  // goal_tolerance
  // z_control_mode
  // travel_altitude
  // travel_depth
  // speed_control_mode
  // travel_rpm
  // travel_speed
  // lat
  // lon
  // arrival_heading
  // use_heading
  // name
  if (!rosidl_runtime_c__String__init(&msg->name)) {
    smarc_mission_msgs__msg__GotoWaypoint__fini(msg);
    return false;
  }
  return true;
}

void
smarc_mission_msgs__msg__GotoWaypoint__fini(smarc_mission_msgs__msg__GotoWaypoint * msg)
{
  if (!msg) {
    return;
  }
  // pose
  geometry_msgs__msg__PoseStamped__fini(&msg->pose);
  // goal_tolerance
  // z_control_mode
  // travel_altitude
  // travel_depth
  // speed_control_mode
  // travel_rpm
  // travel_speed
  // lat
  // lon
  // arrival_heading
  // use_heading
  // name
  rosidl_runtime_c__String__fini(&msg->name);
}

bool
smarc_mission_msgs__msg__GotoWaypoint__are_equal(const smarc_mission_msgs__msg__GotoWaypoint * lhs, const smarc_mission_msgs__msg__GotoWaypoint * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  // goal_tolerance
  if (lhs->goal_tolerance != rhs->goal_tolerance) {
    return false;
  }
  // z_control_mode
  if (lhs->z_control_mode != rhs->z_control_mode) {
    return false;
  }
  // travel_altitude
  if (lhs->travel_altitude != rhs->travel_altitude) {
    return false;
  }
  // travel_depth
  if (lhs->travel_depth != rhs->travel_depth) {
    return false;
  }
  // speed_control_mode
  if (lhs->speed_control_mode != rhs->speed_control_mode) {
    return false;
  }
  // travel_rpm
  if (lhs->travel_rpm != rhs->travel_rpm) {
    return false;
  }
  // travel_speed
  if (lhs->travel_speed != rhs->travel_speed) {
    return false;
  }
  // lat
  if (lhs->lat != rhs->lat) {
    return false;
  }
  // lon
  if (lhs->lon != rhs->lon) {
    return false;
  }
  // arrival_heading
  if (lhs->arrival_heading != rhs->arrival_heading) {
    return false;
  }
  // use_heading
  if (lhs->use_heading != rhs->use_heading) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->name), &(rhs->name)))
  {
    return false;
  }
  return true;
}

bool
smarc_mission_msgs__msg__GotoWaypoint__copy(
  const smarc_mission_msgs__msg__GotoWaypoint * input,
  smarc_mission_msgs__msg__GotoWaypoint * output)
{
  if (!input || !output) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  // goal_tolerance
  output->goal_tolerance = input->goal_tolerance;
  // z_control_mode
  output->z_control_mode = input->z_control_mode;
  // travel_altitude
  output->travel_altitude = input->travel_altitude;
  // travel_depth
  output->travel_depth = input->travel_depth;
  // speed_control_mode
  output->speed_control_mode = input->speed_control_mode;
  // travel_rpm
  output->travel_rpm = input->travel_rpm;
  // travel_speed
  output->travel_speed = input->travel_speed;
  // lat
  output->lat = input->lat;
  // lon
  output->lon = input->lon;
  // arrival_heading
  output->arrival_heading = input->arrival_heading;
  // use_heading
  output->use_heading = input->use_heading;
  // name
  if (!rosidl_runtime_c__String__copy(
      &(input->name), &(output->name)))
  {
    return false;
  }
  return true;
}

smarc_mission_msgs__msg__GotoWaypoint *
smarc_mission_msgs__msg__GotoWaypoint__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__GotoWaypoint * msg = (smarc_mission_msgs__msg__GotoWaypoint *)allocator.allocate(sizeof(smarc_mission_msgs__msg__GotoWaypoint), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smarc_mission_msgs__msg__GotoWaypoint));
  bool success = smarc_mission_msgs__msg__GotoWaypoint__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smarc_mission_msgs__msg__GotoWaypoint__destroy(smarc_mission_msgs__msg__GotoWaypoint * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smarc_mission_msgs__msg__GotoWaypoint__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smarc_mission_msgs__msg__GotoWaypoint__Sequence__init(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__GotoWaypoint * data = NULL;

  if (size) {
    data = (smarc_mission_msgs__msg__GotoWaypoint *)allocator.zero_allocate(size, sizeof(smarc_mission_msgs__msg__GotoWaypoint), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smarc_mission_msgs__msg__GotoWaypoint__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smarc_mission_msgs__msg__GotoWaypoint__fini(&data[i - 1]);
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
smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array)
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
      smarc_mission_msgs__msg__GotoWaypoint__fini(&array->data[i]);
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

smarc_mission_msgs__msg__GotoWaypoint__Sequence *
smarc_mission_msgs__msg__GotoWaypoint__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smarc_mission_msgs__msg__GotoWaypoint__Sequence * array = (smarc_mission_msgs__msg__GotoWaypoint__Sequence *)allocator.allocate(sizeof(smarc_mission_msgs__msg__GotoWaypoint__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smarc_mission_msgs__msg__GotoWaypoint__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smarc_mission_msgs__msg__GotoWaypoint__Sequence__destroy(smarc_mission_msgs__msg__GotoWaypoint__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smarc_mission_msgs__msg__GotoWaypoint__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smarc_mission_msgs__msg__GotoWaypoint__Sequence__are_equal(const smarc_mission_msgs__msg__GotoWaypoint__Sequence * lhs, const smarc_mission_msgs__msg__GotoWaypoint__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smarc_mission_msgs__msg__GotoWaypoint__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smarc_mission_msgs__msg__GotoWaypoint__Sequence__copy(
  const smarc_mission_msgs__msg__GotoWaypoint__Sequence * input,
  smarc_mission_msgs__msg__GotoWaypoint__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smarc_mission_msgs__msg__GotoWaypoint);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smarc_mission_msgs__msg__GotoWaypoint * data =
      (smarc_mission_msgs__msg__GotoWaypoint *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smarc_mission_msgs__msg__GotoWaypoint__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smarc_mission_msgs__msg__GotoWaypoint__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smarc_mission_msgs__msg__GotoWaypoint__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
