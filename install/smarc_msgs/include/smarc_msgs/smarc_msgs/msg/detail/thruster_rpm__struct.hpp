// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/ThrusterRPM.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__ThrusterRPM __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__ThrusterRPM __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ThrusterRPM_
{
  using Type = ThrusterRPM_<ContainerAllocator>;

  explicit ThrusterRPM_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rpm = 0l;
    }
  }

  explicit ThrusterRPM_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rpm = 0l;
    }
  }

  // field types and members
  using _rpm_type =
    int32_t;
  _rpm_type rpm;

  // setters for named parameter idiom
  Type & set__rpm(
    const int32_t & _arg)
  {
    this->rpm = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__ThrusterRPM
    std::shared_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__ThrusterRPM
    std::shared_ptr<smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ThrusterRPM_ & other) const
  {
    if (this->rpm != other.rpm) {
      return false;
    }
    return true;
  }
  bool operator!=(const ThrusterRPM_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ThrusterRPM_

// alias to use template instance with default allocator
using ThrusterRPM =
  smarc_msgs::msg::ThrusterRPM_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_RPM__STRUCT_HPP_
