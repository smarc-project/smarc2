// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ArrayCommand.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/array_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ArrayCommand_commands
{
public:
  Init_ArrayCommand_commands()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::sam_msgs::msg::ArrayCommand commands(::sam_msgs::msg::ArrayCommand::_commands_type arg)
  {
    msg_.commands = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ArrayCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ArrayCommand>()
{
  return sam_msgs::msg::builder::Init_ArrayCommand_commands();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__ARRAY_COMMAND__BUILDER_HPP_
