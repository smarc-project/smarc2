// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:srv/AddTasks.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_HPP_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'tasks'
#include "smarc_msgs/msg/detail/sm_task__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__AddTasks_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__AddTasks_Request __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddTasks_Request_
{
  using Type = AddTasks_Request_<ContainerAllocator>;

  explicit AddTasks_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit AddTasks_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _tasks_type =
    std::vector<smarc_msgs::msg::SMTask_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::SMTask_<ContainerAllocator>>>;
  _tasks_type tasks;

  // setters for named parameter idiom
  Type & set__tasks(
    const std::vector<smarc_msgs::msg::SMTask_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<smarc_msgs::msg::SMTask_<ContainerAllocator>>> & _arg)
  {
    this->tasks = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__AddTasks_Request
    std::shared_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__AddTasks_Request
    std::shared_ptr<smarc_msgs::srv::AddTasks_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddTasks_Request_ & other) const
  {
    if (this->tasks != other.tasks) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddTasks_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddTasks_Request_

// alias to use template instance with default allocator
using AddTasks_Request =
  smarc_msgs::srv::AddTasks_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__AddTasks_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__AddTasks_Response __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct AddTasks_Response_
{
  using Type = AddTasks_Response_<ContainerAllocator>;

  explicit AddTasks_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = 0ull;
    }
  }

  explicit AddTasks_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__AddTasks_Response
    std::shared_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__AddTasks_Response
    std::shared_ptr<smarc_msgs::srv::AddTasks_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const AddTasks_Response_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const AddTasks_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct AddTasks_Response_

// alias to use template instance with default allocator
using AddTasks_Response =
  smarc_msgs::srv::AddTasks_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs

namespace smarc_msgs
{

namespace srv
{

struct AddTasks
{
  using Request = smarc_msgs::srv::AddTasks_Request;
  using Response = smarc_msgs::srv::AddTasks_Response;
};

}  // namespace srv

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASKS__STRUCT_HPP_
