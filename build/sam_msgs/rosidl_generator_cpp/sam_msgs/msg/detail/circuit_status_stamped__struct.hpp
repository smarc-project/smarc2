// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/CircuitStatusStamped.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'circuit'
#include "sam_msgs/msg/detail/circuit_status__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__CircuitStatusStamped __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__CircuitStatusStamped __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CircuitStatusStamped_
{
  using Type = CircuitStatusStamped_<ContainerAllocator>;

  explicit CircuitStatusStamped_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    circuit(_init)
  {
    (void)_init;
  }

  explicit CircuitStatusStamped_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    circuit(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _circuit_type =
    sam_msgs::msg::CircuitStatus_<ContainerAllocator>;
  _circuit_type circuit;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__circuit(
    const sam_msgs::msg::CircuitStatus_<ContainerAllocator> & _arg)
  {
    this->circuit = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__CircuitStatusStamped
    std::shared_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__CircuitStatusStamped
    std::shared_ptr<sam_msgs::msg::CircuitStatusStamped_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CircuitStatusStamped_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->circuit != other.circuit) {
      return false;
    }
    return true;
  }
  bool operator!=(const CircuitStatusStamped_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CircuitStatusStamped_

// alias to use template instance with default allocator
using CircuitStatusStamped =
  sam_msgs::msg::CircuitStatusStamped_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__STRUCT_HPP_
