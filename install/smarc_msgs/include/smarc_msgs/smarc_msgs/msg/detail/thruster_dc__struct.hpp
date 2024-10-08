// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/ThrusterDC.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__ThrusterDC __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__ThrusterDC __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ThrusterDC_
{
  using Type = ThrusterDC_<ContainerAllocator>;

  explicit ThrusterDC_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->dc = 0.0f;
    }
  }

  explicit ThrusterDC_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->dc = 0.0f;
    }
  }

  // field types and members
  using _dc_type =
    float;
  _dc_type dc;

  // setters for named parameter idiom
  Type & set__dc(
    const float & _arg)
  {
    this->dc = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::ThrusterDC_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::ThrusterDC_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterDC_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterDC_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__ThrusterDC
    std::shared_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__ThrusterDC
    std::shared_ptr<smarc_msgs::msg::ThrusterDC_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ThrusterDC_ & other) const
  {
    if (this->dc != other.dc) {
      return false;
    }
    return true;
  }
  bool operator!=(const ThrusterDC_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ThrusterDC_

// alias to use template instance with default allocator
using ThrusterDC =
  smarc_msgs::msg::ThrusterDC_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_DC__STRUCT_HPP_
