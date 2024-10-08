// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ConsumedCharge.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/consumed_charge__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ConsumedCharge_charge
{
public:
  explicit Init_ConsumedCharge_charge(::sam_msgs::msg::ConsumedCharge & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::ConsumedCharge charge(::sam_msgs::msg::ConsumedCharge::_charge_type arg)
  {
    msg_.charge = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedCharge msg_;
};

class Init_ConsumedCharge_circuit_id
{
public:
  explicit Init_ConsumedCharge_circuit_id(::sam_msgs::msg::ConsumedCharge & msg)
  : msg_(msg)
  {}
  Init_ConsumedCharge_charge circuit_id(::sam_msgs::msg::ConsumedCharge::_circuit_id_type arg)
  {
    msg_.circuit_id = std::move(arg);
    return Init_ConsumedCharge_charge(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedCharge msg_;
};

class Init_ConsumedCharge_header
{
public:
  Init_ConsumedCharge_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ConsumedCharge_circuit_id header(::sam_msgs::msg::ConsumedCharge::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ConsumedCharge_circuit_id(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedCharge msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ConsumedCharge>()
{
  return sam_msgs::msg::builder::Init_ConsumedCharge_header();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE__BUILDER_HPP_
