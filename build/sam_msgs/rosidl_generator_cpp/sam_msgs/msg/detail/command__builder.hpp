// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__COMMAND__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_Command_command_value
{
public:
  explicit Init_Command_command_value(::sam_msgs::msg::Command & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::Command command_value(::sam_msgs::msg::Command::_command_value_type arg)
  {
    msg_.command_value = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::Command msg_;
};

class Init_Command_command_type
{
public:
  explicit Init_Command_command_type(::sam_msgs::msg::Command & msg)
  : msg_(msg)
  {}
  Init_Command_command_value command_type(::sam_msgs::msg::Command::_command_type_type arg)
  {
    msg_.command_type = std::move(arg);
    return Init_Command_command_value(msg_);
  }

private:
  ::sam_msgs::msg::Command msg_;
};

class Init_Command_actuator_id
{
public:
  Init_Command_actuator_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Command_command_type actuator_id(::sam_msgs::msg::Command::_actuator_id_type arg)
  {
    msg_.actuator_id = std::move(arg);
    return Init_Command_command_type(msg_);
  }

private:
  ::sam_msgs::msg::Command msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::Command>()
{
  return sam_msgs::msg::builder::Init_Command_actuator_id();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__COMMAND__BUILDER_HPP_
