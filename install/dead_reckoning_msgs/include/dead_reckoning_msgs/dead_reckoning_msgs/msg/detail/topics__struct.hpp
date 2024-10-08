// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from dead_reckoning_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
#define DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__dead_reckoning_msgs__msg__Topics __attribute__((deprecated))
#else
# define DEPRECATED__dead_reckoning_msgs__msg__Topics __declspec(deprecated)
#endif

namespace dead_reckoning_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Topics_
{
  using Type = Topics_<ContainerAllocator>;

  explicit Topics_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit Topics_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_DEPTH_POSE_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_GPS_ODOM_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ROLL_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_PITCH_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_YAW_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_DEPTH_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_COMPASS_HEADING_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_LAT_LON_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_X_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_Y_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_Z_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_U_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_V_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_W_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_P_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_Q_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_R_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_ALT_TOPIC;

  // pointer types
  using RawPtr =
    dead_reckoning_msgs::msg::Topics_<ContainerAllocator> *;
  using ConstRawPtr =
    const dead_reckoning_msgs::msg::Topics_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      dead_reckoning_msgs::msg::Topics_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      dead_reckoning_msgs::msg::Topics_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__dead_reckoning_msgs__msg__Topics
    std::shared_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__dead_reckoning_msgs__msg__Topics
    std::shared_ptr<dead_reckoning_msgs::msg::Topics_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Topics_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const Topics_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Topics_

// alias to use template instance with default allocator
using Topics =
  dead_reckoning_msgs::msg::Topics_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_TOPIC = "dr/odom";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_DEPTH_POSE_TOPIC = "dr/depth_pose";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_GPS_ODOM_TOPIC = "dr/gps_odom";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ROLL_TOPIC = "dr/roll";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_PITCH_TOPIC = "dr/pitch";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_YAW_TOPIC = "dr/yaw";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_DEPTH_TOPIC = "dr/depth";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_COMPASS_HEADING_TOPIC = "dr/compass_heading";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_LAT_LON_TOPIC = "dr/lat_lon";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_X_TOPIC = "dr/x";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_Y_TOPIC = "dr/y";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_Z_TOPIC = "dr/z";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_U_TOPIC = "dr/u";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_V_TOPIC = "dr/v";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_W_TOPIC = "dr/w";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_P_TOPIC = "dr/p";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_Q_TOPIC = "dr/q";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_R_TOPIC = "dr/r";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_ALT_TOPIC = "dr/alt";

}  // namespace msg

}  // namespace dead_reckoning_msgs

#endif  // DEAD_RECKONING_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
