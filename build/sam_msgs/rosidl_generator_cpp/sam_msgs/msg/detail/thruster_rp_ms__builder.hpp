// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ThrusterRPMs.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__THRUSTER_RP_MS__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__THRUSTER_RP_MS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/thruster_rp_ms__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ThrusterRPMs_header
{
public:
  explicit Init_ThrusterRPMs_header(::sam_msgs::msg::ThrusterRPMs & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::ThrusterRPMs header(::sam_msgs::msg::ThrusterRPMs::_header_type arg)
  {
    msg_.header = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterRPMs msg_;
};

class Init_ThrusterRPMs_thruster_2_rpm
{
public:
  explicit Init_ThrusterRPMs_thruster_2_rpm(::sam_msgs::msg::ThrusterRPMs & msg)
  : msg_(msg)
  {}
  Init_ThrusterRPMs_header thruster_2_rpm(::sam_msgs::msg::ThrusterRPMs::_thruster_2_rpm_type arg)
  {
    msg_.thruster_2_rpm = std::move(arg);
    return Init_ThrusterRPMs_header(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterRPMs msg_;
};

class Init_ThrusterRPMs_thruster_1_rpm
{
public:
  Init_ThrusterRPMs_thruster_1_rpm()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ThrusterRPMs_thruster_2_rpm thruster_1_rpm(::sam_msgs::msg::ThrusterRPMs::_thruster_1_rpm_type arg)
  {
    msg_.thruster_1_rpm = std::move(arg);
    return Init_ThrusterRPMs_thruster_2_rpm(msg_);
  }

private:
  ::sam_msgs::msg::ThrusterRPMs msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ThrusterRPMs>()
{
  return sam_msgs::msg::builder::Init_ThrusterRPMs_thruster_1_rpm();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__THRUSTER_RP_MS__BUILDER_HPP_
