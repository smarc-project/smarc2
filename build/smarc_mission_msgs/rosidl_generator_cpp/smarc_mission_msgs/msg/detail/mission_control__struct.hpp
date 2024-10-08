// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'waypoints'
#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__msg__MissionControl __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__msg__MissionControl __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MissionControl_
{
  using Type = MissionControl_<ContainerAllocator>;

  explicit MissionControl_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->name = "";
      this->hash = "";
      this->timeout = 0ull;
      this->command = 0;
      this->plan_state = 0;
      this->feedback_str = "";
    }
  }

  explicit MissionControl_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : name(_alloc),
    hash(_alloc),
    feedback_str(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->name = "";
      this->hash = "";
      this->timeout = 0ull;
      this->command = 0;
      this->plan_state = 0;
      this->feedback_str = "";
    }
  }

  // field types and members
  using _name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _name_type name;
  using _hash_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _hash_type hash;
  using _timeout_type =
    uint64_t;
  _timeout_type timeout;
  using _command_type =
    uint8_t;
  _command_type command;
  using _plan_state_type =
    uint8_t;
  _plan_state_type plan_state;
  using _feedback_str_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _feedback_str_type feedback_str;
  using _waypoints_type =
    std::vector<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>>;
  _waypoints_type waypoints;

  // setters for named parameter idiom
  Type & set__name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->name = _arg;
    return *this;
  }
  Type & set__hash(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->hash = _arg;
    return *this;
  }
  Type & set__timeout(
    const uint64_t & _arg)
  {
    this->timeout = _arg;
    return *this;
  }
  Type & set__command(
    const uint8_t & _arg)
  {
    this->command = _arg;
    return *this;
  }
  Type & set__plan_state(
    const uint8_t & _arg)
  {
    this->plan_state = _arg;
    return *this;
  }
  Type & set__feedback_str(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->feedback_str = _arg;
    return *this;
  }
  Type & set__waypoints(
    const std::vector<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_mission_msgs::msg::GotoWaypoint_<ContainerAllocator>>> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t CMD_START =
    0u;
  static constexpr uint8_t CMD_STOP =
    1u;
  static constexpr uint8_t CMD_PAUSE =
    2u;
  static constexpr uint8_t CMD_EMERGENCY =
    3u;
  static constexpr uint8_t CMD_SET_PLAN =
    4u;
  static constexpr uint8_t CMD_IS_FEEDBACK =
    5u;
  static constexpr uint8_t CMD_REQUEST_FEEDBACK =
    6u;
  static constexpr uint8_t FB_RUNNING =
    0u;
  static constexpr uint8_t FB_STOPPED =
    1u;
  static constexpr uint8_t FB_PAUSED =
    2u;
  static constexpr uint8_t FB_EMERGENCY =
    3u;
  static constexpr uint8_t FB_RECEIVED =
    4u;
  static constexpr uint8_t FB_COMPLETED =
    5u;

  // pointer types
  using RawPtr =
    smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__msg__MissionControl
    std::shared_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__msg__MissionControl
    std::shared_ptr<smarc_mission_msgs::msg::MissionControl_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MissionControl_ & other) const
  {
    if (this->name != other.name) {
      return false;
    }
    if (this->hash != other.hash) {
      return false;
    }
    if (this->timeout != other.timeout) {
      return false;
    }
    if (this->command != other.command) {
      return false;
    }
    if (this->plan_state != other.plan_state) {
      return false;
    }
    if (this->feedback_str != other.feedback_str) {
      return false;
    }
    if (this->waypoints != other.waypoints) {
      return false;
    }
    return true;
  }
  bool operator!=(const MissionControl_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MissionControl_

// alias to use template instance with default allocator
using MissionControl =
  smarc_mission_msgs::msg::MissionControl_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_START;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_STOP;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_PAUSE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_EMERGENCY;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_SET_PLAN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_IS_FEEDBACK;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::CMD_REQUEST_FEEDBACK;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_RUNNING;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_STOPPED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_PAUSED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_EMERGENCY;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_RECEIVED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t MissionControl_<ContainerAllocator>::FB_COMPLETED;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__STRUCT_HPP_
