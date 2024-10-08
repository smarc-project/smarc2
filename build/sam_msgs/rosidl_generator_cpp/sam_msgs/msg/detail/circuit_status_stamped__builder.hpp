// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/CircuitStatusStamped.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/circuit_status_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_CircuitStatusStamped_circuit
{
public:
  explicit Init_CircuitStatusStamped_circuit(::sam_msgs::msg::CircuitStatusStamped & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::CircuitStatusStamped circuit(::sam_msgs::msg::CircuitStatusStamped::_circuit_type arg)
  {
    msg_.circuit = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatusStamped msg_;
};

class Init_CircuitStatusStamped_header
{
public:
  Init_CircuitStatusStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CircuitStatusStamped_circuit header(::sam_msgs::msg::CircuitStatusStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CircuitStatusStamped_circuit(msg_);
  }

private:
  ::sam_msgs::msg::CircuitStatusStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::CircuitStatusStamped>()
{
  return sam_msgs::msg::builder::Init_CircuitStatusStamped_header();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CIRCUIT_STATUS_STAMPED__BUILDER_HPP_
