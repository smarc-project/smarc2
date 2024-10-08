// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_mission_msgs:srv/UTMLatLon.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__TRAITS_HPP_
#define SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_mission_msgs/srv/detail/utm_lat_lon__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'utm_points'
#include "geometry_msgs/msg/detail/point_stamped__traits.hpp"
// Member 'lat_lon_points'
#include "geographic_msgs/msg/detail/geo_point__traits.hpp"

namespace smarc_mission_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const UTMLatLon_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: utm_points
  {
    if (msg.utm_points.size() == 0) {
      out << "utm_points: []";
    } else {
      out << "utm_points: [";
      size_t pending_items = msg.utm_points.size();
      for (auto item : msg.utm_points) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: lat_lon_points
  {
    if (msg.lat_lon_points.size() == 0) {
      out << "lat_lon_points: []";
    } else {
      out << "lat_lon_points: [";
      size_t pending_items = msg.lat_lon_points.size();
      for (auto item : msg.lat_lon_points) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UTMLatLon_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: utm_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.utm_points.size() == 0) {
      out << "utm_points: []\n";
    } else {
      out << "utm_points:\n";
      for (auto item : msg.utm_points) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: lat_lon_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.lat_lon_points.size() == 0) {
      out << "lat_lon_points: []\n";
    } else {
      out << "lat_lon_points:\n";
      for (auto item : msg.lat_lon_points) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UTMLatLon_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_mission_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_mission_msgs::srv::UTMLatLon_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::srv::UTMLatLon_Request & msg)
{
  return smarc_mission_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::srv::UTMLatLon_Request>()
{
  return "smarc_mission_msgs::srv::UTMLatLon_Request";
}

template<>
inline const char * name<smarc_mission_msgs::srv::UTMLatLon_Request>()
{
  return "smarc_mission_msgs/srv/UTMLatLon_Request";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::UTMLatLon_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::UTMLatLon_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::srv::UTMLatLon_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'lat_lon_points'
// already included above
// #include "geographic_msgs/msg/detail/geo_point__traits.hpp"
// Member 'utm_points'
// already included above
// #include "geometry_msgs/msg/detail/point_stamped__traits.hpp"

namespace smarc_mission_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const UTMLatLon_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: lat_lon_points
  {
    if (msg.lat_lon_points.size() == 0) {
      out << "lat_lon_points: []";
    } else {
      out << "lat_lon_points: [";
      size_t pending_items = msg.lat_lon_points.size();
      for (auto item : msg.lat_lon_points) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: utm_points
  {
    if (msg.utm_points.size() == 0) {
      out << "utm_points: []";
    } else {
      out << "utm_points: [";
      size_t pending_items = msg.utm_points.size();
      for (auto item : msg.utm_points) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const UTMLatLon_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: lat_lon_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.lat_lon_points.size() == 0) {
      out << "lat_lon_points: []\n";
    } else {
      out << "lat_lon_points:\n";
      for (auto item : msg.lat_lon_points) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: utm_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.utm_points.size() == 0) {
      out << "utm_points: []\n";
    } else {
      out << "utm_points:\n";
      for (auto item : msg.utm_points) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const UTMLatLon_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace smarc_mission_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_mission_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_mission_msgs::srv::UTMLatLon_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_mission_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_mission_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const smarc_mission_msgs::srv::UTMLatLon_Response & msg)
{
  return smarc_mission_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_mission_msgs::srv::UTMLatLon_Response>()
{
  return "smarc_mission_msgs::srv::UTMLatLon_Response";
}

template<>
inline const char * name<smarc_mission_msgs::srv::UTMLatLon_Response>()
{
  return "smarc_mission_msgs/srv/UTMLatLon_Response";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::UTMLatLon_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::UTMLatLon_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_mission_msgs::srv::UTMLatLon_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<smarc_mission_msgs::srv::UTMLatLon>()
{
  return "smarc_mission_msgs::srv::UTMLatLon";
}

template<>
inline const char * name<smarc_mission_msgs::srv::UTMLatLon>()
{
  return "smarc_mission_msgs/srv/UTMLatLon";
}

template<>
struct has_fixed_size<smarc_mission_msgs::srv::UTMLatLon>
  : std::integral_constant<
    bool,
    has_fixed_size<smarc_mission_msgs::srv::UTMLatLon_Request>::value &&
    has_fixed_size<smarc_mission_msgs::srv::UTMLatLon_Response>::value
  >
{
};

template<>
struct has_bounded_size<smarc_mission_msgs::srv::UTMLatLon>
  : std::integral_constant<
    bool,
    has_bounded_size<smarc_mission_msgs::srv::UTMLatLon_Request>::value &&
    has_bounded_size<smarc_mission_msgs::srv::UTMLatLon_Response>::value
  >
{
};

template<>
struct is_service<smarc_mission_msgs::srv::UTMLatLon>
  : std::true_type
{
};

template<>
struct is_service_request<smarc_mission_msgs::srv::UTMLatLon_Request>
  : std::true_type
{
};

template<>
struct is_service_response<smarc_mission_msgs::srv::UTMLatLon_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MISSION_MSGS__SRV__DETAIL__UTM_LAT_LON__TRAITS_HPP_
