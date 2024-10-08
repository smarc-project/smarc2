// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_control_msgs:msg/ControlError.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_control_msgs__msg__ControlError __attribute__((deprecated))
#else
# define DEPRECATED__smarc_control_msgs__msg__ControlError __declspec(deprecated)
#endif

namespace smarc_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ControlError_
{
  using Type = ControlError_<ContainerAllocator>;

  explicit ControlError_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->roll = 0.0;
      this->pitch = 0.0;
      this->yaw = 0.0;
      this->heading = 0.0;
      this->distance = 0.0;
    }
  }

  explicit ControlError_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->roll = 0.0;
      this->pitch = 0.0;
      this->yaw = 0.0;
      this->heading = 0.0;
      this->distance = 0.0;
    }
  }

  // field types and members
  using _x_type =
    double;
  _x_type x;
  using _y_type =
    double;
  _y_type y;
  using _z_type =
    double;
  _z_type z;
  using _roll_type =
    double;
  _roll_type roll;
  using _pitch_type =
    double;
  _pitch_type pitch;
  using _yaw_type =
    double;
  _yaw_type yaw;
  using _heading_type =
    double;
  _heading_type heading;
  using _distance_type =
    double;
  _distance_type distance;

  // setters for named parameter idiom
  Type & set__x(
    const double & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const double & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__z(
    const double & _arg)
  {
    this->z = _arg;
    return *this;
  }
  Type & set__roll(
    const double & _arg)
  {
    this->roll = _arg;
    return *this;
  }
  Type & set__pitch(
    const double & _arg)
  {
    this->pitch = _arg;
    return *this;
  }
  Type & set__yaw(
    const double & _arg)
  {
    this->yaw = _arg;
    return *this;
  }
  Type & set__heading(
    const double & _arg)
  {
    this->heading = _arg;
    return *this;
  }
  Type & set__distance(
    const double & _arg)
  {
    this->distance = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_control_msgs::msg::ControlError_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_control_msgs::msg::ControlError_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlError_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::ControlError_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_control_msgs__msg__ControlError
    std::shared_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_control_msgs__msg__ControlError
    std::shared_ptr<smarc_control_msgs::msg::ControlError_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ControlError_ & other) const
  {
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->z != other.z) {
      return false;
    }
    if (this->roll != other.roll) {
      return false;
    }
    if (this->pitch != other.pitch) {
      return false;
    }
    if (this->yaw != other.yaw) {
      return false;
    }
    if (this->heading != other.heading) {
      return false;
    }
    if (this->distance != other.distance) {
      return false;
    }
    return true;
  }
  bool operator!=(const ControlError_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ControlError_

// alias to use template instance with default allocator
using ControlError =
  smarc_control_msgs::msg::ControlError_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__CONTROL_ERROR__STRUCT_HPP_
