// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_HPP_

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
# define DEPRECATED__smarc_mission_msgs__msg__GotoWaypoint __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__msg__GotoWaypoint __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct GotoWaypoint_
{
  using Type = GotoWaypoint_<ContainerAllocator>;

  explicit GotoWaypoint_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->goal_tolerance = 0.0;
      this->z_control_mode = 0;
      this->travel_altitude = 0.0;
      this->travel_depth = 0.0;
      this->speed_control_mode = 0;
      this->travel_rpm = 0.0;
      this->travel_speed = 0.0;
      this->lat = 0.0;
      this->lon = 0.0;
      this->arrival_heading = 0.0;
      this->use_heading = false;
      this->name = "";
    }
  }

  explicit GotoWaypoint_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init),
    name(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->goal_tolerance = 0.0;
      this->z_control_mode = 0;
      this->travel_altitude = 0.0;
      this->travel_depth = 0.0;
      this->speed_control_mode = 0;
      this->travel_rpm = 0.0;
      this->travel_speed = 0.0;
      this->lat = 0.0;
      this->lon = 0.0;
      this->arrival_heading = 0.0;
      this->use_heading = false;
      this->name = "";
    }
  }

  // field types and members
  using _pose_type =
    geometry_msgs::msg::PoseStamped_<ContainerAllocator>;
  _pose_type pose;
  using _goal_tolerance_type =
    double;
  _goal_tolerance_type goal_tolerance;
  using _z_control_mode_type =
    uint8_t;
  _z_control_mode_type z_control_mode;
  using _travel_altitude_type =
    double;
  _travel_altitude_type travel_altitude;
  using _travel_depth_type =
    double;
  _travel_depth_type travel_depth;
  using _speed_control_mode_type =
    uint8_t;
  _speed_control_mode_type speed_control_mode;
  using _travel_rpm_type =
    double;
  _travel_rpm_type travel_rpm;
  using _travel_speed_type =
    double;
  _travel_speed_type travel_speed;
  using _lat_type =
    double;
  _lat_type lat;
  using _lon_type =
    double;
  _lon_type lon;
  using _arrival_heading_type =
    double;
  _arrival_heading_type arrival_heading;
  using _use_heading_type =
    bool;
  _use_heading_type use_heading;
  using _name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _name_type name;

  // setters for named parameter idiom
  Type & set__pose(
    const geometry_msgs::msg::PoseStamped_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }
  Type & set__goal_tolerance(
    const double & _arg)
  {
    this->goal_tolerance = _arg;
    return *this;
  }
  Type & set__z_control_mode(
    const uint8_t & _arg)
  {
    this->z_control_mode = _arg;
    return *this;
  }
  Type & set__travel_altitude(
    const double & _arg)
  {
    this->travel_altitude = _arg;
    return *this;
  }
  Type & set__travel_depth(
    const double & _arg)
  {
    this->travel_depth = _arg;
    return *this;
  }
  Type & set__speed_control_mode(
    const uint8_t & _arg)
  {
    this->speed_control_mode = _arg;
    return *this;
  }
  Type & set__travel_rpm(
    const double & _arg)
  {
    this->travel_rpm = _arg;
    return *this;
  }
  Type & set__travel_speed(
    const double & _arg)
  {
    this->travel_speed = _arg;
    return *this;
  }
  Type & set__lat(
    const double & _arg)
  {
    this->lat = _arg;
    return *this;
  }
  Type & set__lon(
    const double & _arg)
  {
    this->lon = _arg;
    return *this;
  }
  Type & set__arrival_heading(
    const double & _arg)
  {
    this->arrival_heading = _arg;
    return *this;
  }
  Type & set__use_heading(
    const bool & _arg)
  {
    this->use_heading = _arg;
    return *this;
  }
  Type & set__name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->name = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t Z_CONTROL_NONE =
    0u;
  static constexpr uint8_t Z_CONTROL_DEPTH =
    1u;
  static constexpr uint8_t Z_CONTROL_ALTITUDE =
    2u;
  static constexpr uint8_t SPEED_CONTROL_NONE =
    0u;
  static constexpr uint8_t SPEED_CONTROL_RPM =
    1u;
  static constexpr uint8_t SPEED_CONTROL_SPEED =
    2u;

  // pointer types
  using RawPtr =
    smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__msg__GotoWaypoint
    std::shared_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__msg__GotoWaypoint
    std::shared_ptr<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GotoWaypoint_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    if (this->goal_tolerance != other.goal_tolerance) {
      return false;
    }
    if (this->z_control_mode != other.z_control_mode) {
      return false;
    }
    if (this->travel_altitude != other.travel_altitude) {
      return false;
    }
    if (this->travel_depth != other.travel_depth) {
      return false;
    }
    if (this->speed_control_mode != other.speed_control_mode) {
      return false;
    }
    if (this->travel_rpm != other.travel_rpm) {
      return false;
    }
    if (this->travel_speed != other.travel_speed) {
      return false;
    }
    if (this->lat != other.lat) {
      return false;
    }
    if (this->lon != other.lon) {
      return false;
    }
    if (this->arrival_heading != other.arrival_heading) {
      return false;
    }
    if (this->use_heading != other.use_heading) {
      return false;
    }
    if (this->name != other.name) {
      return false;
    }
    return true;
  }
  bool operator!=(const GotoWaypoint_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GotoWaypoint_

// alias to use template instance with default allocator
using GotoWaypoint =
  smarc_mission_msgs::msg::GotoWaypoint_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::Z_CONTROL_NONE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::Z_CONTROL_DEPTH;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::Z_CONTROL_ALTITUDE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::SPEED_CONTROL_NONE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::SPEED_CONTROL_RPM;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GotoWaypoint_<ContainerAllocator>::SPEED_CONTROL_SPEED;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__STRUCT_HPP_
