// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/LightCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'command'
#include "std_msgs/msg/detail/color_rgba__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__LightCommand __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__LightCommand __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct LightCommand_
{
  using Type = LightCommand_<ContainerAllocator>;

  explicit LightCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : command(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
    }
  }

  explicit LightCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : command(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
    }
  }

  // field types and members
  using _id_type =
    uint16_t;
  _id_type id;
  using _command_type =
    std_msgs::msg::ColorRGBA_<ContainerAllocator>;
  _command_type command;

  // setters for named parameter idiom
  Type & set__id(
    const uint16_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__command(
    const std_msgs::msg::ColorRGBA_<ContainerAllocator> & _arg)
  {
    this->command = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::LightCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::LightCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::LightCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::LightCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__LightCommand
    std::shared_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__LightCommand
    std::shared_ptr<sam_msgs::msg::LightCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LightCommand_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->command != other.command) {
      return false;
    }
    return true;
  }
  bool operator!=(const LightCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LightCommand_

// alias to use template instance with default allocator
using LightCommand =
  sam_msgs::msg::LightCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__STRUCT_HPP_
