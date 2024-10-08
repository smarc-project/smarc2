// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/ThrusterFeedback.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_HPP_

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
// Member 'rpm'
#include "smarc_msgs/msg/detail/thruster_rpm__struct.hpp"
// Member 'dc'
#include "smarc_msgs/msg/detail/thruster_dc__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__ThrusterFeedback __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__ThrusterFeedback __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ThrusterFeedback_
{
  using Type = ThrusterFeedback_<ContainerAllocator>;

  explicit ThrusterFeedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    rpm(_init),
    dc(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current = 0.0f;
      this->torque = 0.0f;
    }
  }

  explicit ThrusterFeedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    rpm(_alloc, _init),
    dc(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current = 0.0f;
      this->torque = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _rpm_type =
    smarc_msgs::msg::ThrusterRPM_<ContainerAllocator>;
  _rpm_type rpm;
  using _dc_type =
    smarc_msgs::msg::ThrusterDC_<ContainerAllocator>;
  _dc_type dc;
  using _current_type =
    float;
  _current_type current;
  using _torque_type =
    float;
  _torque_type torque;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__rpm(
    const smarc_msgs::msg::ThrusterRPM_<ContainerAllocator> & _arg)
  {
    this->rpm = _arg;
    return *this;
  }
  Type & set__dc(
    const smarc_msgs::msg::ThrusterDC_<ContainerAllocator> & _arg)
  {
    this->dc = _arg;
    return *this;
  }
  Type & set__current(
    const float & _arg)
  {
    this->current = _arg;
    return *this;
  }
  Type & set__torque(
    const float & _arg)
  {
    this->torque = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__ThrusterFeedback
    std::shared_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__ThrusterFeedback
    std::shared_ptr<smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ThrusterFeedback_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->rpm != other.rpm) {
      return false;
    }
    if (this->dc != other.dc) {
      return false;
    }
    if (this->current != other.current) {
      return false;
    }
    if (this->torque != other.torque) {
      return false;
    }
    return true;
  }
  bool operator!=(const ThrusterFeedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ThrusterFeedback_

// alias to use template instance with default allocator
using ThrusterFeedback =
  smarc_msgs::msg::ThrusterFeedback_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__THRUSTER_FEEDBACK__STRUCT_HPP_
