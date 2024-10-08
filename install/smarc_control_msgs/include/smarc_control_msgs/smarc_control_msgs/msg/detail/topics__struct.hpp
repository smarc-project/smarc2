// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_control_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
#define SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_control_msgs__msg__Topics __attribute__((deprecated))
#else
# define DEPRECATED__smarc_control_msgs__msg__Topics __declspec(deprecated)
#endif

namespace smarc_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Topics_
{
  using Type = Topics_<ContainerAllocator>;

  explicit Topics_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit Topics_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> STATES;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DEPTH_SETPOINT;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> PITCH_SETPOINT;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> STATES_CONV;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> REF_CONV;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> CONTROL_ERROR_CONV;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> CONTROL_INPUT_CONV;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> WAYPOINT_CONV;

  // pointer types
  using RawPtr =
    smarc_control_msgs::msg::Topics_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_control_msgs::msg::Topics_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::Topics_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_control_msgs::msg::Topics_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_control_msgs__msg__Topics
    std::shared_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_control_msgs__msg__Topics
    std::shared_ptr<smarc_control_msgs::msg::Topics_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Topics_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const Topics_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Topics_

// alias to use template instance with default allocator
using Topics =
  smarc_control_msgs::msg::Topics_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::STATES = "core/odom_gt";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DEPTH_SETPOINT = "ctrl/depth_setpoint";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::PITCH_SETPOINT = "ctrl/pitch_setpoint";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::STATES_CONV = "ctrl/conv/states";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::REF_CONV = "ctrl/conv/ref";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::CONTROL_ERROR_CONV = "ctrl/conv/error";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::CONTROL_INPUT_CONV = "ctrl/conv/control_input";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::WAYPOINT_CONV = "ctrl/conv/waypoint";

}  // namespace msg

}  // namespace smarc_control_msgs

#endif  // SMARC_CONTROL_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
