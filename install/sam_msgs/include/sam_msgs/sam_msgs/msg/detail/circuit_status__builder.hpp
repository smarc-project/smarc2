// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/CircuitStatus.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/circuit_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_CircuitStatus_current
{
public:
  explicit Init_CircuitStatus_current(::sam_msgs::msg::CircuitStatus & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::CircuitStatus current(::sam_msgs::msg::CircuitStatus::_current_type arg)
  {
    msg_.current = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatus msg_;
};

class Init_CircuitStatus_voltage
{
public:
  explicit Init_CircuitStatus_voltage(::sam_msgs::msg::CircuitStatus & msg)
  : msg_(msg)
  {}
  Init_CircuitStatus_current voltage(::sam_msgs::msg::CircuitStatus::_voltage_type arg)
  {
    msg_.voltage = std::move(arg);
    return Init_CircuitStatus_current(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatus msg_;
};

class Init_CircuitStatus_circuit_id
{
public:
  explicit Init_CircuitStatus_circuit_id(::sam_msgs::msg::CircuitStatus & msg)
  : msg_(msg)
  {}
  Init_CircuitStatus_voltage circuit_id(::sam_msgs::msg::CircuitStatus::_circuit_id_type arg)
  {
    msg_.circuit_id = std::move(arg);
    return Init_CircuitStatus_voltage(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatus msg_;
};

class Init_CircuitStatus_error_flags
{
public:
  Init_CircuitStatus_error_flags()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CircuitStatus_circuit_id error_flags(::sam_msgs::msg::CircuitStatus::_error_flags_type arg)
  {
    msg_.error_flags = std::move(arg);
    return Init_CircuitStatus_circuit_id(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::CircuitStatus>()
{
  return sam_msgs::msg::builder::Init_CircuitStatus_error_flags();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS__BUILDER_HPP_
