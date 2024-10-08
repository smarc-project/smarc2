// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'waypoints'
#include "geometry_msgs/msg/detail/pose2_d__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Request __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct DubinsPlan_Request_
{
  using Type = DubinsPlan_Request_<ContainerAllocator>;

  explicit DubinsPlan_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->step = 0.0;
      this->turning_radius = 0.0;
    }
  }

  explicit DubinsPlan_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->step = 0.0;
      this->turning_radius = 0.0;
    }
  }

  // field types and members
  using _waypoints_type =
    std::vector<geometry_msgs::msg::Pose2D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose2D_<ContainerAllocator>>>;
  _waypoints_type waypoints;
  using _step_type =
    double;
  _step_type step;
  using _turning_radius_type =
    double;
  _turning_radius_type turning_radius;

  // setters for named parameter idiom
  Type & set__waypoints(
    const std::vector<geometry_msgs::msg::Pose2D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose2D_<ContainerAllocator>>> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }
  Type & set__step(
    const double & _arg)
  {
    this->step = _arg;
    return *this;
  }
  Type & set__turning_radius(
    const double & _arg)
  {
    this->turning_radius = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Request
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Request
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DubinsPlan_Request_ & other) const
  {
    if (this->waypoints != other.waypoints) {
      return false;
    }
    if (this->step != other.step) {
      return false;
    }
    if (this->turning_radius != other.turning_radius) {
      return false;
    }
    return true;
  }
  bool operator!=(const DubinsPlan_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DubinsPlan_Request_

// alias to use template instance with default allocator
using DubinsPlan_Request =
  smarc_mission_msgs::srv::DubinsPlan_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_mission_msgs


// Include directives for member types
// Member 'waypoints'
// already included above
// #include "geometry_msgs/msg/detail/pose2_d__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Response __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct DubinsPlan_Response_
{
  using Type = DubinsPlan_Response_<ContainerAllocator>;

  explicit DubinsPlan_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit DubinsPlan_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _waypoints_type =
    std::vector<geometry_msgs::msg::Pose2D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose2D_<ContainerAllocator>>>;
  _waypoints_type waypoints;
  using _original_wp_indices_type =
    std::vector<uint16_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint16_t>>;
  _original_wp_indices_type original_wp_indices;

  // setters for named parameter idiom
  Type & set__waypoints(
    const std::vector<geometry_msgs::msg::Pose2D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose2D_<ContainerAllocator>>> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }
  Type & set__original_wp_indices(
    const std::vector<uint16_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint16_t>> & _arg)
  {
    this->original_wp_indices = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Response
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__srv__DubinsPlan_Response
    std::shared_ptr<smarc_mission_msgs::srv::DubinsPlan_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DubinsPlan_Response_ & other) const
  {
    if (this->waypoints != other.waypoints) {
      return false;
    }
    if (this->original_wp_indices != other.original_wp_indices) {
      return false;
    }
    return true;
  }
  bool operator!=(const DubinsPlan_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DubinsPlan_Response_

// alias to use template instance with default allocator
using DubinsPlan_Response =
  smarc_mission_msgs::srv::DubinsPlan_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace smarc_mission_msgs
{

namespace srv
{

struct DubinsPlan
{
  using Request = smarc_mission_msgs::srv::DubinsPlan_Request;
  using Response = smarc_mission_msgs::srv::DubinsPlan_Response;
};

}  // namespace srv

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__STRUCT_HPP_
