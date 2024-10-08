// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:action/Empty.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__BUILDER_HPP_
#define SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/action/detail/empty__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace action
{


}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_Goal>()
{
  return ::smarc_mission_msgs::action::Empty_Goal(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{


}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_Result>()
{
  return ::smarc_mission_msgs::action::Empty_Result(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{


}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_Feedback>()
{
  return ::smarc_mission_msgs::action::Empty_Feedback(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_Empty_SendGoal_Request_goal
{
public:
  explicit Init_Empty_SendGoal_Request_goal(::smarc_mission_msgs::action::Empty_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::Empty_SendGoal_Request goal(::smarc_mission_msgs::action::Empty_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_SendGoal_Request msg_;
};

class Init_Empty_SendGoal_Request_goal_id
{
public:
  Init_Empty_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Empty_SendGoal_Request_goal goal_id(::smarc_mission_msgs::action::Empty_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_Empty_SendGoal_Request_goal(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_SendGoal_Request>()
{
  return smarc_mission_msgs::action::builder::Init_Empty_SendGoal_Request_goal_id();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_Empty_SendGoal_Response_stamp
{
public:
  explicit Init_Empty_SendGoal_Response_stamp(::smarc_mission_msgs::action::Empty_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::Empty_SendGoal_Response stamp(::smarc_mission_msgs::action::Empty_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_SendGoal_Response msg_;
};

class Init_Empty_SendGoal_Response_accepted
{
public:
  Init_Empty_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Empty_SendGoal_Response_stamp accepted(::smarc_mission_msgs::action::Empty_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_Empty_SendGoal_Response_stamp(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_SendGoal_Response>()
{
  return smarc_mission_msgs::action::builder::Init_Empty_SendGoal_Response_accepted();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_Empty_GetResult_Request_goal_id
{
public:
  Init_Empty_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_mission_msgs::action::Empty_GetResult_Request goal_id(::smarc_mission_msgs::action::Empty_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_GetResult_Request>()
{
  return smarc_mission_msgs::action::builder::Init_Empty_GetResult_Request_goal_id();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_Empty_GetResult_Response_result
{
public:
  explicit Init_Empty_GetResult_Response_result(::smarc_mission_msgs::action::Empty_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::Empty_GetResult_Response result(::smarc_mission_msgs::action::Empty_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_GetResult_Response msg_;
};

class Init_Empty_GetResult_Response_status
{
public:
  Init_Empty_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Empty_GetResult_Response_result status(::smarc_mission_msgs::action::Empty_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_Empty_GetResult_Response_result(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_GetResult_Response>()
{
  return smarc_mission_msgs::action::builder::Init_Empty_GetResult_Response_status();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_Empty_FeedbackMessage_feedback
{
public:
  explicit Init_Empty_FeedbackMessage_feedback(::smarc_mission_msgs::action::Empty_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::Empty_FeedbackMessage feedback(::smarc_mission_msgs::action::Empty_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_FeedbackMessage msg_;
};

class Init_Empty_FeedbackMessage_goal_id
{
public:
  Init_Empty_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Empty_FeedbackMessage_feedback goal_id(::smarc_mission_msgs::action::Empty_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_Empty_FeedbackMessage_feedback(msg_);
  }

private:
  ::smarc_mission_msgs::action::Empty_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::Empty_FeedbackMessage>()
{
  return smarc_mission_msgs::action::builder::Init_Empty_FeedbackMessage_goal_id();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__ACTION__DETAIL__EMPTY__BUILDER_HPP_
