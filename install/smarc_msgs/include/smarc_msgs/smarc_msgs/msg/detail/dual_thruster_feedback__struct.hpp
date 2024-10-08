// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/DualThrusterFeedback.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'thruster_front'
// Member 'thruster_back'
#include "smarc_msgs/msg/detail/thruster_feedback__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__DualThrusterFeedback __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__DualThrusterFeedback __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DualThrusterFeedback_
{
  using Type = DualThrusterFeedback_<ContainerAllocator>;

  explicit DualThrusterFeedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : thruster_front(_init),
    thruster_back(_init)
  {
    (void)_init;
  }

  explicit DualThrusterFeedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : thruster_front(_alloc, _init),
    thruster_back(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _thruster_front_type =
    smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>;
  _thruster_front_type thruster_front;
  using _thruster_back_type =
    smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator>;
  _thruster_back_type thruster_back;

  // setters for named parameter idiom
  Type & set__thruster_front(
    const smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> & _arg)
  {
    this->thruster_front = _arg;
    return *this;
  }
  Type & set__thruster_back(
    const smarc_msgs::msg::ThrusterFeedback_<ContainerAllocator> & _arg)
  {
    this->thruster_back = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__DualThrusterFeedback
    std::shared_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__DualThrusterFeedback
    std::shared_ptr<smarc_msgs::msg::DualThrusterFeedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DualThrusterFeedback_ & other) const
  {
    if (this->thruster_front != other.thruster_front) {
      return false;
    }
    if (this->thruster_back != other.thruster_back) {
      return false;
    }
    return true;
  }
  bool operator!=(const DualThrusterFeedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DualThrusterFeedback_

// alias to use template instance with default allocator
using DualThrusterFeedback =
  smarc_msgs::msg::DualThrusterFeedback_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DUAL_THRUSTER_FEEDBACK__STRUCT_HPP_
