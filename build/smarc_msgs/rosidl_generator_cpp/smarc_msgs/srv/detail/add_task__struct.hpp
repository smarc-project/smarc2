// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:srv/AddTask.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASK__STRUCT_HPP_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'task'
#include "smarc_msgs/msg/detail/sm_task__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__AddTask_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__AddTask_Request __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddTask_Request_
{
  using Type = AddTask_Request_<ContainerAllocator>;

  explicit AddTask_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : task(_init)
  {
    (void)_init;
  }

  explicit AddTask_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : task(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _task_type =
    smarc_msgs::msg::SMTask_<ContainerAllocator>;
  _task_type task;

  // setters for named parameter idiom
  Type & set__task(
    const smarc_msgs::msg::SMTask_<ContainerAllocator> & _arg)
  {
    this->task = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::AddTask_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::AddTask_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTask_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTask_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__AddTask_Request
    std::shared_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__AddTask_Request
    std::shared_ptr<smarc_msgs::srv::AddTask_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddTask_Request_ & other) const
  {
    if (this->task != other.task) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddTask_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddTask_Request_

// alias to use template instance with default allocator
using AddTask_Request =
  smarc_msgs::srv::AddTask_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__AddTask_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__AddTask_Response __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddTask_Response_
{
  using Type = AddTask_Response_<ContainerAllocator>;

  explicit AddTask_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = 0ull;
    }
  }

  explicit AddTask_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = 0ull;
    }
  }

  // field types and members
  using _task_id_type =
    uint64_t;
  _task_id_type task_id;

  // setters for named parameter idiom
  Type & set__task_id(
    const uint64_t & _arg)
  {
    this->task_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::AddTask_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::AddTask_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTask_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTask_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__AddTask_Response
    std::shared_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__AddTask_Response
    std::shared_ptr<smarc_msgs::srv::AddTask_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddTask_Response_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddTask_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddTask_Response_

// alias to use template instance with default allocator
using AddTask_Response =
  smarc_msgs::srv::AddTask_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs

namespace smarc_msgs
{

namespace srv
{

struct AddTask
{
  using Request = smarc_msgs::srv::AddTask_Request;
  using Response = smarc_msgs::srv::AddTask_Response;
};

}  // namespace srv

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASK__STRUCT_HPP_
