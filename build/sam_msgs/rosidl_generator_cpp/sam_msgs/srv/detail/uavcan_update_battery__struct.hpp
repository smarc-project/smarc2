// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_HPP_
#define SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Request __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Request __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct UavcanUpdateBattery_Request_
{
  using Type = UavcanUpdateBattery_Request_<ContainerAllocator>;

  explicit UavcanUpdateBattery_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->node_id = 0;
      this->command = 0;
      this->charge = 0.0f;
    }
  }

  explicit UavcanUpdateBattery_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->node_id = 0;
      this->command = 0;
      this->charge = 0.0f;
    }
  }

  // field types and members
  using _node_id_type =
    uint8_t;
  _node_id_type node_id;
  using _command_type =
    uint8_t;
  _command_type command;
  using _charge_type =
    float;
  _charge_type charge;

  // setters for named parameter idiom
  Type & set__node_id(
    const uint8_t & _arg)
  {
    this->node_id = _arg;
    return *this;
  }
  Type & set__command(
    const uint8_t & _arg)
  {
    this->command = _arg;
    return *this;
  }
  Type & set__charge(
    const float & _arg)
  {
    this->charge = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t IS_FULL =
    1u;
  static constexpr uint8_t WAS_FULL =
    2u;
  static constexpr uint8_t ADD_CHARGE =
    3u;
  static constexpr uint8_t ON_MAINS =
    4u;

  // pointer types
  using RawPtr =
    sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Request
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Request
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UavcanUpdateBattery_Request_ & other) const
  {
    if (this->node_id != other.node_id) {
      return false;
    }
    if (this->command != other.command) {
      return false;
    }
    if (this->charge != other.charge) {
      return false;
    }
    return true;
  }
  bool operator!=(const UavcanUpdateBattery_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UavcanUpdateBattery_Request_

// alias to use template instance with default allocator
using UavcanUpdateBattery_Request =
  sam_msgs::srv::UavcanUpdateBattery_Request_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Request_<ContainerAllocator>::IS_FULL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Request_<ContainerAllocator>::WAS_FULL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Request_<ContainerAllocator>::ADD_CHARGE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Request_<ContainerAllocator>::ON_MAINS;
#endif  // __cplusplus < 201703L

}  // namespace srv

}  // namespace sam_msgs


#ifndef _WIN32
# define DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Response __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Response __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct UavcanUpdateBattery_Response_
{
  using Type = UavcanUpdateBattery_Response_<ContainerAllocator>;

  explicit UavcanUpdateBattery_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = 0;
    }
  }

  explicit UavcanUpdateBattery_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = 0;
    }
  }

  // field types and members
  using _success_type =
    uint8_t;
  _success_type success;

  // setters for named parameter idiom
  Type & set__success(
    const uint8_t & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t UPDATE_SUCCESSFULL =
    1u;
  static constexpr uint8_t UPDATE_FAILED =
    0u;

  // pointer types
  using RawPtr =
    sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Response
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__srv__UavcanUpdateBattery_Response
    std::shared_ptr<sam_msgs::srv::UavcanUpdateBattery_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UavcanUpdateBattery_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const UavcanUpdateBattery_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UavcanUpdateBattery_Response_

// alias to use template instance with default allocator
using UavcanUpdateBattery_Response =
  sam_msgs::srv::UavcanUpdateBattery_Response_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Response_<ContainerAllocator>::UPDATE_SUCCESSFULL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t UavcanUpdateBattery_Response_<ContainerAllocator>::UPDATE_FAILED;
#endif  // __cplusplus < 201703L

}  // namespace srv

}  // namespace sam_msgs

namespace sam_msgs
{

namespace srv
{

struct UavcanUpdateBattery
{
  using Request = sam_msgs::srv::UavcanUpdateBattery_Request;
  using Response = sam_msgs::srv::UavcanUpdateBattery_Response;
};

}  // namespace srv

}  // namespace sam_msgs

#endif  // SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__STRUCT_HPP_
