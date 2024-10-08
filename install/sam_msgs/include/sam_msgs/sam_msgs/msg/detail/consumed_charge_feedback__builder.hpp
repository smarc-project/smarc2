// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
// generated code does not contain a copyright notice

#ifndef SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__BUILDER_HPP_
#define SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "sam_msgs/msg/detail/consumed_charge_feedback__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace sam_msgs
{

namespace msg
{

namespace builder
{

class Init_ConsumedChargeFeedback_v33
{
public:
  explicit Init_ConsumedChargeFeedback_v33(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  ::sam_msgs::msg::ConsumedChargeFeedback v33(::sam_msgs::msg::ConsumedChargeFeedback::_v33_type arg)
  {
    msg_.v33 = std::move(arg);
    return std::move(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_v5
{
public:
  explicit Init_ConsumedChargeFeedback_v5(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_v33 v5(::sam_msgs::msg::ConsumedChargeFeedback::_v5_type arg)
  {
    msg_.v5 = std::move(arg);
    return Init_ConsumedChargeFeedback_v33(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_v7
{
public:
  explicit Init_ConsumedChargeFeedback_v7(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_v5 v7(::sam_msgs::msg::ConsumedChargeFeedback::_v7_type arg)
  {
    msg_.v7 = std::move(arg);
    return Init_ConsumedChargeFeedback_v5(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_v12
{
public:
  explicit Init_ConsumedChargeFeedback_v12(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_v7 v12(::sam_msgs::msg::ConsumedChargeFeedback::_v12_type arg)
  {
    msg_.v12 = std::move(arg);
    return Init_ConsumedChargeFeedback_v7(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_v20
{
public:
  explicit Init_ConsumedChargeFeedback_v20(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_v12 v20(::sam_msgs::msg::ConsumedChargeFeedback::_v20_type arg)
  {
    msg_.v20 = std::move(arg);
    return Init_ConsumedChargeFeedback_v12(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_esc3
{
public:
  explicit Init_ConsumedChargeFeedback_esc3(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_v20 esc3(::sam_msgs::msg::ConsumedChargeFeedback::_esc3_type arg)
  {
    msg_.esc3 = std::move(arg);
    return Init_ConsumedChargeFeedback_v20(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_esc2
{
public:
  explicit Init_ConsumedChargeFeedback_esc2(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_esc3 esc2(::sam_msgs::msg::ConsumedChargeFeedback::_esc2_type arg)
  {
    msg_.esc2 = std::move(arg);
    return Init_ConsumedChargeFeedback_esc3(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_esc1
{
public:
  explicit Init_ConsumedChargeFeedback_esc1(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_esc2 esc1(::sam_msgs::msg::ConsumedChargeFeedback::_esc1_type arg)
  {
    msg_.esc1 = std::move(arg);
    return Init_ConsumedChargeFeedback_esc2(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_main
{
public:
  explicit Init_ConsumedChargeFeedback_main(::sam_msgs::msg::ConsumedChargeFeedback & msg)
  : msg_(msg)
  {}
  Init_ConsumedChargeFeedback_esc1 main(::sam_msgs::msg::ConsumedChargeFeedback::_main_type arg)
  {
    msg_.main = std::move(arg);
    return Init_ConsumedChargeFeedback_esc1(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

class Init_ConsumedChargeFeedback_header
{
public:
  Init_ConsumedChargeFeedback_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ConsumedChargeFeedback_main header(::sam_msgs::msg::ConsumedChargeFeedback::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ConsumedChargeFeedback_main(msg_);
  }

private:
  ::sam_msgs::msg::ConsumedChargeFeedback msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::sam_msgs::msg::ConsumedChargeFeedback>()
{
  return sam_msgs::msg::builder::Init_ConsumedChargeFeedback_header();
}

}  // namespace sam_msgs

#endif  // SAM_MSGS__MSG__DETAIL__CONSUMED_CHARGE_FEEDBACK__BUILDER_HPP_
