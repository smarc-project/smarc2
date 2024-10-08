// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'ns'
#include "sam_msgs/msg/detail/uavcan_node_status__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__UavcanNodeStatusNamed __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__UavcanNodeStatusNamed __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct UavcanNodeStatusNamed_
{
  using Type = UavcanNodeStatusNamed_<ContainerAllocator>;

  explicit UavcanNodeStatusNamed_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : ns(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
      this->name = "";
    }
  }

  explicit UavcanNodeStatusNamed_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : name(_alloc),
    ns(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0;
      this->name = "";
    }
  }

  // field types and members
  using _id_type =
    uint8_t;
  _id_type id;
  using _name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _name_type name;
  using _ns_type =
    sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator>;
  _ns_type ns;

  // setters for named parameter idiom
  Type & set__id(
    const uint8_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->name = _arg;
    return *this;
  }
  Type & set__ns(
    const sam_msgs::msg::UavcanNodeStatus_<ContainerAllocator> & _arg)
  {
    this->ns = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__UavcanNodeStatusNamed
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__UavcanNodeStatusNamed
    std::shared_ptr<sam_msgs::msg::UavcanNodeStatusNamed_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UavcanNodeStatusNamed_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->name != other.name) {
      return false;
    }
    if (this->ns != other.ns) {
      return false;
    }
    return true;
  }
  bool operator!=(const UavcanNodeStatusNamed_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UavcanNodeStatusNamed_

// alias to use template instance with default allocator
using UavcanNodeStatusNamed =
  sam_msgs::msg::UavcanNodeStatusNamed_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__STRUCT_HPP_
