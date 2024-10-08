// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/Leak.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__Leak __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__Leak __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Leak_
{
  using Type = Leak_<ContainerAllocator>;

  explicit Leak_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->value = false;
      this->leak_counter = 0l;
    }
  }

  explicit Leak_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->value = false;
      this->leak_counter = 0l;
    }
  }

  // field types and members
  using _value_type =
    bool;
  _value_type value;
  using _leak_counter_type =
    int32_t;
  _leak_counter_type leak_counter;

  // setters for named parameter idiom
  Type & set__value(
    const bool & _arg)
  {
    this->value = _arg;
    return *this;
  }
  Type & set__leak_counter(
    const int32_t & _arg)
  {
    this->leak_counter = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::Leak_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::Leak_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::Leak_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::Leak_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Leak_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Leak_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Leak_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Leak_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::Leak_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::Leak_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__Leak
    std::shared_ptr<sam_msgs::msg::Leak_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__Leak
    std::shared_ptr<sam_msgs::msg::Leak_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Leak_ & other) const
  {
    if (this->value != other.value) {
      return false;
    }
    if (this->leak_counter != other.leak_counter) {
      return false;
    }
    return true;
  }
  bool operator!=(const Leak_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Leak_

// alias to use template instance with default allocator
using Leak =
  sam_msgs::msg::Leak_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LEAK__STRUCT_HPP_
