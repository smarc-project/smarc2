// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smarc_msgs:msg/Sidescan.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__SIDESCAN__TRAITS_HPP_
#define SMARC_MSGS__MSG__DETAIL__SIDESCAN__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smarc_msgs/msg/detail/sidescan__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace smarc_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Sidescan & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: type
  {
    out << "type: ";
    rosidl_generator_traits::value_to_yaml(msg.type, out);
    out << ", ";
  }

  // member: time
  {
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << ", ";
  }

  // member: frequency_id
  {
    out << "frequency_id: ";
    rosidl_generator_traits::value_to_yaml(msg.frequency_id, out);
    out << ", ";
  }

  // member: gain
  {
    out << "gain: ";
    rosidl_generator_traits::value_to_yaml(msg.gain, out);
    out << ", ";
  }

  // member: decimation
  {
    out << "decimation: ";
    rosidl_generator_traits::value_to_yaml(msg.decimation, out);
    out << ", ";
  }

  // member: max_duration
  {
    out << "max_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.max_duration, out);
    out << ", ";
  }

  // member: port_channel
  {
    if (msg.port_channel.size() == 0) {
      out << "port_channel: []";
    } else {
      out << "port_channel: [";
      size_t pending_items = msg.port_channel.size();
      for (auto item : msg.port_channel) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: starboard_channel
  {
    if (msg.starboard_channel.size() == 0) {
      out << "starboard_channel: []";
    } else {
      out << "starboard_channel: [";
      size_t pending_items = msg.starboard_channel.size();
      for (auto item : msg.starboard_channel) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: port_channel_angle_high
  {
    if (msg.port_channel_angle_high.size() == 0) {
      out << "port_channel_angle_high: []";
    } else {
      out << "port_channel_angle_high: [";
      size_t pending_items = msg.port_channel_angle_high.size();
      for (auto item : msg.port_channel_angle_high) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: port_channel_angle_low
  {
    if (msg.port_channel_angle_low.size() == 0) {
      out << "port_channel_angle_low: []";
    } else {
      out << "port_channel_angle_low: [";
      size_t pending_items = msg.port_channel_angle_low.size();
      for (auto item : msg.port_channel_angle_low) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: starboard_channel_angle_high
  {
    if (msg.starboard_channel_angle_high.size() == 0) {
      out << "starboard_channel_angle_high: []";
    } else {
      out << "starboard_channel_angle_high: [";
      size_t pending_items = msg.starboard_channel_angle_high.size();
      for (auto item : msg.starboard_channel_angle_high) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: starboard_channel_angle_low
  {
    if (msg.starboard_channel_angle_low.size() == 0) {
      out << "starboard_channel_angle_low: []";
    } else {
      out << "starboard_channel_angle_low: [";
      size_t pending_items = msg.starboard_channel_angle_low.size();
      for (auto item : msg.starboard_channel_angle_low) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: extra_channel
  {
    if (msg.extra_channel.size() == 0) {
      out << "extra_channel: []";
    } else {
      out << "extra_channel: [";
      size_t pending_items = msg.extra_channel.size();
      for (auto item : msg.extra_channel) {
        rosidl_generator_traits::value_to_yaml(item, out);
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
  const Sidescan & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "type: ";
    rosidl_generator_traits::value_to_yaml(msg.type, out);
    out << "\n";
  }

  // member: time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << "\n";
  }

  // member: frequency_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "frequency_id: ";
    rosidl_generator_traits::value_to_yaml(msg.frequency_id, out);
    out << "\n";
  }

  // member: gain
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "gain: ";
    rosidl_generator_traits::value_to_yaml(msg.gain, out);
    out << "\n";
  }

  // member: decimation
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "decimation: ";
    rosidl_generator_traits::value_to_yaml(msg.decimation, out);
    out << "\n";
  }

  // member: max_duration
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "max_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.max_duration, out);
    out << "\n";
  }

  // member: port_channel
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.port_channel.size() == 0) {
      out << "port_channel: []\n";
    } else {
      out << "port_channel:\n";
      for (auto item : msg.port_channel) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: starboard_channel
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.starboard_channel.size() == 0) {
      out << "starboard_channel: []\n";
    } else {
      out << "starboard_channel:\n";
      for (auto item : msg.starboard_channel) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: port_channel_angle_high
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.port_channel_angle_high.size() == 0) {
      out << "port_channel_angle_high: []\n";
    } else {
      out << "port_channel_angle_high:\n";
      for (auto item : msg.port_channel_angle_high) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: port_channel_angle_low
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.port_channel_angle_low.size() == 0) {
      out << "port_channel_angle_low: []\n";
    } else {
      out << "port_channel_angle_low:\n";
      for (auto item : msg.port_channel_angle_low) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: starboard_channel_angle_high
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.starboard_channel_angle_high.size() == 0) {
      out << "starboard_channel_angle_high: []\n";
    } else {
      out << "starboard_channel_angle_high:\n";
      for (auto item : msg.starboard_channel_angle_high) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: starboard_channel_angle_low
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.starboard_channel_angle_low.size() == 0) {
      out << "starboard_channel_angle_low: []\n";
    } else {
      out << "starboard_channel_angle_low:\n";
      for (auto item : msg.starboard_channel_angle_low) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: extra_channel
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.extra_channel.size() == 0) {
      out << "extra_channel: []\n";
    } else {
      out << "extra_channel:\n";
      for (auto item : msg.extra_channel) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Sidescan & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace smarc_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smarc_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smarc_msgs::msg::Sidescan & msg,
  std::ostream & out, size_t indentation = 0)
{
  smarc_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smarc_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smarc_msgs::msg::Sidescan & msg)
{
  return smarc_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smarc_msgs::msg::Sidescan>()
{
  return "smarc_msgs::msg::Sidescan";
}

template<>
inline const char * name<smarc_msgs::msg::Sidescan>()
{
  return "smarc_msgs/msg/Sidescan";
}

template<>
struct has_fixed_size<smarc_msgs::msg::Sidescan>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<smarc_msgs::msg::Sidescan>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<smarc_msgs::msg::Sidescan>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMARC_MSGS__MSG__DETAIL__SIDESCAN__TRAITS_HPP_
