// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_control_msgs:msg/ControlInput.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__STRUCT_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_control_msgs__msg__ControlInput __attribute__((deprecated))
#else
# define DEPRECATED__smarc_control_msgs__msg__ControlInput __declspec(deprecated)
#endif

namespace smarc_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ControlInput_
{
  using Type = ControlInput_<ContainerAllocator>;

  explicit ControlInput_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->thrusterrpm = 0.0;
      this->thrustervertical = 0.0;
      this->thrusterhorizontal = 0.0;
      this->vbs = 0.0;
      this->lcg = 0.0;
    }
  }

  explicit ControlInput_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->thrusterrpm = 0.0;
      this->thrustervertical = 0.0;
      this->thrusterhorizontal = 0.0;
      this->vbs = 0.0;
      this->lcg = 0.0;
    }
  }

  // field types and members
  using _thrusterrpm_type =
    double;
  _thrusterrpm_type thrusterrpm;
  using _thrustervertical_type =
    double;
  _thrustervertical_type thrustervertical;
  using _thrusterhorizontal_type =
    double;
  _thrusterhorizontal_type thrusterhorizontal;
  using _vbs_type =
    double;
  _vbs_type vbs;
  using _lcg_type =
    double;
  _lcg_type lcg;

  // setters for named parameter idiom
  Type & set__thrusterrpm(
    const double & _arg)
  {
    this->thrusterrpm = _arg;
    return *this;
  }
  Type & set__thrustervertical(
    const double & _arg)
  {
    this->thrustervertical = _arg;
    return *this;
  }
  Type & set__thrusterhorizontal(
    const double & _arg)
  {
    this->thrusterhorizontal = _arg;
    return *this;
  }
  Type & set__vbs(
    const double & _arg)
  {
    this->vbs = _arg;
    return *this;
  }
  Type & set__lcg(
    const double & _arg)
  {
    this->lcg = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_control_msgs::msg::ControlInput_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_control_msgs::msg::ControlInput_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlInput_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlInput_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_control_msgs__msg__ControlInput
    std::shared_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_control_msgs__msg__ControlInput
    std::shared_ptr<smarc_control_msgs::msg::ControlInput_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ControlInput_ & other) const
  {
    if (this->thrusterrpm != other.thrusterrpm) {
      return false;
    }
    if (this->thrustervertical != other.thrustervertical) {
      return false;
    }
    if (this->thrusterhorizontal != other.thrusterhorizontal) {
      return false;
    }
    if (this->vbs != other.vbs) {
      return false;
    }
    if (this->lcg != other.lcg) {
      return false;
    }
    return true;
  }
  bool operator!=(const ControlInput_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ControlInput_

// alias to use template instance with default allocator
using ControlInput =
  smarc_control_msgs::msg::ControlInput_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_INPUT__STRUCT_HPP_
