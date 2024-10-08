// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/uavcan_node_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_UavcanNodeStatus_vendor_specific_status_code
{
public:
  explicit Init_UavcanNodeStatus_vendor_specific_status_code(::sam_msgs::msg::UavcanNodeStatus & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::UavcanNodeStatus vendor_specific_status_code(::sam_msgs::msg::UavcanNodeStatus::_vendor_specific_status_code_type arg)
  {
    msg_.vendor_specific_status_code = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatus msg_;
};

class Init_UavcanNodeStatus_sub_mode
{
public:
  explicit Init_UavcanNodeStatus_sub_mode(::sam_msgs::msg::UavcanNodeStatus & msg)
  : msg_(msg)
  {}
  Init_UavcanNodeStatus_vendor_specific_status_code sub_mode(::sam_msgs::msg::UavcanNodeStatus::_sub_mode_type arg)
  {
    msg_.sub_mode = std::move(arg);
    return Init_UavcanNodeStatus_vendor_specific_status_code(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatus msg_;
};

class Init_UavcanNodeStatus_mode
{
public:
  explicit Init_UavcanNodeStatus_mode(::sam_msgs::msg::UavcanNodeStatus & msg)
  : msg_(msg)
  {}
  Init_UavcanNodeStatus_sub_mode mode(::sam_msgs::msg::UavcanNodeStatus::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_UavcanNodeStatus_sub_mode(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatus msg_;
};

class Init_UavcanNodeStatus_health
{
public:
  explicit Init_UavcanNodeStatus_health(::sam_msgs::msg::UavcanNodeStatus & msg)
  : msg_(msg)
  {}
  Init_UavcanNodeStatus_mode health(::sam_msgs::msg::UavcanNodeStatus::_health_type arg)
  {
    msg_.health = std::move(arg);
    return Init_UavcanNodeStatus_mode(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatus msg_;
};

class Init_UavcanNodeStatus_uptime_sec
{
public:
  Init_UavcanNodeStatus_uptime_sec()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_UavcanNodeStatus_health uptime_sec(::sam_msgs::msg::UavcanNodeStatus::_uptime_sec_type arg)
  {
    msg_.uptime_sec = std::move(arg);
    return Init_UavcanNodeStatus_health(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::UavcanNodeStatus>()
{
  return sam_msgs::msg::builder::Init_UavcanNodeStatus_uptime_sec();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS__BUILDER_HPP_
