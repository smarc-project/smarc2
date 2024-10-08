// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:srv/DubinsPlan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__BUILDER_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/srv/detail/dubins_plan__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace srv
{

namespace builder
{

class Init_DubinsPlan_Request_turning_radius
{
public:
  explicit Init_DubinsPlan_Request_turning_radius(::smarc_mission_msgs::srv::DubinsPlan_Request & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::srv::DubinsPlan_Request turning_radius(::smarc_mission_msgs::srv::DubinsPlan_Request::_turning_radius_type arg)
  {
    msg_.turning_radius = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::srv::DubinsPlan_Request msg_;
};

class Init_DubinsPlan_Request_step
{
public:
  explicit Init_DubinsPlan_Request_step(::smarc_mission_msgs::srv::DubinsPlan_Request & msg)
  : msg_(msg)
  {}
  Init_DubinsPlan_Request_turning_radius step(::smarc_mission_msgs::srv::DubinsPlan_Request::_step_type arg)
  {
    msg_.step = std::move(arg);
    return Init_DubinsPlan_Request_turning_radius(msg_);
  }

private:
  ::smarc_mission_msgs::srv::DubinsPlan_Request msg_;
};

class Init_DubinsPlan_Request_waypoints
{
public:
  Init_DubinsPlan_Request_waypoints()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DubinsPlan_Request_step waypoints(::smarc_mission_msgs::srv::DubinsPlan_Request::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return Init_DubinsPlan_Request_step(msg_);
  }

private:
  ::smarc_mission_msgs::srv::DubinsPlan_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::srv::DubinsPlan_Request>()
{
  return smarc_mission_msgs::srv::builder::Init_DubinsPlan_Request_waypoints();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace srv
{

namespace builder
{

class Init_DubinsPlan_Response_original_wp_indices
{
public:
  explicit Init_DubinsPlan_Response_original_wp_indices(::smarc_mission_msgs::srv::DubinsPlan_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::srv::DubinsPlan_Response original_wp_indices(::smarc_mission_msgs::srv::DubinsPlan_Response::_original_wp_indices_type arg)
  {
    msg_.original_wp_indices = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::srv::DubinsPlan_Response msg_;
};

class Init_DubinsPlan_Response_waypoints
{
public:
  Init_DubinsPlan_Response_waypoints()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DubinsPlan_Response_original_wp_indices waypoints(::smarc_mission_msgs::srv::DubinsPlan_Response::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return Init_DubinsPlan_Response_original_wp_indices(msg_);
  }

private:
  ::smarc_mission_msgs::srv::DubinsPlan_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::srv::DubinsPlan_Response>()
{
  return smarc_mission_msgs::srv::builder::Init_DubinsPlan_Response_waypoints();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__DUBINS_PLAN__BUILDER_HPP_
