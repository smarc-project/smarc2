// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/LightCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/light_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_LightCommand_command
{
public:
  explicit Init_LightCommand_command(::sam_msgs::msg::LightCommand & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::LightCommand command(::sam_msgs::msg::LightCommand::_command_type arg)
  {
    msg_.command = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::LightCommand msg_;
};

class Init_LightCommand_id
{
public:
  Init_LightCommand_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_LightCommand_command id(::sam_msgs::msg::LightCommand::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_LightCommand_command(msg_);
  }

private:
  ::sam_msgs::msg::LightCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::LightCommand>()
{
  return sam_msgs::msg::builder::Init_LightCommand_id();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__LIGHT_COMMAND__BUILDER_HPP_
