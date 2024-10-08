// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/ThrusterAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__STRUCT_HPP_

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

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__ThrusterAngles __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__ThrusterAngles __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ThrusterAngles_
{
  using Type = ThrusterAngles_<ContainerAllocator>;

  explicit ThrusterAngles_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->thruster_vertical_radians = 0.0f;
      this->thruster_horizontal_radians = 0.0f;
    }
  }

  explicit ThrusterAngles_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->thruster_vertical_radians = 0.0f;
      this->thruster_horizontal_radians = 0.0f;
    }
  }

  // field types and members
  using _thruster_vertical_radians_type =
    float;
  _thruster_vertical_radians_type thruster_vertical_radians;
  using _thruster_horizontal_radians_type =
    float;
  _thruster_horizontal_radians_type thruster_horizontal_radians;
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;

  // setters for named parameter idiom
  Type & set__thruster_vertical_radians(
    const float & _arg)
  {
    this->thruster_vertical_radians = _arg;
    return *this;
  }
  Type & set__thruster_horizontal_radians(
    const float & _arg)
  {
    this->thruster_horizontal_radians = _arg;
    return *this;
  }
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::ThrusterAngles_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::ThrusterAngles_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ThrusterAngles_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ThrusterAngles_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__ThrusterAngles
    std::shared_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__ThrusterAngles
    std::shared_ptr<sam_msgs::msg::ThrusterAngles_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ThrusterAngles_ & other) const
  {
    if (this->thruster_vertical_radians != other.thruster_vertical_radians) {
      return false;
    }
    if (this->thruster_horizontal_radians != other.thruster_horizontal_radians) {
      return false;
    }
    if (this->header != other.header) {
      return false;
    }
    return true;
  }
  bool operator!=(const ThrusterAngles_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ThrusterAngles_

// alias to use template instance with default allocator
using ThrusterAngles =
  sam_msgs::msg::ThrusterAngles_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__THRUSTER_ANGLES__STRUCT_HPP_
