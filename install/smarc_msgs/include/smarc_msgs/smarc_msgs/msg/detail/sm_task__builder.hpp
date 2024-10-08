// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:msg/SMTask.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SM_TASK__BUILDER_HPP_
#define SMARC_MSGS__MSG__DETAIL__SM_TASK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/msg/detail/sm_task__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace msg
{

namespace builder
{

class Init_SMTask_action_arguments
{
public:
  explicit Init_SMTask_action_arguments(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  ::smarc_msgs::msg::SMTask action_arguments(::smarc_msgs::msg::SMTask::_action_arguments_type arg)
  {
    msg_.action_arguments = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_action_topic
{
public:
  explicit Init_SMTask_action_topic(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_action_arguments action_topic(::smarc_msgs::msg::SMTask::_action_topic_type arg)
  {
    msg_.action_topic = std::move(arg);
    return Init_SMTask_action_arguments(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_max_duration
{
public:
  explicit Init_SMTask_max_duration(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_action_topic max_duration(::smarc_msgs::msg::SMTask::_max_duration_type arg)
  {
    msg_.max_duration = std::move(arg);
    return Init_SMTask_action_topic(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_theta
{
public:
  explicit Init_SMTask_theta(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_max_duration theta(::smarc_msgs::msg::SMTask::_theta_type arg)
  {
    msg_.theta = std::move(arg);
    return Init_SMTask_max_duration(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_altitude
{
public:
  explicit Init_SMTask_altitude(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_theta altitude(::smarc_msgs::msg::SMTask::_altitude_type arg)
  {
    msg_.altitude = std::move(arg);
    return Init_SMTask_theta(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_depth
{
public:
  explicit Init_SMTask_depth(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_altitude depth(::smarc_msgs::msg::SMTask::_depth_type arg)
  {
    msg_.depth = std::move(arg);
    return Init_SMTask_altitude(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_y
{
public:
  explicit Init_SMTask_y(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_depth y(::smarc_msgs::msg::SMTask::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_SMTask_depth(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_x
{
public:
  explicit Init_SMTask_x(::smarc_msgs::msg::SMTask & msg)
  : msg_(msg)
  {}
  Init_SMTask_y x(::smarc_msgs::msg::SMTask::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_SMTask_y(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

class Init_SMTask_task_id
{
public:
  Init_SMTask_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SMTask_x task_id(::smarc_msgs::msg::SMTask::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_SMTask_x(msg_);
  }

private:
  ::smarc_msgs::msg::SMTask msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::msg::SMTask>()
{
  return smarc_msgs::msg::builder::Init_SMTask_task_id();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__MSG__DETAIL__SM_TASK__BUILDER_HPP_
