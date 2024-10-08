// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__UavcanNodeStatus __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__UavcanNodeStatus __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct UavcanNodeStatus_
{
  using Type = UavcanNodeStatus_<ContainerAllocator>;

  explicit UavcanNodeStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->uptime_sec = 0ul;
      this->health = 0;
      this->mode = 0;
      this->sub_mode = 0;
      this->vendor_specific_status_code = 0;
    }
  }

  explicit UavcanNodeStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->uptime_sec = 0ul;
      this->health = 0;
      this->mode = 0;
      this->sub_mode = 0;
      this->vendor_specific_status_code = 0;
    }
  }

  // field types and members
  using _uptime_sec_type =
    uint32_t;
  _uptime_sec_type uptime_sec;
  using _health_type =
    uint8_t;
  _health_type health;
  using _mode_type =
    uint8_t;
  _mode_type mode;
  using _sub_mode_type =
    uint8_t;
  _sub_mode_type sub_mode;
  using _vendor_specific_status_code_type =
    uint16_t;
  _vendor_specific_status_code_type vendor_specific_status_code;

  // setters for named parameter idiom
  Type & set__uptime_sec(
    const uint32_t & _arg)
  {
    this->uptime_sec = _arg;
    return *this;
  }
  Type & set__health(
    const uint8_t & _arg)
  {
    this->health = _arg;
    return *this;
  }
  Type & set__mode(
    const uint8_t & _arg)
  {
    this->mode = _arg;
    return *this;
  }
  Type & set__sub_mode(
    const uint8_t & _arg)
  {
    this->sub_mode = _arg;
    return *this;
  }
  Type & set__vendor_specific_status_code(
    const uint16_t & _arg)
  {
    this->vendor_specific_status_code = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint16_t MAX_BROADCASTING_PERIOD_MS =
    1000u;
  static constexpr uint16_t MIN_BROADCASTING_PERIOD_MS =
    2u;
  static constexpr uint16_t OFFLINE_TIMEOUT_MS =
    3000u;
  static constexpr uint8_t HEALTH_OK =
    0u;
  static constexpr uint8_t HEALTH_WARNING =
    1u;
  static constexpr uint8_t HEALTH_ERROR =
    2u;
  static constexpr uint8_t HEALTH_CRITICAL =
    3u;
  static constexpr uint8_t MODE_OPERATIONAL =
    0u;
  static constexpr uint8_t MODE_INITIALIZATION =
    1u;
  static constexpr uint8_t MODE_MAINTENANCE =
    2u;
  static constexpr uint8_t MODE_SOFTWARE_UPDATE =
    3u;
  static constexpr uint8_t MODE_OFFLINE =
    7u;

  // pointer types
  using RawPtr =
    sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__UavcanNodeStatus
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__UavcanNodeStatus
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UavcanNodeStatus_ & other) const
  {
    if (this->uptime_sec != other.uptime_sec) {
      return false;
    }
    if (this->health != other.health) {
      return false;
    }
    if (this->mode != other.mode) {
      return false;
    }
    if (this->sub_mode != other.sub_mode) {
      return false;
    }
    if (this->vendor_specific_status_code != other.vendor_specific_status_code) {
      return false;
    }
    return true;
  }
  bool operator!=(const UavcanNodeStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UavcanNodeStatus_

// alias to use template instance with default allocator
using UavcanNodeStatus =
  sam_msgs::msg::UavcanNodeStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint16_t UavcanNodeStatus_<ContainerAllocator>::MAX_BROADCASTING_PERIOD_MS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint16_t UavcanNodeStatus_<ContainerAllocator>::MIN_BROADCASTING_PERIOD_MS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint16_t UavcanNodeStatus_<ContainerAllocator>::OFFLINE_TIMEOUT_MS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::HEALTH_OK;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::HEALTH_WARNING;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::HEALTH_ERROR;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::HEALTH_CRITICAL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::MODE_OPERATIONAL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::MODE_INITIALIZATION;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::MODE_MAINTENANCE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::MODE_SOFTWARE_UPDATE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanNodeStatus_<ContainerAllocator>::MODE_OFFLINE;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__STRUCT_HPP_
