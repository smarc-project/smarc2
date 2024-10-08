// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/LatLonOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_HPP_

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
// Member 'lat_lon_pose'
#include "geographic_msgs/msg/detail/geo_pose__struct.hpp"
// Member 'twist'
#include "geometry_msgs/msg/detail/twist_with_covariance__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__LatLonOdometry __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__LatLonOdometry __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct LatLonOdometry_
{
  using Type = LatLonOdometry_<ContainerAllocator>;

  explicit LatLonOdometry_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    lat_lon_pose(_init),
    twist(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 36>::iterator, double>(this->covariance.begin(), this->covariance.end(), 0.0);
    }
  }

  explicit LatLonOdometry_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    lat_lon_pose(_alloc, _init),
    covariance(_alloc),
    twist(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 36>::iterator, double>(this->covariance.begin(), this->covariance.end(), 0.0);
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _lat_lon_pose_type =
    geographic_msgs::msg::GeoPose_<ContainerAllocator>;
  _lat_lon_pose_type lat_lon_pose;
  using _covariance_type =
    std::array<double, 36>;
  _covariance_type covariance;
  using _twist_type =
    geometry_msgs::msg::TwistWithCovariance_<ContainerAllocator>;
  _twist_type twist;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__lat_lon_pose(
    const geographic_msgs::msg::GeoPose_<ContainerAllocator> & _arg)
  {
    this->lat_lon_pose = _arg;
    return *this;
  }
  Type & set__covariance(
    const std::array<double, 36> & _arg)
  {
    this->covariance = _arg;
    return *this;
  }
  Type & set__twist(
    const geometry_msgs::msg::TwistWithCovariance_<ContainerAllocator> & _arg)
  {
    this->twist = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__LatLonOdometry
    std::shared_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__LatLonOdometry
    std::shared_ptr<smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LatLonOdometry_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->lat_lon_pose != other.lat_lon_pose) {
      return false;
    }
    if (this->covariance != other.covariance) {
      return false;
    }
    if (this->twist != other.twist) {
      return false;
    }
    return true;
  }
  bool operator!=(const LatLonOdometry_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LatLonOdometry_

// alias to use template instance with default allocator
using LatLonOdometry =
  smarc_msgs::msg::LatLonOdometry_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__LAT_LON_ODOMETRY__STRUCT_HPP_
