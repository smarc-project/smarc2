// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from smarc_mission_msgs:action/GotoWaypoint.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_Goal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_Goal_type_support_ids_t;

static const _GotoWaypoint_Goal_type_support_ids_t _GotoWaypoint_Goal_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_Goal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_Goal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_Goal_type_support_symbol_names_t _GotoWaypoint_Goal_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_Goal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_Goal)),
  }
};

typedef struct _GotoWaypoint_Goal_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_Goal_type_support_data_t;

static _GotoWaypoint_Goal_type_support_data_t _GotoWaypoint_Goal_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_Goal_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_Goal_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_Goal_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_Goal_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_Goal_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_Goal_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Goal>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_Goal_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_Goal)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Goal>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_Result_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_Result_type_support_ids_t;

static const _GotoWaypoint_Result_type_support_ids_t _GotoWaypoint_Result_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_Result_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_Result_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_Result_type_support_symbol_names_t _GotoWaypoint_Result_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_Result)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_Result)),
  }
};

typedef struct _GotoWaypoint_Result_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_Result_type_support_data_t;

static _GotoWaypoint_Result_type_support_data_t _GotoWaypoint_Result_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_Result_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_Result_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_Result_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_Result_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_Result_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_Result_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Result>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_Result_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_Result)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Result>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_Feedback_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_Feedback_type_support_ids_t;

static const _GotoWaypoint_Feedback_type_support_ids_t _GotoWaypoint_Feedback_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_Feedback_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_Feedback_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_Feedback_type_support_symbol_names_t _GotoWaypoint_Feedback_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_Feedback)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_Feedback)),
  }
};

typedef struct _GotoWaypoint_Feedback_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_Feedback_type_support_data_t;

static _GotoWaypoint_Feedback_type_support_data_t _GotoWaypoint_Feedback_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_Feedback_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_Feedback_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_Feedback_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_Feedback_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_Feedback_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_Feedback_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Feedback>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_Feedback_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_Feedback)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_Feedback>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_SendGoal_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_SendGoal_Request_type_support_ids_t;

static const _GotoWaypoint_SendGoal_Request_type_support_ids_t _GotoWaypoint_SendGoal_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_SendGoal_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_SendGoal_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_SendGoal_Request_type_support_symbol_names_t _GotoWaypoint_SendGoal_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Request)),
  }
};

typedef struct _GotoWaypoint_SendGoal_Request_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_SendGoal_Request_type_support_data_t;

static _GotoWaypoint_SendGoal_Request_type_support_data_t _GotoWaypoint_SendGoal_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_SendGoal_Request_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_SendGoal_Request_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_SendGoal_Request_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_SendGoal_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_SendGoal_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_SendGoal_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_SendGoal_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Request)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_SendGoal_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_SendGoal_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_SendGoal_Response_type_support_ids_t;

static const _GotoWaypoint_SendGoal_Response_type_support_ids_t _GotoWaypoint_SendGoal_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_SendGoal_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_SendGoal_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_SendGoal_Response_type_support_symbol_names_t _GotoWaypoint_SendGoal_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Response)),
  }
};

typedef struct _GotoWaypoint_SendGoal_Response_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_SendGoal_Response_type_support_data_t;

static _GotoWaypoint_SendGoal_Response_type_support_data_t _GotoWaypoint_SendGoal_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_SendGoal_Response_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_SendGoal_Response_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_SendGoal_Response_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_SendGoal_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_SendGoal_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_SendGoal_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_SendGoal_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal_Response)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_SendGoal_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_SendGoal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_SendGoal_type_support_ids_t;

static const _GotoWaypoint_SendGoal_type_support_ids_t _GotoWaypoint_SendGoal_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_SendGoal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_SendGoal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_SendGoal_type_support_symbol_names_t _GotoWaypoint_SendGoal_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_SendGoal)),
  }
};

typedef struct _GotoWaypoint_SendGoal_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_SendGoal_type_support_data_t;

static _GotoWaypoint_SendGoal_type_support_data_t _GotoWaypoint_SendGoal_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_SendGoal_service_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_SendGoal_service_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_SendGoal_service_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_SendGoal_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t GotoWaypoint_SendGoal_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_SendGoal_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_SendGoal>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_SendGoal_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_GetResult_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_GetResult_Request_type_support_ids_t;

static const _GotoWaypoint_GetResult_Request_type_support_ids_t _GotoWaypoint_GetResult_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_GetResult_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_GetResult_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_GetResult_Request_type_support_symbol_names_t _GotoWaypoint_GetResult_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Request)),
  }
};

typedef struct _GotoWaypoint_GetResult_Request_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_GetResult_Request_type_support_data_t;

static _GotoWaypoint_GetResult_Request_type_support_data_t _GotoWaypoint_GetResult_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_GetResult_Request_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_GetResult_Request_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_GetResult_Request_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_GetResult_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_GetResult_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_GetResult_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_GetResult_Request>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_GetResult_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Request)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_GetResult_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_GetResult_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_GetResult_Response_type_support_ids_t;

