// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_HPP_

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
# define DEPRECATED__sam_msgs__msg__ConsumedChargeFeedback __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__ConsumedChargeFeedback __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ConsumedChargeFeedback_
{
  using Type = ConsumedChargeFeedback_<ContainerAllocator>;

  explicit ConsumedChargeFeedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->main = 0.0f;
      this->esc1 = 0.0f;
      this->esc2 = 0.0f;
      this->esc3 = 0.0f;
      this->v20 = 0.0f;
      this->v12 = 0.0f;
      this->v7 = 0.0f;
      this->v5 = 0.0f;
      this->v33 = 0.0f;
    }
  }

  explicit ConsumedChargeFeedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->main = 0.0f;
      this->esc1 = 0.0f;
      this->esc2 = 0.0f;
      this->esc3 = 0.0f;
      this->v20 = 0.0f;
      this->v12 = 0.0f;
      this->v7 = 0.0f;
      this->v5 = 0.0f;
      this->v33 = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _main_type =
    float;
  _main_type main;
  using _esc1_type =
    float;
  _esc1_type esc1;
  using _esc2_type =
    float;
  _esc2_type esc2;
  using _esc3_type =
    float;
  _esc3_type esc3;
  using _v20_type =
    float;
  _v20_type v20;
  using _v12_type =
    float;
  _v12_type v12;
  using _v7_type =
    float;
  _v7_type v7;
  using _v5_type =
    float;
  _v5_type v5;
  using _v33_type =
    float;
  _v33_type v33;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__main(
    const float & _arg)
  {
    this->main = _arg;
    return *this;
  }
  Type & set__esc1(
    const float & _arg)
  {
    this->esc1 = _arg;
    return *this;
  }
  Type & set__esc2(
    const float & _arg)
  {
    this->esc2 = _arg;
    return *this;
  }
  Type & set__esc3(
    const float & _arg)
  {
    this->esc3 = _arg;
    return *this;
  }
  Type & set__v20(
    const float & _arg)
  {
    this->v20 = _arg;
    return *this;
  }
  Type & set__v12(
    const float & _arg)
  {
    this->v12 = _arg;
    return *this;
  }
  Type & set__v7(
    const float & _arg)
  {
    this->v7 = _arg;
    return *this;
  }
  Type & set__v5(
    const float & _arg)
  {
    this->v5 = _arg;
    return *this;
  }
  Type & set__v33(
    const float & _arg)
  {
    this->v33 = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__ConsumedChargeFeedback
    std::shared_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__ConsumedChargeFeedback
    std::shared_ptr<sam_msgs::msg::ConsumedChargeFeedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ConsumedChargeFeedback_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->main != other.main) {
      return false;
    }
    if (this->esc1 != other.esc1) {
      return false;
    }
    if (this->esc2 != other.esc2) {
      return false;
    }
    if (this->esc3 != other.esc3) {
      return false;
    }
    if (this->v20 != other.v20) {
      return false;
    }
    if (this->v12 != other.v12) {
      return false;
    }
    if (this->v7 != other.v7) {
      return false;
    }
    if (this->v5 != other.v5) {
      return false;
    }
    if (this->v33 != other.v33) {
      return false;
    }
    return true;
  }
  bool operator!=(const ConsumedChargeFeedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ConsumedChargeFeedback_

// alias to use template instance with default allocator
using ConsumedChargeFeedback =
  sam_msgs::msg::ConsumedChargeFeedback_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__STRUCT_HPP_
