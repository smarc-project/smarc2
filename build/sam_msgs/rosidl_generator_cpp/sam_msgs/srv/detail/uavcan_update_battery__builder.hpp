// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:srv/UavcanUpdateBattery.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__BUILDER_HPP_
#define SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/srv/detail/uavcan_update_battery__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace srv
{

namespace builder
{

class Init_UavcanUpdateBattery_Request_charge
{
public:
  explicit Init_UavcanUpdateBattery_Request_charge(::sam_msgs::srv::UavcanUpdateBattery_Request & msg)
  : msg_(msg)
  {}
  ::sam_msgs::srv::UavcanUpdateBattery_Request charge(::sam_msgs::srv::UavcanUpdateBattery_Request::_charge_type arg)
  {
    msg_.charge = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::srv::UavcanUpdateBattery_Request msg_;
};

class Init_UavcanUpdateBattery_Request_command
{
public:
  explicit Init_UavcanUpdateBattery_Request_command(::sam_msgs::srv::UavcanUpdateBattery_Request & msg)
  : msg_(msg)
  {}
  Init_UavcanUpdateBattery_Request_charge command(::sam_msgs::srv::UavcanUpdateBattery_Request::_command_type arg)
  {
    msg_.command = std::move(arg);
    return Init_UavcanUpdateBattery_Request_charge(msg_);
  }

private:
  ::sam_msgs::srv::UavcanUpdateBattery_Request msg_;
};

class Init_UavcanUpdateBattery_Request_node_id
{
public:
  Init_UavcanUpdateBattery_Request_node_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_UavcanUpdateBattery_Request_command node_id(::sam_msgs::srv::UavcanUpdateBattery_Request::_node_id_type arg)
  {
    msg_.node_id = std::move(arg);
    return Init_UavcanUpdateBattery_Request_command(msg_);
  }

private:
  ::sam_msgs::srv::UavcanUpdateBattery_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::srv::UavcanUpdateBattery_Request>()
{
  return sam_msgs::srv::builder::Init_UavcanUpdateBattery_Request_node_id();
}

}  // namespace sam_msgs


namespace sam_msgs
{

namespace srv
{

namespace builder
{

class Init_UavcanUpdateBattery_Response_success
{
public:
  Init_UavcanUpdateBattery_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::sam_msgs::srv::UavcanUpdateBattery_Response success(::sam_msgs::srv::UavcanUpdateBattery_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::srv::UavcanUpdateBattery_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::srv::UavcanUpdateBattery_Response>()
{
  return sam_msgs::srv::builder::Init_UavcanUpdateBattery_Response_success();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__SRV__DETAIL__UAVCAN_UPDATE_BATTERY__BUILDER_HPP_
