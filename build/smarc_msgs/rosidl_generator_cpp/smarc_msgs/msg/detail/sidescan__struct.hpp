// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_HPP_
#define SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_HPP_

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
# define DEPRECATED__smarc_msgs__msg__Sidescan __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__msg__Sidescan __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Sidescan_
{
  using Type = Sidescan_<ContainerAllocator>;

  explicit Sidescan_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->type = 0;
      this->time = 0ul;
      this->frequency_id = 0;
      this->gain = 0;
      this->decimation = 0;
      this->max_duration = 0.0f;
    }
  }

  explicit Sidescan_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->type = 0;
      this->time = 0ul;
      this->frequency_id = 0;
      this->gain = 0;
      this->decimation = 0;
      this->max_duration = 0.0f;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _type_type =
    uint8_t;
  _type_type type;
  using _time_type =
    uint32_t;
  _time_type time;
  using _frequency_id_type =
    uint8_t;
  _frequency_id_type frequency_id;
  using _gain_type =
    int16_t;
  _gain_type gain;
  using _decimation_type =
    uint16_t;
  _decimation_type decimation;
  using _max_duration_type =
    float;
  _max_duration_type max_duration;
  using _port_channel_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _port_channel_type port_channel;
  using _starboard_channel_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _starboard_channel_type starboard_channel;
  using _port_channel_angle_high_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _port_channel_angle_high_type port_channel_angle_high;
  using _port_channel_angle_low_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _port_channel_angle_low_type port_channel_angle_low;
  using _starboard_channel_angle_high_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _starboard_channel_angle_high_type starboard_channel_angle_high;
  using _starboard_channel_angle_low_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _starboard_channel_angle_low_type starboard_channel_angle_low;
  using _extra_channel_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _extra_channel_type extra_channel;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__type(
    const uint8_t & _arg)
  {
    this->type = _arg;
    return *this;
  }
  Type & set__time(
    const uint32_t & _arg)
  {
    this->time = _arg;
    return *this;
  }
  Type & set__frequency_id(
    const uint8_t & _arg)
  {
    this->frequency_id = _arg;
    return *this;
  }
  Type & set__gain(
    const int16_t & _arg)
  {
    this->gain = _arg;
    return *this;
  }
  Type & set__decimation(
    const uint16_t & _arg)
  {
    this->decimation = _arg;
    return *this;
  }
  Type & set__max_duration(
    const float & _arg)
  {
    this->max_duration = _arg;
    return *this;
  }
  Type & set__port_channel(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->port_channel = _arg;
    return *this;
  }
  Type & set__starboard_channel(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->starboard_channel = _arg;
    return *this;
  }
  Type & set__port_channel_angle_high(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->port_channel_angle_high = _arg;
    return *this;
  }
  Type & set__port_channel_angle_low(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->port_channel_angle_low = _arg;
    return *this;
  }
  Type & set__starboard_channel_angle_high(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->starboard_channel_angle_high = _arg;
    return *this;
  }
  Type & set__starboard_channel_angle_low(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->starboard_channel_angle_low = _arg;
    return *this;
  }
  Type & set__extra_channel(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->extra_channel = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::msg::Sidescan_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::msg::Sidescan_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::Sidescan_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::msg::Sidescan_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__msg__Sidescan
    std::shared_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__msg__Sidescan
    std::shared_ptr<smarc_msgs::msg::Sidescan_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Sidescan_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->type != other.type) {
      return false;
    }
    if (this->time != other.time) {
      return false;
    }
    if (this->frequency_id != other.frequency_id) {
      return false;
    }
    if (this->gain != other.gain) {
      return false;
    }
    if (this->decimation != other.decimation) {
      return false;
    }
    if (this->max_duration != other.max_duration) {
      return false;
    }
    if (this->port_channel != other.port_channel) {
      return false;
    }
    if (this->starboard_channel != other.starboard_channel) {
      return false;
    }
    if (this->port_channel_angle_high != other.port_channel_angle_high) {
      return false;
    }
    if (this->port_channel_angle_low != other.port_channel_angle_low) {
      return false;
    }
    if (this->starboard_channel_angle_high != other.starboard_channel_angle_high) {
      return false;
    }
    if (this->starboard_channel_angle_low != other.starboard_channel_angle_low) {
      return false;
    }
    if (this->extra_channel != other.extra_channel) {
      return false;
    }
    return true;
  }
  bool operator!=(const Sidescan_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Sidescan_

// alias to use template instance with default allocator
using Sidescan =
  smarc_msgs::msg::Sidescan_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__SIDESCAN__STRUCT_HPP_
