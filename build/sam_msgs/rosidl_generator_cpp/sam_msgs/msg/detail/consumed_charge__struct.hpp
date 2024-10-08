// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/ConsumedCharge.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_HPP_

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

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__ConsumedCharge __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__ConsumedCharge __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ConsumedCharge_
{
  using Type = ConsumedCharge_<ContainerAllocator>;

  explicit ConsumedCharge_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->circuit_id = 0;
      this->charge = 0.0f;
    }
  }

  explicit ConsumedCharge_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->circuit_id = 0;
      this->charge = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _circuit_id_type =
    uint16_t;
  _circuit_id_type circuit_id;
  using _charge_type =
    float;
  _charge_type charge;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__circuit_id(
    const uint16_t & _arg)
  {
    this->circuit_id = _arg;
    return *this;
  }
  Type & set__charge(
    const float & _arg)
  {
    this->charge = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::ConsumedCharge_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::ConsumedCharge_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ConsumedCharge_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ConsumedCharge_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__ConsumedCharge
    std::shared_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__ConsumedCharge
    std::shared_ptr<sam_msgs::msg::ConsumedCharge_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ConsumedCharge_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->circuit_id != other.circuit_id) {
      return false;
    }
    if (this->charge != other.charge) {
      return false;
    }
    return true;
  }
  bool operator!=(const ConsumedCharge_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ConsumedCharge_

// alias to use template instance with default allocator
using ConsumedCharge =
  sam_msgs::msg::ConsumedCharge_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__STRUCT_HPP_
