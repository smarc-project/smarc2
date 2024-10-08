// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_mission_msgs:msg/BTCommand.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__msg__BTCommand __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__msg__BTCommand __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct BTCommand_
{
  using Type = BTCommand_<ContainerAllocator>;

  explicit BTCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->msg_type = 0;
      this->cmd_json = "";
      this->fb_json = "";
    }
  }

  explicit BTCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : cmd_json(_alloc),
    fb_json(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->msg_type = 0;
      this->cmd_json = "";
      this->fb_json = "";
    }
  }

  // field types and members
  using _msg_type_type =
    uint8_t;
  _msg_type_type msg_type;
  using _cmd_json_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _cmd_json_type cmd_json;
  using _fb_json_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _fb_json_type fb_json;

  // setters for named parameter idiom
  Type & set__msg_type(
    const uint8_t & _arg)
  {
    this->msg_type = _arg;
    return *this;
  }
  Type & set__cmd_json(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->cmd_json = _arg;
    return *this;
  }
  Type & set__fb_json(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->fb_json = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t TYPE_CMD =
    0u;
  static constexpr uint8_t TYPE_FB =
    1u;

  // pointer types
  using RawPtr =
    smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__msg__BTCommand
    std::shared_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__msg__BTCommand
    std::shared_ptr<smarc_mission_msgs::msg::BTCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const BTCommand_ & other) const
  {
    if (this->msg_type != other.msg_type) {
      return false;
    }
    if (this->cmd_json != other.cmd_json) {
      return false;
    }
    if (this->fb_json != other.fb_json) {
      return false;
    }
    return true;
  }
  bool operator!=(const BTCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct BTCommand_

// alias to use template instance with default allocator
using BTCommand =
  smarc_mission_msgs::msg::BTCommand_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t BTCommand_<ContainerAllocator>::TYPE_CMD;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t BTCommand_<ContainerAllocator>::TYPE_FB;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__STRUCT_HPP_
