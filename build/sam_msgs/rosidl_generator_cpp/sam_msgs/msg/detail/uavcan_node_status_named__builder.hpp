// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamed.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/uavcan_node_status_named__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_UavcanNodeStatusNamed_ns
{
public:
  explicit Init_UavcanNodeStatusNamed_ns(::sam_msgs::msg::UavcanNodeStatusNamed & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::UavcanNodeStatusNamed ns(::sam_msgs::msg::UavcanNodeStatusNamed::_ns_type arg)
  {
    msg_.ns = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatusNamed msg_;
};

class Init_UavcanNodeStatusNamed_name
{
public:
  explicit Init_UavcanNodeStatusNamed_name(::sam_msgs::msg::UavcanNodeStatusNamed & msg)
  : msg_(msg)
  {}
  Init_UavcanNodeStatusNamed_ns name(::sam_msgs::msg::UavcanNodeStatusNamed::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_UavcanNodeStatusNamed_ns(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatusNamed msg_;
};

class Init_UavcanNodeStatusNamed_id
{
public:
  Init_UavcanNodeStatusNamed_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_UavcanNodeStatusNamed_name id(::sam_msgs::msg::UavcanNodeStatusNamed::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_UavcanNodeStatusNamed_name(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatusNamed msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::UavcanNodeStatusNamed>()
{
  return sam_msgs::msg::builder::Init_UavcanNodeStatusNamed_id();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED__BUILDER_HPP_
