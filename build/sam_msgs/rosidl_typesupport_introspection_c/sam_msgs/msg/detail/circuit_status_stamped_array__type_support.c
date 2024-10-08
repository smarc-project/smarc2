// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from sam_msgs:msg/CircuitStatusStampedArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "sam_msgs/msg/detail/circuit_status_stamped_array__rosidl_typesupport_introspection_c.h"
#include "sam_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "sam_msgs/msg/detail/circuit_status_stamped_array__functions.h"
#include "sam_msgs/msg/detail/circuit_status_stamped_array__struct.h"


// Include directives for member types
// Member `array`
#include "sam_msgs/msg/circuit_status_stamped.h"
// Member `array`
#include "sam_msgs/msg/detail/circuit_status_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  sam_msgs__msg__CircuitStatusStampedArray__init(message_memory);
}

void sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_fini_function(void * message_memory)
{
  sam_msgs__msg__CircuitStatusStampedArray__fini(message_memory);
}

size_t sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__size_function__CircuitStatusStampedArray__array(
  const void * untyped_member)
{
  const sam_msgs__msg__CircuitStatusStamped__Sequence * member =
    (const sam_msgs__msg__CircuitStatusStamped__Sequence *)(untyped_member);
  return member->size;
}

const void * sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_const_function__CircuitStatusStampedArray__array(
  const void * untyped_member, size_t index)
{
  const sam_msgs__msg__CircuitStatusStamped__Sequence * member =
    (const sam_msgs__msg__CircuitStatusStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void * sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_function__CircuitStatusStampedArray__array(
  void * untyped_member, size_t index)
{
  sam_msgs__msg__CircuitStatusStamped__Sequence * member =
    (sam_msgs__msg__CircuitStatusStamped__Sequence *)(untyped_member);
  return &member->data[index];
}

void sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__fetch_function__CircuitStatusStampedArray__array(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const sam_msgs__msg__CircuitStatusStamped * item =
    ((const sam_msgs__msg__CircuitStatusStamped *)
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_const_function__CircuitStatusStampedArray__array(untyped_member, index));
  sam_msgs__msg__CircuitStatusStamped * value =
    (sam_msgs__msg__CircuitStatusStamped *)(untyped_value);
  *value = *item;
}

void sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__assign_function__CircuitStatusStampedArray__array(
  void * untyped_member, size_t index, const void * untyped_value)
{
  sam_msgs__msg__CircuitStatusStamped * item =
    ((sam_msgs__msg__CircuitStatusStamped *)
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_function__CircuitStatusStampedArray__array(untyped_member, index));
  const sam_msgs__msg__CircuitStatusStamped * value =
    (const sam_msgs__msg__CircuitStatusStamped *)(untyped_value);
  *item = *value;
}

bool sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__resize_function__CircuitStatusStampedArray__array(
  void * untyped_member, size_t size)
{
  sam_msgs__msg__CircuitStatusStamped__Sequence * member =
    (sam_msgs__msg__CircuitStatusStamped__Sequence *)(untyped_member);
  sam_msgs__msg__CircuitStatusStamped__Sequence__fini(member);
  return sam_msgs__msg__CircuitStatusStamped__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_member_array[1] = {
  {
    "array",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(sam_msgs__msg__CircuitStatusStampedArray, array),  // bytes offset in struct
    NULL,  // default value
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__size_function__CircuitStatusStampedArray__array,  // size() function pointer
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_const_function__CircuitStatusStampedArray__array,  // get_const(index) function pointer
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__get_function__CircuitStatusStampedArray__array,  // get(index) function pointer
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__fetch_function__CircuitStatusStampedArray__array,  // fetch(index, &value) function pointer
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__assign_function__CircuitStatusStampedArray__array,  // assign(index, value) function pointer
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__resize_function__CircuitStatusStampedArray__array  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_members = {
  "sam_msgs__msg",  // message namespace
  "CircuitStatusStampedArray",  // message name
  1,  // number of fields
  sizeof(sam_msgs__msg__CircuitStatusStampedArray),
  sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_member_array,  // message members
  sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_init_function,  // function to initialize message memory (memory has to be allocated)
  sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_type_support_handle = {
  0,
  &sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_sam_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sam_msgs, msg, CircuitStatusStampedArray)() {
  sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sam_msgs, msg, CircuitStatusStamped)();
  if (!sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_type_support_handle.typesupport_identifier) {
    sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &sam_msgs__msg__CircuitStatusStampedArray__rosidl_typesupport_introspection_c__CircuitStatusStampedArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
