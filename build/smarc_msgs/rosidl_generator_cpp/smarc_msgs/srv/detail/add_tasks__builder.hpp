// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_msgs:srv/AddTasks.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__SRV__DETAIL__ADD_TASKS__BUILDER_HPP_
#define SMARC_MSGS__SRV__DETAIL__ADD_TASKS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_msgs/srv/detail/add_tasks__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_AddTasks_Request_tasks
{
public:
  Init_AddTasks_Request_tasks()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::AddTasks_Request tasks(::smarc_msgs::srv::AddTasks_Request::_tasks_type arg)
  {
    msg_.tasks = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::AddTasks_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::AddTasks_Request>()
{
  return smarc_msgs::srv::builder::Init_AddTasks_Request_tasks();
}

}  // namespace smarc_msgs


namespace smarc_msgs
{

namespace srv
{

namespace builder
{

class Init_AddTasks_Response_task_id
{
public:
  Init_AddTasks_Response_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_msgs::srv::AddTasks_Response task_id(::smarc_msgs::srv::AddTasks_Response::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_msgs::srv::AddTasks_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_msgs::srv::AddTasks_Response>()
{
  return smarc_msgs::srv::builder::Init_AddTasks_Response_task_id();
}

}  // namespace smarc_msgs

#endif  // SMARC_MSGS__SRV__DETAIL__ADD_TASKS__BUILDER_HPP_
