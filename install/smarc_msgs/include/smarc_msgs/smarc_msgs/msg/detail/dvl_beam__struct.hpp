// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/DVLBeam.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__DVLBeam __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__DVLBeam __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DVLBeam_
{
  using Type = DVLBeam_<ContainerAllocator>;

  explicit DVLBeam_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->range = 0.0;
      this->range_covariance = 0.0;
      this->velocity = 0.0;
      this->velocity_covariance = 0.0;
    }
  }

  explicit DVLBeam_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->range = 0.0;
      this->range_covariance = 0.0;
      this->velocity = 0.0;
      this->velocity_covariance = 0.0;
    }
  }

  // field types and members
  using _range_type =
    double;
  _range_type range;
  using _range_covariance_type =
    double;
  _range_covariance_type range_covariance;
  using _velocity_type =
    double;
  _velocity_type velocity;
  using _velocity_covariance_type =
    double;
  _velocity_covariance_type velocity_covariance;
  using _pose_type =
    geometry_msgs::msg::PoseStamped_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__range(
    const double & _arg)
  {
    this->range = _arg;
    return *this;
  }
  Type & set__range_covariance(
    const double & _arg)
  {
    this->range_covariance = _arg;
    return *this;
  }
  Type & set__velocity(
    const double & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__velocity_covariance(
    const double & _arg)
  {
    this->velocity_covariance = _arg;
    return *this;
  }
  Type & set__pose(
    const geometry_msgs::msg::PoseStamped_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::DVLBeam_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::DVLBeam_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DVLBeam_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DVLBeam_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__DVLBeam
    std::shared_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__DVLBeam
    std::shared_ptr<smarc_msgs::msg::DVLBeam_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DVLBeam_ & other) const
  {
    if (this->range != other.range) {
      return false;
    }
    if (this->range_covariance != other.range_covariance) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->velocity_covariance != other.velocity_covariance) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const DVLBeam_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DVLBeam_

// alias to use template instance with default allocator
using DVLBeam =
  smarc_msgs::msg::DVLBeam_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_HPP_
