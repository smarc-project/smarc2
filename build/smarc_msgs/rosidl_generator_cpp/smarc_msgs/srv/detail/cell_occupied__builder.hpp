// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:srv/CellOccupied.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__BUILDER_HPP_
#define SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/srv/detail/cell_occupied__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_CellOccupied_Request_y
{
public:
  explicit Init_CellOccupied_Request_y(::smarc_msgs::srv::CellOccupied_Request & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::srv::CellOccupied_Request y(::smarc_msgs::srv::CellOccupied_Request::_y_type arg)
  {
    msg_.y = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::CellOccupied_Request msg_;
};

class Init_CellOccupied_Request_x
{
public:
  Init_CellOccupied_Request_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CellOccupied_Request_y x(::smarc_msgs::srv::CellOccupied_Request::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_CellOccupied_Request_y(msg_);
  }

private:
  ::smarc_msgs::srv::CellOccupied_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::CellOccupied_Request>()
{
  return smarc_msgs::srv::builder::Init_CellOccupied_Request_x();
}

}  // namespace smarc_msgs


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_CellOccupied_Response_cost
{
public:
  Init_CellOccupied_Response_cost()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::CellOccupied_Response cost(::smarc_msgs::srv::CellOccupied_Response::_cost_type arg)
  {
    msg_.cost = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::CellOccupied_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::CellOccupied_Response>()
{
  return smarc_msgs::srv::builder::Init_CellOccupied_Response_cost();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__CELL_OCCUPIED__BUILDER_HPP_
