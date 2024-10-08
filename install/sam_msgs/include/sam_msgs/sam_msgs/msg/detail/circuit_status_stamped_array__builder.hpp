// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/CircuitStatusStampedArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/circuit_status_stamped_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_CircuitStatusStampedArray_array
{
public:
  Init_CircuitStatusStampedArray_array()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::sam_msgs::msg::CircuitStatusStampedArray array(::sam_msgs::msg::CircuitStatusStampedArray::_array_type arg)
  {
    msg_.array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatusStampedArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::CircuitStatusStampedArray>()
{
  return sam_msgs::msg::builder::Init_CircuitStatusStampedArray_array();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED_ARRAY__BUILDER_HPP_
