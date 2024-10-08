// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/BallastAngles.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_HPP_

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
# define DEPRECATED__sam_msgs__msg__BallastAngles __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__BallastAngles __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct BallastAngles_
{
  using Type = BallastAngles_<ContainerAllocator>;

  explicit BallastAngles_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->weight_1_offset_radians = 0.0f;
      this->weight_2_offset_radians = 0.0f;
    }
  }

  explicit BallastAngles_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->weight_1_offset_radians = 0.0f;
      this->weight_2_offset_radians = 0.0f;
    }
  }

  // field types and members
  using _weight_1_offset_radians_type =
    float;
  _weight_1_offset_radians_type weight_1_offset_radians;
  using _weight_2_offset_radians_type =
    float;
  _weight_2_offset_radians_type weight_2_offset_radians;
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;

  // setters for named parameter idiom
  Type & set__weight_1_offset_radians(
    const float & _arg)
  {
    this->weight_1_offset_radians = _arg;
    return *this;
  }
  Type & set__weight_2_offset_radians(
    const float & _arg)
  {
    this->weight_2_offset_radians = _arg;
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
    sam_msgs::msg::BallastAngles_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::BallastAngles_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::BallastAngles_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::BallastAngles_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__BallastAngles
    std::shared_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__BallastAngles
    std::shared_ptr<sam_msgs::msg::BallastAngles_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const BallastAngles_ & other) const
  {
    if (this->weight_1_offset_radians != other.weight_1_offset_radians) {
      return false;
    }
    if (this->weight_2_offset_radians != other.weight_2_offset_radians) {
      return false;
    }
    if (this->header != other.header) {
      return false;
    }
    return true;
  }
  bool operator!=(const BallastAngles_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct BallastAngles_

// alias to use template instance with default allocator
using BallastAngles =
  sam_msgs::msg::BallastAngles_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__BALLAST_ANGLES__STRUCT_HPP_
