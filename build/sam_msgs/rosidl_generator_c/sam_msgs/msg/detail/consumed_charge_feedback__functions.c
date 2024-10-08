// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice
#include "sam_msgs/msg/detail/consumed_charge_feedback__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
sam_msgs__msg__ConsumedChargeFeedback__init(sam_msgs__msg__ConsumedChargeFeedback * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    sam_msgs__msg__ConsumedChargeFeedback__fini(msg);
    return false;
  }
  // main
  // esc1
  // esc2
  // esc3
  // v20
  // v12
  // v7
  // v5
  // v33
  return true;
}

void
sam_msgs__msg__ConsumedChargeFeedback__fini(sam_msgs__msg__ConsumedChargeFeedback * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // main
  // esc1
  // esc2
  // esc3
  // v20
  // v12
  // v7
  // v5
  // v33
}

bool
sam_msgs__msg__ConsumedChargeFeedback__are_equal(const sam_msgs__msg__ConsumedChargeFeedback * lhs, const sam_msgs__msg__ConsumedChargeFeedback * rhs)
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
  // main
  if (lhs->main != rhs->main) {
    return false;
  }
  // esc1
  if (lhs->esc1 != rhs->esc1) {
    return false;
  }
  // esc2
  if (lhs->esc2 != rhs->esc2) {
    return false;
  }
  // esc3
  if (lhs->esc3 != rhs->esc3) {
    return false;
  }
  // v20
  if (lhs->v20 != rhs->v20) {
    return false;
  }
  // v12
  if (lhs->v12 != rhs->v12) {
    return false;
  }
  // v7
  if (lhs->v7 != rhs->v7) {
    return false;
  }
  // v5
  if (lhs->v5 != rhs->v5) {
    return false;
  }
  // v33
  if (lhs->v33 != rhs->v33) {
    return false;
  }
  return true;
}

bool
sam_msgs__msg__ConsumedChargeFeedback__copy(
  const sam_msgs__msg__ConsumedChargeFeedback * input,
  sam_msgs__msg__ConsumedChargeFeedback * output)
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
  // main
  output->main = input->main;
  // esc1
  output->esc1 = input->esc1;
  // esc2
  output->esc2 = input->esc2;
  // esc3
  output->esc3 = input->esc3;
  // v20
  output->v20 = input->v20;
  // v12
  output->v12 = input->v12;
  // v7
  output->v7 = input->v7;
  // v5
  output->v5 = input->v5;
  // v33
  output->v33 = input->v33;
  return true;
}

sam_msgs__msg__ConsumedChargeFeedback *
sam_msgs__msg__ConsumedChargeFeedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ConsumedChargeFeedback * msg = (sam_msgs__msg__ConsumedChargeFeedback *)allocator.allocate(sizeof(sam_msgs__msg__ConsumedChargeFeedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(sam_msgs__msg__ConsumedChargeFeedback));
  bool success = sam_msgs__msg__ConsumedChargeFeedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
sam_msgs__msg__ConsumedChargeFeedback__destroy(sam_msgs__msg__ConsumedChargeFeedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    sam_msgs__msg__ConsumedChargeFeedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
sam_msgs__msg__ConsumedChargeFeedback__Sequence__init(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ConsumedChargeFeedback * data = NULL;

  if (size) {
    data = (sam_msgs__msg__ConsumedChargeFeedback *)allocator.zero_allocate(size, sizeof(sam_msgs__msg__ConsumedChargeFeedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = sam_msgs__msg__ConsumedChargeFeedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        sam_msgs__msg__ConsumedChargeFeedback__fini(&data[i - 1]);
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
sam_msgs__msg__ConsumedChargeFeedback__Sequence__fini(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array)
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
      sam_msgs__msg__ConsumedChargeFeedback__fini(&array->data[i]);
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

sam_msgs__msg__ConsumedChargeFeedback__Sequence *
sam_msgs__msg__ConsumedChargeFeedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  sam_msgs__msg__ConsumedChargeFeedback__Sequence * array = (sam_msgs__msg__ConsumedChargeFeedback__Sequence *)allocator.allocate(sizeof(sam_msgs__msg__ConsumedChargeFeedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = sam_msgs__msg__ConsumedChargeFeedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
sam_msgs__msg__ConsumedChargeFeedback__Sequence__destroy(sam_msgs__msg__ConsumedChargeFeedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    sam_msgs__msg__ConsumedChargeFeedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
sam_msgs__msg__ConsumedChargeFeedback__Sequence__are_equal(const sam_msgs__msg__ConsumedChargeFeedback__Sequence * lhs, const sam_msgs__msg__ConsumedChargeFeedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!sam_msgs__msg__ConsumedChargeFeedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
sam_msgs__msg__ConsumedChargeFeedback__Sequence__copy(
  const sam_msgs__msg__ConsumedChargeFeedback__Sequence * input,
  sam_msgs__msg__ConsumedChargeFeedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(sam_msgs__msg__ConsumedChargeFeedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    sam_msgs__msg__ConsumedChargeFeedback * data =
      (sam_msgs__msg__ConsumedChargeFeedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!sam_msgs__msg__ConsumedChargeFeedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          sam_msgs__msg__ConsumedChargeFeedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!sam_msgs__msg__ConsumedChargeFeedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
