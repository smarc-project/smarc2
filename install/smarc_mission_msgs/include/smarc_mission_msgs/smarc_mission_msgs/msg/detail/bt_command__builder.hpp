// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:msg/BTCommand.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__BUILDER_HPP_
#define SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/msg/detail/bt_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace msg
{

namespace builder
{

class Init_BTCommand_fb_json
{
public:
  explicit Init_BTCommand_fb_json(::smarc_mission_msgs::msg::BTCommand & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::msg::BTCommand fb_json(::smarc_mission_msgs::msg::BTCommand::_fb_json_type arg)
  {
    msg_.fb_json = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::msg::BTCommand msg_;
};

class Init_BTCommand_cmd_json
{
public:
  explicit Init_BTCommand_cmd_json(::smarc_mission_msgs::msg::BTCommand & msg)
  : msg_(msg)
  {}
  Init_BTCommand_fb_json cmd_json(::smarc_mission_msgs::msg::BTCommand::_cmd_json_type arg)
  {
    msg_.cmd_json = std::move(arg);
    return Init_BTCommand_fb_json(msg_);
  }

private:
  ::smarc_mission_msgs::msg::BTCommand msg_;
};

class Init_BTCommand_msg_type
{
public:
  Init_BTCommand_msg_type()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_BTCommand_cmd_json msg_type(::smarc_mission_msgs::msg::BTCommand::_msg_type_type arg)
  {
    msg_.msg_type = std::move(arg);
    return Init_BTCommand_cmd_json(msg_);
  }

private:
  ::smarc_mission_msgs::msg::BTCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::msg::BTCommand>()
{
  return smarc_mission_msgs::msg::builder::Init_BTCommand_msg_type();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__MSG__DETAIL__BT_COMMAND__BUILDER_HPP_
