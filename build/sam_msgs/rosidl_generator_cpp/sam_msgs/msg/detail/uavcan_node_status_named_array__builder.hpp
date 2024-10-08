// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/UavcanNodeStatusNamedArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/uavcan_node_status_named_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_UavcanNodeStatusNamedArray_array
{
public:
  Init_UavcanNodeStatusNamedArray_array()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::sam_msgs::msg::UavcanNodeStatusNamedArray array(::sam_msgs::msg::UavcanNodeStatusNamedArray::_array_type arg)
  {
    msg_.array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::UavcanNodeStatusNamedArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::UavcanNodeStatusNamedArray>()
{
  return sam_msgs::msg::builder::Init_UavcanNodeStatusNamedArray_array();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__UAVCAN_NODE_STATUS_NAMED_ARRAY__BUILDER_HPP_
