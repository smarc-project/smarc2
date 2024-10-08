// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/CircuitStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__CircuitStatus __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__CircuitStatus __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CircuitStatus_
{
  using Type = CircuitStatus_<ContainerAllocator>;

  explicit CircuitStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->error_flags = 0;
      this->circuit_id = 0;
      this->voltage = 0.0f;
      this->current = 0.0f;
    }
  }

  explicit CircuitStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->error_flags = 0;
      this->circuit_id = 0;
      this->voltage = 0.0f;
      this->current = 0.0f;
    }
  }

  // field types and members
  using _error_flags_type =
    uint8_t;
  _error_flags_type error_flags;
  using _circuit_id_type =
    uint16_t;
  _circuit_id_type circuit_id;
  using _voltage_type =
    float;
  _voltage_type voltage;
  using _current_type =
    float;
  _current_type current;

  // setters for named parameter idiom
  Type & set__error_flags(
    const uint8_t & _arg)
  {
    this->error_flags = _arg;
    return *this;
  }
  Type & set__circuit_id(
    const uint16_t & _arg)
  {
    this->circuit_id = _arg;
    return *this;
  }
  Type & set__voltage(
    const float & _arg)
  {
    this->voltage = _arg;
    return *this;
  }
  Type & set__current(
    const float & _arg)
  {
    this->current = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t ERROR_FLAG_OVERVOLTAGE =
    1u;
  static constexpr uint8_t ERROR_FLAG_UNDERVOLTAGE =
    2u;
  static constexpr uint8_t ERROR_FLAG_OVERCURRENT =
    4u;
  static constexpr uint8_t ERROR_FLAG_UNDERCURRENT =
    8u;

  // pointer types
  using RawPtr =
    sam_msgs::msg::CircuitStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::CircuitStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::CircuitStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__CircuitStatus
    std::shared_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__CircuitStatus
    std::shared_ptr<sam_msgs::msg::CircuitStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CircuitStatus_ & other) const
  {
    if (this->error_flags != other.error_flags) {
      return false;
    }
    if (this->circuit_id != other.circuit_id) {
      return false;
    }
    if (this->voltage != other.voltage) {
      return false;
    }
    if (this->current != other.current) {
      return false;
    }
    return true;
  }
  bool operator!=(const CircuitStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CircuitStatus_

// alias to use template instance with default allocator
using CircuitStatus =
  sam_msgs::msg::CircuitStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t CircuitStatus_<ContainerAllocator>::ERROR_FLAG_OVERVOLTAGE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t CircuitStatus_<ContainerAllocator>::ERROR_FLAG_UNDERVOLTAGE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t CircuitStatus_<ContainerAllocator>::ERROR_FLAG_OVERCURRENT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t CircuitStatus_<ContainerAllocator>::ERROR_FLAG_UNDERCURRENT;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__STRUCT_HPP_
