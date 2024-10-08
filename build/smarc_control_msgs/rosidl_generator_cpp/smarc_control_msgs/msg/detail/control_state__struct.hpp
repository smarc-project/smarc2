// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_control_msgs:msg/ControlState.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
// Member 'vel'
#include "smarc_control_msgs/msg/detail/state__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_control_msgs__msg__ControlState __attribute__((deprecated))
#else
# define DEPRECATED__smarc_control_msgs__msg__ControlState __declspec(deprecated)
#endif

namespace smarc_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ControlState_
{
  using Type = ControlState_<ContainerAllocator>;

  explicit ControlState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init),
    vel(_init)
  {
    (void)_init;
  }

  explicit ControlState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init),
    vel(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _pose_type =
    smarc_control_msgs::msg::State_<ContainerAllocator>;
  _pose_type pose;
  using _vel_type =
    smarc_control_msgs::msg::State_<ContainerAllocator>;
  _vel_type vel;

  // setters for named parameter idiom
  Type & set__pose(
    const smarc_control_msgs::msg::State_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
  Type & set__vel(
    const smarc_control_msgs::msg::State_<ContainerAllocator> & _arg)
  {
    this->vel = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_control_msgs::msg::ControlState_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_control_msgs::msg::ControlState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_control_msgs__msg__ControlState
    std::shared_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_control_msgs__msg__ControlState
    std::shared_ptr<smarc_control_msgs::msg::ControlState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ControlState_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    if (this->vel != other.vel) {
      return false;
    }
    return true;
  }
  bool operator!=(const ControlState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ControlState_

// alias to use template instance with default allocator
using ControlState =
  smarc_control_msgs::msg::ControlState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_STATE__STRUCT_HPP_
