// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice
#include "sam_msgs/srv/detail/uavcan_update_battery__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
sam_msgs__srv__UavcanUpdateBattery_Request__init(sam_msgs__srv__UavcanUpdateBattery_Request * msg)
{
  if (!msg) {
    return false;
  }
  // node_id
  // command
  // charge
  return true;
}

void
sam_msgs__srv__UavcanUpdateBattery_Request__fini(sam_msgs__srv__UavcanUpdateBattery_Request * msg)
{
  if (!msg) {
    return;
  }
  // node_id
  // command
  // charge
}

bool
sam_msgs__srv__UavcanUpdateBattery_Request__are_equal(const sam_msgs__srv__UavcanUpdateBattery_Request * lhs, const sam_msgs__srv__UavcanUpdateBattery_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // node_id
  if (lhs->node_id != rhs->node_id) {
    return false;
  }
  // command
  if (lhs->command != rhs->command) {
    return false;
  }
  // charge
  if (lhs->charge != rhs->charge) {
    return false;
  }
  return true;
}

bool
sam_msgs__srv__UavcanUpdateBattery_Request__copy(
  const sam_msgs__srv__UavcanUpdateBattery_Request * input,
  sam_msgs__srv__UavcanUpdateBattery_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // node_id
  output->node_id = input->node_id;
  // command
  output->command = input->command;
  // charge
  output->charge = input->charge;
  return true;
}

sam_msgs__srv__UavcanUpdateBattery_Request *
sam_msgs__srv__UavcanUpdateBattery_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Request * msg = (sam_msgs__srv__UavcanUpdateBattery_Request *)allocator.allocate(sizeof(sam_msgs__srv__UavcanUpdateBattery_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__srv__UavcanUpdateBattery_Request));
  bool success = sam_msgs__srv__UavcanUpdateBattery_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__srv__UavcanUpdateBattery_Request__destroy(sam_msgs__srv__UavcanUpdateBattery_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__srv__UavcanUpdateBattery_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__init(sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Request * data = NULL;

  if (size) {
    data = (sam_msgs__srv__UavcanUpdateBattery_Request *)allocator.zero_allocate(size, sizeof(sam_msgs__srv__UavcanUpdateBattery_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__srv__UavcanUpdateBattery_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__srv__UavcanUpdateBattery_Request__fini(&data[i - 1]);
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
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__fini(sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * array)
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
      sam_msgs__srv__UavcanUpdateBattery_Request__fini(&array->data[i]);
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

sam_msgs__srv__UavcanUpdateBattery_Request__Sequence *
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * array = (sam_msgs__srv__UavcanUpdateBattery_Request__Sequence *)allocator.allocate(sizeof(sam_msgs__srv__UavcanUpdateBattery_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__destroy(sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__are_equal(const sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * lhs, const sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__srv__UavcanUpdateBattery_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__srv__UavcanUpdateBattery_Request__Sequence__copy(
  const sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * input,
  sam_msgs__srv__UavcanUpdateBattery_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__srv__UavcanUpdateBattery_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__srv__UavcanUpdateBattery_Request * data =
      (sam_msgs__srv__UavcanUpdateBattery_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__srv__UavcanUpdateBattery_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__srv__UavcanUpdateBattery_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__srv__UavcanUpdateBattery_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
sam_msgs__srv__UavcanUpdateBattery_Response__init(sam_msgs__srv__UavcanUpdateBattery_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  return true;
}

void
sam_msgs__srv__UavcanUpdateBattery_Response__fini(sam_msgs__srv__UavcanUpdateBattery_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
}

bool
sam_msgs__srv__UavcanUpdateBattery_Response__are_equal(const sam_msgs__srv__UavcanUpdateBattery_Response * lhs, const sam_msgs__srv__UavcanUpdateBattery_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  return true;
}

bool
sam_msgs__srv__UavcanUpdateBattery_Response__copy(
  const sam_msgs__srv__UavcanUpdateBattery_Response * input,
  sam_msgs__srv__UavcanUpdateBattery_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  return true;
}

sam_msgs__srv__UavcanUpdateBattery_Response *
sam_msgs__srv__UavcanUpdateBattery_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Response * msg = (sam_msgs__srv__UavcanUpdateBattery_Response *)allocator.allocate(sizeof(sam_msgs__srv__UavcanUpdateBattery_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__srv__UavcanUpdateBattery_Response));
  bool success = sam_msgs__srv__UavcanUpdateBattery_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__srv__UavcanUpdateBattery_Response__destroy(sam_msgs__srv__UavcanUpdateBattery_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__srv__UavcanUpdateBattery_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__init(sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Response * data = NULL;

  if (size) {
    data = (sam_msgs__srv__UavcanUpdateBattery_Response *)allocator.zero_allocate(size, sizeof(sam_msgs__srv__UavcanUpdateBattery_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__srv__UavcanUpdateBattery_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__srv__UavcanUpdateBattery_Response__fini(&data[i - 1]);
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
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__fini(sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * array)
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
      sam_msgs__srv__UavcanUpdateBattery_Response__fini(&array->data[i]);
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

sam_msgs__srv__UavcanUpdateBattery_Response__Sequence *
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * array = (sam_msgs__srv__UavcanUpdateBattery_Response__Sequence *)allocator.allocate(sizeof(sam_msgs__srv__UavcanUpdateBattery_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__destroy(sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__are_equal(const sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * lhs, const sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__srv__UavcanUpdateBattery_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__srv__UavcanUpdateBattery_Response__Sequence__copy(
  const sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * input,
  sam_msgs__srv__UavcanUpdateBattery_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__srv__UavcanUpdateBattery_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__srv__UavcanUpdateBattery_Response * data =
      (sam_msgs__srv__UavcanUpdateBattery_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__srv__UavcanUpdateBattery_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__srv__UavcanUpdateBattery_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__srv__UavcanUpdateBattery_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
