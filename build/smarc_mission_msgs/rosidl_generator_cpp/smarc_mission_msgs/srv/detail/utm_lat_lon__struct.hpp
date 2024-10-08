// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_mission_msgs:srv/UTMLatLon.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'utm_points'
#include "geometry_msgs/msg/detail/point_stamped__struct.hpp"
// Member 'lat_lon_points'
#include "geographic_msgs/msg/detail/geo_point__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Request __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct UTMLatLon_Request_
{
  using Type = UTMLatLon_Request_<ContainerAllocator>;

  explicit UTMLatLon_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit UTMLatLon_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _utm_points_type =
    std::vector<geometry_msgs::msg::PointStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PointStamped_<ContainerAllocator>>>;
  _utm_points_type utm_points;
  using _lat_lon_points_type =
    std::vector<geographic_msgs::msg::GeoPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geographic_msgs::msg::GeoPoint_<ContainerAllocator>>>;
  _lat_lon_points_type lat_lon_points;

  // setters for named parameter idiom
  Type & set__utm_points(
    const std::vector<geometry_msgs::msg::PointStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PointStamped_<ContainerAllocator>>> & _arg)
  {
    this->utm_points = _arg;
    return *this;
  }
  Type & set__lat_lon_points(
    const std::vector<geographic_msgs::msg::GeoPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geographic_msgs::msg::GeoPoint_<ContainerAllocator>>> & _arg)
  {
    this->lat_lon_points = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Request
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Request
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UTMLatLon_Request_ & other) const
  {
    if (this->utm_points != other.utm_points) {
      return false;
    }
    if (this->lat_lon_points != other.lat_lon_points) {
      return false;
    }
    return true;
  }
  bool operator!=(const UTMLatLon_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UTMLatLon_Request_

// alias to use template instance with default allocator
using UTMLatLon_Request =
  smarc_mission_msgs::srv::UTMLatLon_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_mission_msgs


// Include directives for member types
// Member 'lat_lon_points'
// already included above
// #include "geographic_msgs/msg/detail/geo_point__struct.hpp"
// Member 'utm_points'
// already included above
// #include "geometry_msgs/msg/detail/point_stamped__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Response __declspec(deprecated)
#endif

namespace smarc_mission_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct UTMLatLon_Response_
{
  using Type = UTMLatLon_Response_<ContainerAllocator>;

  explicit UTMLatLon_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit UTMLatLon_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _lat_lon_points_type =
    std::vector<geographic_msgs::msg::GeoPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geographic_msgs::msg::GeoPoint_<ContainerAllocator>>>;
  _lat_lon_points_type lat_lon_points;
  using _utm_points_type =
    std::vector<geometry_msgs::msg::PointStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PointStamped_<ContainerAllocator>>>;
  _utm_points_type utm_points;

  // setters for named parameter idiom
  Type & set__lat_lon_points(
    const std::vector<geographic_msgs::msg::GeoPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geographic_msgs::msg::GeoPoint_<ContainerAllocator>>> & _arg)
  {
    this->lat_lon_points = _arg;
    return *this;
  }
  Type & set__utm_points(
    const std::vector<geometry_msgs::msg::PointStamped_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::PointStamped_<ContainerAllocator>>> & _arg)
  {
    this->utm_points = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Response
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_mission_msgs__srv__UTMLatLon_Response
    std::shared_ptr<smarc_mission_msgs::srv::UTMLatLon_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const UTMLatLon_Response_ & other) const
  {
    if (this->lat_lon_points != other.lat_lon_points) {
      return false;
    }
    if (this->utm_points != other.utm_points) {
      return false;
    }
    return true;
  }
  bool operator!=(const UTMLatLon_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct UTMLatLon_Response_

// alias to use template instance with default allocator
using UTMLatLon_Response =
  smarc_mission_msgs::srv::UTMLatLon_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace smarc_mission_msgs
{

namespace srv
{

struct UTMLatLon
{
  using Request = smarc_mission_msgs::srv::UTMLatLon_Request;
  using Response = smarc_mission_msgs::srv::UTMLatLon_Response;
};

}  // namespace srv

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__STRUCT_HPP_
