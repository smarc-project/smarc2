// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/ControllerStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__ControllerStatus __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__ControllerStatus __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ControllerStatus_
{
  using Type = ControllerStatus_<ContainerAllocator>;

  explicit ControllerStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_status = 0;
      this->service_name = "";
      this->diagnostics_message = "";
    }
  }

  explicit ControllerStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : service_name(_alloc),
    diagnostics_message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_status = 0;
      this->service_name = "";
      this->diagnostics_message = "";
    }
  }

  // field types and members
  using _control_status_type =
    uint8_t;
  _control_status_type control_status;
  using _service_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _service_name_type service_name;
  using _diagnostics_message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _diagnostics_message_type diagnostics_message;

  // setters for named parameter idiom
  Type & set__control_status(
    const uint8_t & _arg)
  {
    this->control_status = _arg;
    return *this;
  }
  Type & set__service_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->service_name = _arg;
    return *this;
  }
  Type & set__diagnostics_message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->diagnostics_message = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t CONTROL_STATUS_NOT_CONTROLLING =
    0u;
  static constexpr uint8_t CONTROL_STATUS_CONTROLLING =
    1u;
  static constexpr uint8_t CONTROL_STATUS_ERROR =
    2u;

  // pointer types
  using RawPtr =
    smarc_msgs::msg::ControllerStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::ControllerStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ControllerStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ControllerStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__ControllerStatus
    std::shared_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__ControllerStatus
    std::shared_ptr<smarc_msgs::msg::ControllerStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ControllerStatus_ & other) const
  {
    if (this->control_status != other.control_status) {
      return false;
    }
    if (this->service_name != other.service_name) {
      return false;
    }
    if (this->diagnostics_message != other.diagnostics_message) {
      return false;
    }
    return true;
  }
  bool operator!=(const ControllerStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ControllerStatus_

// alias to use template instance with default allocator
using ControllerStatus =
  smarc_msgs::msg::ControllerStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ControllerStatus_<ContainerAllocator>::CONTROL_STATUS_NOT_CONTROLLING;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ControllerStatus_<ContainerAllocator>::CONTROL_STATUS_CONTROLLING;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t ControllerStatus_<ContainerAllocator>::CONTROL_STATUS_ERROR;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__CONTROLLER_STATUS__STRUCT_HPP_
