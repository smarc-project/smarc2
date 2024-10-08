// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smarc_mission_msgs:action/GotoWaypoint.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_
#define SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_Goal_waypoint
{
public:
  Init_GotoWaypoint_Goal_waypoint()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_Goal waypoint(::smarc_mission_msgs::action::GotoWaypoint_Goal::_waypoint_type arg)
  {
    msg_.waypoint = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_Goal>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_Goal_waypoint();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_Result_reached_waypoint
{
public:
  Init_GotoWaypoint_Result_reached_waypoint()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_Result reached_waypoint(::smarc_mission_msgs::action::GotoWaypoint_Result::_reached_waypoint_type arg)
  {
    msg_.reached_waypoint = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_Result>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_Result_reached_waypoint();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_Feedback_distance_remaining
{
public:
  explicit Init_GotoWaypoint_Feedback_distance_remaining(::smarc_mission_msgs::action::GotoWaypoint_Feedback & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_Feedback distance_remaining(::smarc_mission_msgs::action::GotoWaypoint_Feedback::_distance_remaining_type arg)
  {
    msg_.distance_remaining = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_Feedback msg_;
};

class Init_GotoWaypoint_Feedback_feedback_message
{
public:
  explicit Init_GotoWaypoint_Feedback_feedback_message(::smarc_mission_msgs::action::GotoWaypoint_Feedback & msg)
  : msg_(msg)
  {}
  Init_GotoWaypoint_Feedback_distance_remaining feedback_message(::smarc_mission_msgs::action::GotoWaypoint_Feedback::_feedback_message_type arg)
  {
    msg_.feedback_message = std::move(arg);
    return Init_GotoWaypoint_Feedback_distance_remaining(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_Feedback msg_;
};

class Init_GotoWaypoint_Feedback_time_remaining
{
public:
  Init_GotoWaypoint_Feedback_time_remaining()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_Feedback_feedback_message time_remaining(::smarc_mission_msgs::action::GotoWaypoint_Feedback::_time_remaining_type arg)
  {
    msg_.time_remaining = std::move(arg);
    return Init_GotoWaypoint_Feedback_feedback_message(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_Feedback>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_Feedback_time_remaining();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_SendGoal_Request_goal
{
public:
  explicit Init_GotoWaypoint_SendGoal_Request_goal(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request goal(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request msg_;
};

class Init_GotoWaypoint_SendGoal_Request_goal_id
{
public:
  Init_GotoWaypoint_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_SendGoal_Request_goal goal_id(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_GotoWaypoint_SendGoal_Request_goal(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_SendGoal_Request_goal_id();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_SendGoal_Response_stamp
{
public:
  explicit Init_GotoWaypoint_SendGoal_Response_stamp(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response stamp(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response msg_;
};

class Init_GotoWaypoint_SendGoal_Response_accepted
{
public:
  Init_GotoWaypoint_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_SendGoal_Response_stamp accepted(::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_GotoWaypoint_SendGoal_Response_stamp(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_SendGoal_Response_accepted();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_GetResult_Request_goal_id
{
public:
  Init_GotoWaypoint_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_GetResult_Request goal_id(::smarc_mission_msgs::action::GotoWaypoint_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_GetResult_Request>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_GetResult_Request_goal_id();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_GetResult_Response_result
{
public:
  explicit Init_GotoWaypoint_GetResult_Response_result(::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response result(::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response msg_;
};

class Init_GotoWaypoint_GetResult_Response_status
{
public:
  Init_GotoWaypoint_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_GetResult_Response_result status(::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_GotoWaypoint_GetResult_Response_result(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_GetResult_Response>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_GetResult_Response_status();
}

}  // namespace smarc_mission_msgs


namespace smarc_mission_msgs
{

namespace action
{

namespace builder
{

class Init_GotoWaypoint_FeedbackMessage_feedback
{
public:
  explicit Init_GotoWaypoint_FeedbackMessage_feedback(::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage feedback(::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage msg_;
};

class Init_GotoWaypoint_FeedbackMessage_goal_id
{
public:
  Init_GotoWaypoint_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GotoWaypoint_FeedbackMessage_feedback goal_id(::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_GotoWaypoint_FeedbackMessage_feedback(msg_);
  }

private:
  ::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage>()
{
  return smarc_mission_msgs::action::builder::Init_GotoWaypoint_FeedbackMessage_goal_id();
}

}  // namespace smarc_mission_msgs

#endif  // SMARC_MISSION_MSGS__ACTION__DETAIL__GOTO_WAYPOINT__BUILDER_HPP_
