// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/ArrayCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'commands'
#include "sam_msgs/msg/detail/command__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__ArrayCommand __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__ArrayCommand __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ArrayCommand_
{
  using Type = ArrayCommand_<ContainerAllocator>;

  explicit ArrayCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit ArrayCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _commands_type =
    std::vector<sam_msgs::msg::Command_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<sam_msgs::msg::Command_<ContainerAllocator>>>;
  _commands_type commands;

  // setters for named parameter idiom
  Type & set__commands(
    const std::vector<sam_msgs::msg::Command_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<sam_msgs::msg::Command_<ContainerAllocator>>> & _arg)
  {
    this->commands = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::ArrayCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::ArrayCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ArrayCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ArrayCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__ArrayCommand
    std::shared_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__ArrayCommand
    std::shared_ptr<sam_msgs::msg::ArrayCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ArrayCommand_ & other) const
  {
    if (this->commands != other.commands) {
      return false;
    }
    return true;
  }
  bool operator!=(const ArrayCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ArrayCommand_

// alias to use template instance with default allocator
using ArrayCommand =
  sam_msgs::msg::ArrayCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__STRUCT_HPP_
