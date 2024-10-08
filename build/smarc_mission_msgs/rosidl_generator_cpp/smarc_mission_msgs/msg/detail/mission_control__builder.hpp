// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:msg/MissionControl.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__BUILDER_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/msg/detail/mission_control__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace msg
{

namespace builder
{

class Init_MissionControl_waypoints
{
public:
  explicit Init_MissionControl_waypoints(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::msg::MissionControl waypoints(::smarc_mission_msgs::msg::MissionControl::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_feedback_str
{
public:
  explicit Init_MissionControl_feedback_str(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  Init_MissionControl_waypoints feedback_str(::smarc_mission_msgs::msg::MissionControl::_feedback_str_type arg)
  {
    msg_.feedback_str = std::move(arg);
    return Init_MissionControl_waypoints(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_plan_state
{
public:
  explicit Init_MissionControl_plan_state(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  Init_MissionControl_feedback_str plan_state(::smarc_mission_msgs::msg::MissionControl::_plan_state_type arg)
  {
    msg_.plan_state = std::move(arg);
    return Init_MissionControl_feedback_str(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_command
{
public:
  explicit Init_MissionControl_command(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  Init_MissionControl_plan_state command(::smarc_mission_msgs::msg::MissionControl::_command_type arg)
  {
    msg_.command = std::move(arg);
    return Init_MissionControl_plan_state(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_timeout
{
public:
  explicit Init_MissionControl_timeout(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  Init_MissionControl_command timeout(::smarc_mission_msgs::msg::MissionControl::_timeout_type arg)
  {
    msg_.timeout = std::move(arg);
    return Init_MissionControl_command(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_hash
{
public:
  explicit Init_MissionControl_hash(::smarc_mission_msgs::msg::MissionControl & msg)
  : msg_(msg)
  {}
  Init_MissionControl_timeout hash(::smarc_mission_msgs::msg::MissionControl::_hash_type arg)
  {
    msg_.hash = std::move(arg);
    return Init_MissionControl_timeout(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

class Init_MissionControl_name
{
public:
  Init_MissionControl_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MissionControl_hash name(::smarc_mission_msgs::msg::MissionControl::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_MissionControl_hash(msg_);
  }

private:
  ::smarc_mission_msgs::msg::MissionControl msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::msg::MissionControl>()
{
  return smarc_mission_msgs::msg::builder::Init_MissionControl_name();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__MISSION_CONTROL__BUILDER_HPP_
