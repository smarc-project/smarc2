// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/CircuitStatusStampedArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'array'
#include "sam_msgs/msg/detail/circuit_status_stamped__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__CircuitStatusStampedArray __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__CircuitStatusStampedArray __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CircuitStatusStampedArray_
{
  using Type = CircuitStatusStampedArray_<ContainerAllocator>;

  explicit CircuitStatusStampedArray_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit CircuitStatusStampedArray_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _array_type =
    std::vector<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>>;
  _array_type array;

  // setters for named parameter idiom
  Type & set__array(
    const std::vector<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>> & _arg)
  {
    this->array = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__CircuitStatusStampedArray
    std::shared_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__CircuitStatusStampedArray
    std::shared_ptr<sam_msgs::msg::CircuitStatusStampedArray_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CircuitStatusStampedArray_ & other) const
  {
    if (this->array != other.array) {
      return false;
    }
    return true;
  }
  bool operator!=(const CircuitStatusStampedArray_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CircuitStatusStampedArray_

// alias to use template instance with default allocator
using CircuitStatusStampedArray =
  sam_msgs::msg::CircuitStatusStampedArray_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__STRUCT_HPP_
