// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_msgs:msg/Links.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_HPP_
#define SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_msgs__msg__Links __attribute__((deprecated))
#else
# define DEPRECATED__sam_msgs__msg__Links __declspec(deprecated)
#endif

namespace sam_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Links_
{
  using Type = Links_<ContainerAllocator>;

  explicit Links_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit Links_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> BASE_LINK;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> BASE_LINK_2D;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> PRESS_LINK;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> GPS_LINK;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DVL_LINK;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> ODOM_LINK;

  // pointer types
  using RawPtr =
    sam_msgs::msg::Links_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_msgs::msg::Links_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_msgs::msg::Links_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_msgs::msg::Links_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Links_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Links_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_msgs::msg::Links_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_msgs::msg::Links_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_msgs::msg::Links_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_msgs::msg::Links_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_msgs__msg__Links
    std::shared_ptr<sam_msgs::msg::Links_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_msgs__msg__Links
    std::shared_ptr<sam_msgs::msg::Links_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Links_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const Links_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Links_

// alias to use template instance with default allocator
using Links =
  sam_msgs::msg::Links_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::BASE_LINK = "base_link";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::BASE_LINK_2D = "base_link_2d";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::PRESS_LINK = "pressure_link";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::GPS_LINK = "gps_link";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::DVL_LINK = "dvl_link";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Links_<ContainerAllocator>::ODOM_LINK = "odom";

}  // namespace msg

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LINKS__STRUCT_HPP_
