// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace msg
{

namespace builder
{

class Init_GotoWaypoint_name
{
public:
  explicit Init_GotoWaypoint_name(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::msg::GotoWaypoint name(::smarc_mission_msgs::msg::GotoWaypoint::_name_type arg)
  {
    msg_.name = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_use_heading
{
public:
  explicit Init_GotoWaypoint_use_heading(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_name use_heading(::smarc_mission_msgs::msg::GotoWaypoint::_use_heading_type arg)
  {
    msg_.use_heading = std::move(arg);
    return Init_GotoWaypoint_name(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_arrival_heading
{
public:
  explicit Init_GotoWaypoint_arrival_heading(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_use_heading arrival_heading(::smarc_mission_msgs::msg::GotoWaypoint::_arrival_heading_type arg)
  {
    msg_.arrival_heading = std::move(arg);
    return Init_GotoWaypoint_use_heading(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_lon
{
public:
  explicit Init_GotoWaypoint_lon(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_arrival_heading lon(::smarc_mission_msgs::msg::GotoWaypoint::_lon_type arg)
  {
    msg_.lon = std::move(arg);
    return Init_GotoWaypoint_arrival_heading(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_lat
{
public:
  explicit Init_GotoWaypoint_lat(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_lon lat(::smarc_mission_msgs::msg::GotoWaypoint::_lat_type arg)
  {
    msg_.lat = std::move(arg);
    return Init_GotoWaypoint_lon(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_travel_speed
{
public:
  explicit Init_GotoWaypoint_travel_speed(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_lat travel_speed(::smarc_mission_msgs::msg::GotoWaypoint::_travel_speed_type arg)
  {
    msg_.travel_speed = std::move(arg);
    return Init_GotoWaypoint_lat(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_travel_rpm
{
public:
  explicit Init_GotoWaypoint_travel_rpm(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_travel_speed travel_rpm(::smarc_mission_msgs::msg::GotoWaypoint::_travel_rpm_type arg)
  {
    msg_.travel_rpm = std::move(arg);
    return Init_GotoWaypoint_travel_speed(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_speed_control_mode
{
public:
  explicit Init_GotoWaypoint_speed_control_mode(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_travel_rpm speed_control_mode(::smarc_mission_msgs::msg::GotoWaypoint::_speed_control_mode_type arg)
  {
    msg_.speed_control_mode = std::move(arg);
    return Init_GotoWaypoint_travel_rpm(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_travel_depth
{
public:
  explicit Init_GotoWaypoint_travel_depth(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_speed_control_mode travel_depth(::smarc_mission_msgs::msg::GotoWaypoint::_travel_depth_type arg)
  {
    msg_.travel_depth = std::move(arg);
    return Init_GotoWaypoint_speed_control_mode(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_travel_altitude
{
public:
  explicit Init_GotoWaypoint_travel_altitude(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_travel_depth travel_altitude(::smarc_mission_msgs::msg::GotoWaypoint::_travel_altitude_type arg)
  {
    msg_.travel_altitude = std::move(arg);
    return Init_GotoWaypoint_travel_depth(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_z_control_mode
{
public:
  explicit Init_GotoWaypoint_z_control_mode(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_travel_altitude z_control_mode(::smarc_mission_msgs::msg::GotoWaypoint::_z_control_mode_type arg)
  {
    msg_.z_control_mode = std::move(arg);
    return Init_GotoWaypoint_travel_altitude(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_goal_tolerance
{
public:
  explicit Init_GotoWaypoint_goal_tolerance(::smarc_mission_msgs::msg::GotoWaypoint & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_z_control_mode goal_tolerance(::smarc_mission_msgs::msg::GotoWaypoint::_goal_tolerance_type arg)
  {
    msg_.goal_tolerance = std::move(arg);
    return Init_GotoWaypoint_z_control_mode(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

class Init_GotoWaypoint_pose
{
public:
  Init_GotoWaypoint_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_goal_tolerance pose(::smarc_mission_msgs::msg::GotoWaypoint::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_GotoWaypoint_goal_tolerance(msg_);
  }

private:
  ::smarc_mission_msgs::msg::GotoWaypoint msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::msg::GotoWaypoint>()
{
  return smarc_mission_msgs::msg::builder::Init_GotoWaypoint_pose();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_
