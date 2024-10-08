// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/DVL.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DVL__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__DVL__STRUCT_HPP_

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
// Member 'velocity'
#include "geometry_msgs/msg/detail/vector3__struct.hpp"
// Member 'beams'
#include "smarc_msgs/msg/detail/dvl_beam__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__DVL __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__DVL __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DVL_
{
  using Type = DVL_<ContainerAllocator>;

  explicit DVL_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    velocity(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 9>::iterator, double>(this->velocity_covariance.begin(), this->velocity_covariance.end(), 0.0);
      this->altitude = 0.0;
    }
  }

  explicit DVL_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    velocity(_alloc, _init),
    velocity_covariance(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 9>::iterator, double>(this->velocity_covariance.begin(), this->velocity_covariance.end(), 0.0);
      this->altitude = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _velocity_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _velocity_type velocity;
  using _velocity_covariance_type =
    std::array<double, 9>;
  _velocity_covariance_type velocity_covariance;
  using _altitude_type =
    double;
  _altitude_type altitude;
  using _beams_type =
    std::vector<smarc_msgs::msg::DVLBeam_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::DVLBeam_<ContainerAllocator>>>;
  _beams_type beams;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__velocity(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__velocity_covariance(
    const std::array<double, 9> & _arg)
  {
    this->velocity_covariance = _arg;
    return *this;
  }
  Type & set__altitude(
    const double & _arg)
  {
    this->altitude = _arg;
    return *this;
  }
  Type & set__beams(
    const std::vector<smarc_msgs::msg::DVLBeam_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::DVLBeam_<ContainerAllocator>>> & _arg)
  {
    this->beams = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::DVL_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::DVL_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::DVL_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::DVL_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DVL_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DVL_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::DVL_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::DVL_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::DVL_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::DVL_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__DVL
    std::shared_ptr<smarc_msgs::msg::DVL_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__DVL
    std::shared_ptr<smarc_msgs::msg::DVL_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DVL_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->velocity_covariance != other.velocity_covariance) {
      return false;
    }
    if (this->altitude != other.altitude) {
      return false;
    }
    if (this->beams != other.beams) {
      return false;
    }
    return true;
  }
  bool operator!=(const DVL_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DVL_

// alias to use template instance with default allocator
using DVL =
  smarc_msgs::msg::DVL_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__DVL__STRUCT_HPP_
