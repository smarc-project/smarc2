// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_HPP_
#define SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'lat_lon_odom'
#include "smarc_msgs/msg/detail/lat_lon_odometry__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Request __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct LatLonToUTMOdometry_Request_
{
  using Type = LatLonToUTMOdometry_Request_<ContainerAllocator>;

  explicit LatLonToUTMOdometry_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : lat_lon_odom(_init)
  {
    (void)_init;
  }

  explicit LatLonToUTMOdometry_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : lat_lon_odom(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _lat_lon_odom_type =
    smarc_msgs::msg::LatLonOdometry_<ContainerAllocator>;
  _lat_lon_odom_type lat_lon_odom;

  // setters for named parameter idiom
  Type & set__lat_lon_odom(
    const smarc_msgs::msg::LatLonOdometry_<ContainerAllocator> & _arg)
  {
    this->lat_lon_odom = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Request
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Request
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LatLonToUTMOdometry_Request_ & other) const
  {
    if (this->lat_lon_odom != other.lat_lon_odom) {
      return false;
    }
    return true;
  }
  bool operator!=(const LatLonToUTMOdometry_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LatLonToUTMOdometry_Request_

// alias to use template instance with default allocator
using LatLonToUTMOdometry_Request =
  smarc_msgs::srv::LatLonToUTMOdometry_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs


// Include directives for member types
// Member 'odom'
#include "nav_msgs/msg/detail/odometry__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Response __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct LatLonToUTMOdometry_Response_
{
  using Type = LatLonToUTMOdometry_Response_<ContainerAllocator>;

  explicit LatLonToUTMOdometry_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : odom(_init)
  {
    (void)_init;
  }

  explicit LatLonToUTMOdometry_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : odom(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _odom_type =
    nav_msgs::msg::Odometry_<ContainerAllocator>;
  _odom_type odom;

  // setters for named parameter idiom
  Type & set__odom(
    const nav_msgs::msg::Odometry_<ContainerAllocator> & _arg)
  {
    this->odom = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Response
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__LatLonToUTMOdometry_Response
    std::shared_ptr<smarc_msgs::srv::LatLonToUTMOdometry_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LatLonToUTMOdometry_Response_ & other) const
  {
    if (this->odom != other.odom) {
      return false;
    }
    return true;
  }
  bool operator!=(const LatLonToUTMOdometry_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LatLonToUTMOdometry_Response_

// alias to use template instance with default allocator
using LatLonToUTMOdometry_Response =
  smarc_msgs::srv::LatLonToUTMOdometry_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs

namespace smarc_msgs
{

namespace srv
{

struct LatLonToUTMOdometry
{
  using Request = smarc_msgs::srv::LatLonToUTMOdometry_Request;
  using Response = smarc_msgs::srv::LatLonToUTMOdometry_Response;
};

}  // namespace srv

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__LAT_LON_TO_UTM_ODOMETRY__STRUCT_HPP_
