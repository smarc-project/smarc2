// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/ExecutionStatus.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_HPP_

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
// Member 'execution_queue'
#include "smarc_msgs/msg/detail/sm_task__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__msg__ExecutionStatus __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__ExecutionStatus __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ExecutionStatus_
{
  using Type = ExecutionStatus_<ContainerAllocator>;

  explicit ExecutionStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->currently_executing = false;
    }
  }

  explicit ExecutionStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->currently_executing = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _currently_executing_type =
    bool;
  _currently_executing_type currently_executing;
  using _execution_queue_type =
    std::vector<smarc_msgs::msg::SMTask_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::SMTask_<ContainerAllocator>>>;
  _execution_queue_type execution_queue;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__currently_executing(
    const bool & _arg)
  {
    this->currently_executing = _arg;
    return *this;
  }
  Type & set__execution_queue(
    const std::vector<smarc_msgs::msg::SMTask_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::SMTask_<ContainerAllocator>>> & _arg)
  {
    this->execution_queue = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__ExecutionStatus
    std::shared_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__ExecutionStatus
    std::shared_ptr<smarc_msgs::msg::ExecutionStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecutionStatus_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->currently_executing != other.currently_executing) {
      return false;
    }
    if (this->execution_queue != other.execution_queue) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecutionStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecutionStatus_

// alias to use template instance with default allocator
using ExecutionStatus =
  smarc_msgs::msg::ExecutionStatus_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__EXECUTION_STATUS__STRUCT_HPP_