static const _GotoWaypoint_GetResult_Response_type_support_ids_t _GotoWaypoint_GetResult_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_GetResult_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_GetResult_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_GetResult_Response_type_support_symbol_names_t _GotoWaypoint_GetResult_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Response)),
  }
};

typedef struct _GotoWaypoint_GetResult_Response_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_GetResult_Response_type_support_data_t;

static _GotoWaypoint_GetResult_Response_type_support_data_t _GotoWaypoint_GetResult_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_GetResult_Response_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_GetResult_Response_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_GetResult_Response_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_GetResult_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_GetResult_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_GetResult_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_GetResult_Response>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_GetResult_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult_Response)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_GetResult_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_GetResult_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_GetResult_type_support_ids_t;

static const _GotoWaypoint_GetResult_type_support_ids_t _GotoWaypoint_GetResult_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_GetResult_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_GetResult_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_GetResult_type_support_symbol_names_t _GotoWaypoint_GetResult_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_GetResult)),
  }
};

typedef struct _GotoWaypoint_GetResult_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_GetResult_type_support_data_t;

static _GotoWaypoint_GetResult_type_support_data_t _GotoWaypoint_GetResult_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_GetResult_service_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_GetResult_service_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_GetResult_service_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_GetResult_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t GotoWaypoint_GetResult_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_GetResult_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_GetResult>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_GetResult_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _GotoWaypoint_FeedbackMessage_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _GotoWaypoint_FeedbackMessage_type_support_ids_t;

static const _GotoWaypoint_FeedbackMessage_type_support_ids_t _GotoWaypoint_FeedbackMessage_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _GotoWaypoint_FeedbackMessage_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _GotoWaypoint_FeedbackMessage_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _GotoWaypoint_FeedbackMessage_type_support_symbol_names_t _GotoWaypoint_FeedbackMessage_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smarc_mission_msgs, action, GotoWaypoint_FeedbackMessage)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smarc_mission_msgs, action, GotoWaypoint_FeedbackMessage)),
  }
};

typedef struct _GotoWaypoint_FeedbackMessage_type_support_data_t
{
  void * data[2];
} _GotoWaypoint_FeedbackMessage_type_support_data_t;

static _GotoWaypoint_FeedbackMessage_type_support_data_t _GotoWaypoint_FeedbackMessage_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _GotoWaypoint_FeedbackMessage_message_typesupport_map = {
  2,
  "smarc_mission_msgs",
  &_GotoWaypoint_FeedbackMessage_message_typesupport_ids.typesupport_identifier[0],
  &_GotoWaypoint_FeedbackMessage_message_typesupport_symbol_names.symbol_name[0],
  &_GotoWaypoint_FeedbackMessage_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t GotoWaypoint_FeedbackMessage_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_GotoWaypoint_FeedbackMessage_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage>()
{
  return &::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_FeedbackMessage_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, smarc_mission_msgs, action, GotoWaypoint_FeedbackMessage)() {
  return get_message_type_support_handle<smarc_mission_msgs::action::GotoWaypoint_FeedbackMessage>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

#include "action_msgs/msg/goal_status_array.hpp"
#include "action_msgs/srv/cancel_goal.hpp"
// already included above
// #include "smarc_mission_msgs/action/detail/goto_waypoint__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_typesupport_cpp/action_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"

namespace smarc_mission_msgs
{

namespace action
{

namespace rosidl_typesupport_cpp
{

static rosidl_action_type_support_t GotoWaypoint_action_type_support_handle = {
  NULL, NULL, NULL, NULL, NULL};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace smarc_mission_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_action_type_support_t *
get_action_type_support_handle<smarc_mission_msgs::action::GotoWaypoint>()
{
  using ::smarc_mission_msgs::action::rosidl_typesupport_cpp::GotoWaypoint_action_type_support_handle;
  // Thread-safe by always writing the same values to the static struct
  GotoWaypoint_action_type_support_handle.goal_service_type_support = get_service_type_support_handle<::smarc_mission_msgs::action::GotoWaypoint::Impl::SendGoalService>();
  GotoWaypoint_action_type_support_handle.result_service_type_support = get_service_type_support_handle<::smarc_mission_msgs::action::GotoWaypoint::Impl::GetResultService>();
  GotoWaypoint_action_type_support_handle.cancel_service_type_support = get_service_type_support_handle<::smarc_mission_msgs::action::GotoWaypoint::Impl::CancelGoalService>();
  GotoWaypoint_action_type_support_handle.feedback_message_type_support = get_message_type_support_handle<::smarc_mission_msgs::action::GotoWaypoint::Impl::FeedbackMessage>();
  GotoWaypoint_action_type_support_handle.status_message_type_support = get_message_type_support_handle<::smarc_mission_msgs::action::GotoWaypoint::Impl::GoalStatusMessage>();
  return &GotoWaypoint_action_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp
