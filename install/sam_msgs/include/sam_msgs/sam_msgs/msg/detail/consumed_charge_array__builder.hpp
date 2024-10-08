// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ConsumedChargeArray.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/consumed_charge_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ConsumedChargeArray_array
{
public:
  explicit Init_ConsumedChargeArray_array(::sam_msgs::msg::ConsumedChargeArray & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::ConsumedChargeArray array(::sam_msgs::msg::ConsumedChargeArray::_array_type arg)
  {
    msg_.array = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeArray msg_;
};

class Init_ConsumedChargeArray_header
{
public:
  Init_ConsumedChargeArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ConsumedChargeArray_array header(::sam_msgs::msg::ConsumedChargeArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ConsumedChargeArray_array(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ConsumedChargeArray>()
{
  return sam_msgs::msg::builder::Init_ConsumedChargeArray_header();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_ARRAY__BUILDER_HPP_
