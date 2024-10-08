// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__Command __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__Command __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Command_
{
  using Type = Command_<ContainerAllocator>;

  explicit Command_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->actuator_id = 0;
      this->command_type = 0;
      this->command_value = 0.0f;
    }
  }

  explicit Command_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->actuator_id = 0;
      this->command_type = 0;
      this->command_value = 0.0f;
    }
  }

  // field types and members
  using _actuator_id_type =
    uint8_t;
  _actuator_id_type actuator_id;
  using _command_type_type =
    uint8_t;
  _command_type_type command_type;
  using _command_value_type =
    float;
  _command_value_type command_value;

  // setters for named parameter idiom
  Type & set__actuator_id(
    const uint8_t & _arg)
  {
    this->actuator_id = _arg;
    return *this;
  }
  Type & set__command_type(
    const uint8_t & _arg)
  {
    this->command_type = _arg;
    return *this;
  }
  Type & set__command_value(
    const float & _arg)
  {
    this->command_value = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t COMMAND_TYPE_UNITLESS =
    0u;
  static constexpr uint8_t COMMAND_TYPE_POSITION =
    1u;
  static constexpr uint8_t COMMAND_TYPE_FORCE =
    2u;
  static constexpr uint8_t COMMAND_TYPE_SPEED =
    3u;

  // pointer types
  using RawPtr =
    sam_msgs::msg::Command_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::Command_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::Command_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::Command_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Command_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Command_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Command_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Command_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::Command_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::Command_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__Command
    std::shared_ptr<sam_msgs::msg::Command_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__Command
    std::shared_ptr<sam_msgs::msg::Command_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Command_ & other) const
  {
    if (this->actuator_id != other.actuator_id) {
      return false;
    }
    if (this->command_type != other.command_type) {
      return false;
    }
    if (this->command_value != other.command_value) {
      return false;
    }
    return true;
  }
  bool operator!=(const Command_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Command_

// alias to use template instance with default allocator
using Command =
  sam_msgs::msg::Command_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Command_<ContainerAllocator>::COMMAND_TYPE_UNITLESS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Command_<ContainerAllocator>::COMMAND_TYPE_POSITION;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Command_<ContainerAllocator>::COMMAND_TYPE_FORCE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t Command_<ContainerAllocator>::COMMAND_TYPE_SPEED;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__COMMAND__STRUCT_HPP_
