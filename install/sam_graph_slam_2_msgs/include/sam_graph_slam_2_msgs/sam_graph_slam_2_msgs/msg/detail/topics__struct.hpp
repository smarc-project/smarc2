// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from sam_graph_slam_2_msgs:msg/Topics.idl
// generated code does not contain a copyright notice

#ifndef SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
#define SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__sam_graph_slam_2_msgs__msg__Topics __attribute__((deprecated))
#else
# define DEPRECATED__sam_graph_slam_2_msgs__msg__Topics __declspec(deprecated)
#endif

namespace sam_graph_slam_2_msgs
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
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> MAP_LINE_DEPTH_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> MAP_POINT_FEATURE_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> MAP_LINE_FEATURE_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> MAP_MARKED_LINE_SPHERES_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> MAP_MARKED_LINE_LINES_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DETECTOR_HYPOTH_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DETECTOR_MARKER_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DETECTOR_RAW_SSS_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DETECTOR_MARKED_SSS_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> DR_ODOM_TOPIC;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> GT_ODOM_TOPIC;

  // pointer types
  using RawPtr =
    sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> *;
  using ConstRawPtr =
    const sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__sam_graph_slam_2_msgs__msg__Topics
    std::shared_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__sam_graph_slam_2_msgs__msg__Topics
    std::shared_ptr<sam_graph_slam_2_msgs::msg::Topics_<ContainerAllocator> const>
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
  sam_graph_slam_2_msgs::msg::Topics_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::MAP_LINE_DEPTH_TOPIC = "map/line_depth";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::MAP_POINT_FEATURE_TOPIC = "map/point_features";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::MAP_LINE_FEATURE_TOPIC = "map/line_features";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::MAP_MARKED_LINE_SPHERES_TOPIC = "map/marked_lines_spheres";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::MAP_MARKED_LINE_LINES_TOPIC = "map/marked_lines_lines";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DETECTOR_HYPOTH_TOPIC = "payload/sidescan/detection_hypothesis";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DETECTOR_MARKER_TOPIC = "payload/sidescan/detection_markers";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DETECTOR_RAW_SSS_TOPIC = "payload/sidescan/image";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DETECTOR_MARKED_SSS_TOPIC = "payload/sidescan/detection_hypothesis_image";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::DR_ODOM_TOPIC = "graph_dr/dr_odom";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
Topics_<ContainerAllocator>::GT_ODOM_TOPIC = "graph_dr/gt_odom";

}  // namespace msg

}  // namespace sam_graph_slam_2_msgs

#endif  // SAM_GRAPH_SLAM_2_MSGS__MSG__DETAIL__TOPICS__STRUCT_HPP_
