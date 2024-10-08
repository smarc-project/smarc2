// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smarc_msgs:srv/CellOccupied.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_HPP_
#define SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__CellOccupied_Request __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__CellOccupied_Request __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CellOccupied_Request_
{
  using Type = CellOccupied_Request_<ContainerAllocator>;

  explicit CellOccupied_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0f;
      this->y = 0.0f;
    }
  }

  explicit CellOccupied_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0f;
      this->y = 0.0f;
    }
  }

  // field types and members
  using _x_type =
    float;
  _x_type x;
  using _y_type =
    float;
  _y_type y;

  // setters for named parameter idiom
  Type & set__x(
    const float & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const float & _arg)
  {
    this->y = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__CellOccupied_Request
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__CellOccupied_Request
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CellOccupied_Request_ & other) const
  {
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    return true;
  }
  bool operator!=(const CellOccupied_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CellOccupied_Request_

// alias to use template instance with default allocator
using CellOccupied_Request =
  smarc_msgs::srv::CellOccupied_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs


#ifndef _WIN32
# define DEPRECATED__smarc_msgs__srv__CellOccupied_Response __attribute__((deprecated))
#else
# define DEPRECATED__smarc_msgs__srv__CellOccupied_Response __declspec(deprecated)
#endif

namespace smarc_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CellOccupied_Response_
{
  using Type = CellOccupied_Response_<ContainerAllocator>;

  explicit CellOccupied_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->cost = 0;
    }
  }

  explicit CellOccupied_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->cost = 0;
    }
  }

  // field types and members
  using _cost_type =
    uint8_t;
  _cost_type cost;

  // setters for named parameter idiom
  Type & set__cost(
    const uint8_t & _arg)
  {
    this->cost = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smarc_msgs__srv__CellOccupied_Response
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smarc_msgs__srv__CellOccupied_Response
    std::shared_ptr<smarc_msgs::srv::CellOccupied_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CellOccupied_Response_ & other) const
  {
    if (this->cost != other.cost) {
      return false;
    }
    return true;
  }
  bool operator!=(const CellOccupied_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CellOccupied_Response_

// alias to use template instance with default allocator
using CellOccupied_Response =
  smarc_msgs::srv::CellOccupied_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace smarc_msgs

namespace smarc_msgs
{

namespace srv
{

struct CellOccupied
{
  using Request = smarc_msgs::srv::CellOccupied_Request;
  using Response = smarc_msgs::srv::CellOccupied_Response;
};

}  // namespace srv

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__STRUCT_HPP_
