// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/SMTask.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'max_duration'
#include "builtin_interfaces/msg/detail/duration__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__SMTask __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__SMTask __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SMTask_
{
  using Type = SMTask_<ContainerAllocator>;

  explicit SMTask_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : max_duration(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = 0ull;
      this->x = 0.0;
      this->y = 0.0;
      this->depth = 0.0;
      this->altitude = 0.0;
      this->theta = 0.0;
      this->action_topic = "";
      this->action_arguments = "";
    }
  }

  explicit SMTask_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : max_duration(_alloc, _init),
    action_topic(_alloc),
    action_arguments(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = 0ull;
      this->x = 0.0;
      this->y = 0.0;
      this->depth = 0.0;
      this->altitude = 0.0;
      this->theta = 0.0;
      this->action_topic = "";
      this->action_arguments = "";
    }
  }

  // field types and members
  using _task_id_type =
    uint64_t;
  _task_id_type task_id;
  using _x_type =
    double;
  _x_type x;
  using _y_type =
    double;
  _y_type y;
  using _depth_type =
    double;
  _depth_type depth;
  using _altitude_type =
    double;
  _altitude_type altitude;
  using _theta_type =
    double;
  _theta_type theta;
  using _max_duration_type =
    builtin_interfaces::msg::Duration_<ContainerAllocator>;
  _max_duration_type max_duration;
  using _action_topic_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _action_topic_type action_topic;
  using _action_arguments_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _action_arguments_type action_arguments;

  // setters for named parameter idiom
  Type & set__task_id(
    const uint64_t & _arg)
  {
    this->task_id = _arg;
    return *this;
  }
  Type & set__x(
    const double & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const double & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__depth(
    const double & _arg)
  {
    this->depth = _arg;
    return *this;
  }
  Type & set__altitude(
    const double & _arg)
  {
    this->altitude = _arg;
    return *this;
  }
  Type & set__theta(
    const double & _arg)
  {
    this->theta = _arg;
    return *this;
  }
  Type & set__max_duration(
    const builtin_interfaces::msg::Duration_<ContainerAllocator> & _arg)
  {
    this->max_duration = _arg;
    return *this;
  }
  Type & set__action_topic(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->action_topic = _arg;
    return *this;
  }
  Type & set__action_arguments(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->action_arguments = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::SMTask_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::SMTask_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::SMTask_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::SMTask_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__SMTask
    std::shared_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__SMTask
    std::shared_ptr<smarc_msgs::msg::SMTask_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SMTask_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->depth != other.depth) {
      return false;
    }
    if (this->altitude != other.altitude) {
      return false;
    }
    if (this->theta != other.theta) {
      return false;
    }
    if (this->max_duration != other.max_duration) {
      return false;
    }
    if (this->action_topic != other.action_topic) {
      return false;
    }
    if (this->action_arguments != other.action_arguments) {
      return false;
    }
    return true;
  }
  bool operator!=(const SMTask_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SMTask_

// alias to use template instance with default allocator
using SMTask =
  smarc_msgs::msg::SMTask_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__SM_TASK__STRUCT_HPP_
