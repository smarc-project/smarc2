#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include <chrono>
#include <set>

using namespace std::chrono_literals;

class OdometryEntry
{
public:
  explicit OdometryEntry(const nav_msgs::msg::Odometry & msg)
    : msg_(msg), last_seen_(rclcpp::Clock().now())
  {}

  void update_time()
  {
    last_seen_ = rclcpp::Clock().now();
  }

  const nav_msgs::msg::Odometry & msg() const { return msg_; }
  const rclcpp::Time & last_seen() const { return last_seen_; }
  const std::string & child_frame_id() const { return msg_.child_frame_id; }

  bool operator<(const OdometryEntry & other) const
  {
    return msg_.child_frame_id < other.msg_.child_frame_id;
  }

private:
  nav_msgs::msg::Odometry msg_;
  rclcpp::Time last_seen_;
};


class OdometryBuffer
{
public:
  OdometryBuffer(size_t max_size = 1, rclcpp::Duration memory_time = rclcpp::Duration::from_seconds(60.0))
    : max_size_(max_size), memory_time_(memory_time)
  {}

  void add(const nav_msgs::msg::Odometry & msg)
  {
    OdometryEntry new_entry(msg);

    auto it = buffer_.find(new_entry);
    if (it != buffer_.end())
    {
      buffer_.erase(it);
    }
    else if (buffer_.size() >= max_size_)
    {
      buffer_.erase(buffer_.begin());
    }

    buffer_.insert(new_entry);
  }

  void update()
  {
    rclcpp::Time now = rclcpp::Clock().now();
    auto it = buffer_.begin();
    while (it != buffer_.end())
    {
      if ((now - it->last_seen()) > memory_time_)
      {
        it = buffer_.erase(it);
      }
      else
      {
        ++it;
      }
    }
  }

  auto begin() const { return buffer_.begin(); }
  auto end() const { return buffer_.end(); }

  const std::set<OdometryEntry> & messages() const { return buffer_; }

  size_t size() const { return buffer_.size(); }
  bool empty() const { return buffer_.empty(); }
  bool full() const { return buffer_.size() >= max_size_; }

private:
  std::set<OdometryEntry> buffer_;
  size_t max_size_;
  rclcpp::Duration memory_time_;
};