#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <memory>
#include <optional>
#include <string>

#include <geodesy/utm.h>
#include <geographic_msgs/msg/geo_point.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <nlohmann/json.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

namespace {

constexpr double kPi = 3.14159265358979323846;

std::string join_topic(const std::string &prefix, const std::string &topic) {
  if (prefix.empty()) {
    return topic;
  }
  if (topic.empty()) {
    return prefix;
  }
  if (prefix.back() == '/') {
    return prefix + topic;
  }
  return prefix + "/" + topic;
}

std::string strip_leading_slash(std::string value) {
  while (!value.empty() && value.front() == '/') {
    value.erase(value.begin());
  }
  return value;
}

double degrees_to_enu_yaw(double heading_degrees) {
  return (kPi * 0.5) - (heading_degrees * kPi / 180.0);
}

std::optional<double> json_number(const nlohmann::json &json) {
  if (json.is_number()) {
    return json.get<double>();
  }

  if (json.is_string()) {
    try {
      return std::stod(json.get<std::string>());
    } catch (const std::exception &) {
      return std::nullopt;
    }
  }

  return std::nullopt;
}

} // namespace

class MqttToRosAgentPublisher : public rclcpp::Node {
public:
  MqttToRosAgentPublisher()
      : Node("mqtt_to_ros_agent_publisher"), tf_buffer_(this->get_clock()),
        tf_listener_(tf_buffer_) {
    robot_name_ = declare_parameter<std::string>("robot_name", "evolo");
    input_topic_prefix_ =
        declare_parameter<std::string>("input_topic_prefix", "waraps");
    position_topic_ =
        declare_parameter<std::string>("position_topic", "sensor/position");
    heading_topic_ =
        declare_parameter<std::string>("heading_topic", "sensor/heading");
    course_topic_ =
        declare_parameter<std::string>("course_topic", "sensor/course");
    speed_topic_ =
        declare_parameter<std::string>("speed_topic", "sensor/speed");
    roll_topic_ = declare_parameter<std::string>("roll_topic", "sensor/roll");
    pitch_topic_ =
        declare_parameter<std::string>("pitch_topic", "sensor/pitch");

    odom_topic_ = declare_parameter<std::string>("odom_topic", "odom");
    geopoint_topic_ =
        declare_parameter<std::string>("geopoint_topic", "latlon");
    odom_frame_ =
        declare_parameter<std::string>("odom_frame", robot_name_ + "/odom");
    utm_frame_override_ =
        declare_parameter<std::string>("utm_frame_override", "");

    const std::string default_child_frame =
        strip_leading_slash(this->get_namespace()) + "/base_link";
    child_frame_ =
        declare_parameter<std::string>("child_frame", default_child_frame);

    publish_rate_hz_ = declare_parameter<double>("publish_rate_hz", 1.0);
    transform_timeout_s_ =
        declare_parameter<double>("transform_timeout_s", 10.0);
    prefer_heading_ = declare_parameter<bool>("prefer_heading", true);
    angle_unit_ = declare_parameter<std::string>("angle_unit", "deg");

    const double ellipse_x_m =
        declare_parameter<double>("position_covariance.ellipse_x_m", 5.0);
    const double ellipse_y_m =
        declare_parameter<double>("position_covariance.ellipse_y_m", 5.0);
    const double ellipse_z_m =
        declare_parameter<double>("position_covariance.ellipse_z_m", 0.0);

    position_covariance_diagonal_ = {ellipse_x_m * ellipse_x_m,
                                     ellipse_y_m * ellipse_y_m,
                                     ellipse_z_m * ellipse_z_m};

    odom_pub_ = create_publisher<nav_msgs::msg::Odometry>(odom_topic_, 10);
    geopoint_pub_ =
        create_publisher<geographic_msgs::msg::GeoPoint>(geopoint_topic_, 10);

    position_sub_ = create_subscription<std_msgs::msg::String>(
        join_topic(input_topic_prefix_, position_topic_), 10,
        [this](const std_msgs::msg::String::SharedPtr msg) {
          handle_position(*msg);
        });
    heading_sub_ = create_scalar_subscription(heading_topic_, latest_heading_);
    course_sub_ = create_scalar_subscription(course_topic_, latest_course_);
    speed_sub_ = create_scalar_subscription(speed_topic_, latest_speed_);
    roll_sub_ = create_scalar_subscription(roll_topic_, latest_roll_);
    pitch_sub_ = create_scalar_subscription(pitch_topic_, latest_pitch_);

    const auto publish_period =
        std::chrono::duration<double>(1.0 / std::max(0.1, publish_rate_hz_));
    timer_ = create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(publish_period),
        [this]() { publish_latest(); });

    RCLCPP_INFO(
        get_logger(),
        "Publishing MQTT agent state from '%s' as '%s' and '%s' in frame '%s'",
        input_topic_prefix_.c_str(), odom_topic_.c_str(),
        geopoint_topic_.c_str(), odom_frame_.c_str());
    RCLCPP_INFO(
        get_logger(),
        "Position covariance ellipse is %.3f m x %.3f m x %.3f m "
        "(diag %.3f, %.3f, %.3f)",
        ellipse_x_m, ellipse_y_m, ellipse_z_m, position_covariance_diagonal_[0],
        position_covariance_diagonal_[1], position_covariance_diagonal_[2]);

    if (!utm_frame_override_.empty()) {
      cache_transform(utm_frame_override_);
    }
  }

private:
  using StringSub = rclcpp::Subscription<std_msgs::msg::String>::SharedPtr;

  StringSub create_scalar_subscription(const std::string &topic,
                                       std::optional<double> &storage) {
    auto *storage_ptr = &storage;
    return create_subscription<std_msgs::msg::String>(
        join_topic(input_topic_prefix_, topic), 10,
        [this, storage_ptr, topic](const std_msgs::msg::String::SharedPtr msg) {
          const auto value = parse_scalar(msg->data);
          if (!value.has_value()) {
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                                 "Ignoring malformed scalar payload on %s: %s",
                                 topic.c_str(), msg->data.c_str());
            return;
          }
          *storage_ptr = value;
        });
  }

  std::optional<double> parse_scalar(const std::string &payload) const {
    try {
      return json_number(nlohmann::json::parse(payload));
    } catch (const nlohmann::json::parse_error &) {
      try {
        return std::stod(payload);
      } catch (const std::exception &) {
        return std::nullopt;
      }
    }
  }

  void handle_position(const std_msgs::msg::String &msg) {
    try {
      const auto json = nlohmann::json::parse(msg.data);
      if (!json.is_object() || !json.contains("latitude") ||
          !json.contains("longitude") || !json.contains("altitude")) {
        RCLCPP_WARN_THROTTLE(
            get_logger(), *get_clock(), 5000,
            "Ignoring position payload without WARAPS GeoPoint fields: %s",
            msg.data.c_str());
        return;
      }

      if (json.contains("type") && json.at("type").is_string() &&
          json.at("type").get<std::string>() != "GeoPoint") {
        RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                             "Position payload type is not GeoPoint: %s",
                             msg.data.c_str());
      }

      geographic_msgs::msg::GeoPoint geopoint;
      geopoint.latitude = json.at("latitude").get<double>();
      geopoint.longitude = json.at("longitude").get<double>();
      geopoint.altitude = json.at("altitude").get<double>();

      latest_geopoint_ = geopoint;
      latest_position_stamp_ = now();
    } catch (const std::exception &error) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                           "Ignoring malformed position payload: %s (%s)",
                           msg.data.c_str(), error.what());
    }
  }

  void publish_latest() {
    if (!latest_geopoint_.has_value()) {
      return;
    }

    geopoint_pub_->publish(*latest_geopoint_);

    geodesy::UTMPoint utm_point;
    geodesy::fromMsg(*latest_geopoint_, utm_point);

    geometry_msgs::msg::PoseStamped utm_pose;
    utm_pose.header.stamp = latest_position_stamp_.value_or(now());
    utm_pose.header.frame_id = make_utm_frame(utm_point);
    utm_pose.pose.position.x = utm_point.easting;
    utm_pose.pose.position.y = utm_point.northing;
    utm_pose.pose.position.z =
        std::isfinite(utm_point.altitude) ? utm_point.altitude : 0.0;
    utm_pose.pose.orientation = make_orientation();

    if (!cached_transform_.has_value() ||
        cached_transform_->header.frame_id != odom_frame_ ||
        cached_transform_->child_frame_id != utm_pose.header.frame_id) {
      if (!cache_transform(utm_pose.header.frame_id)) {
        return;
      }
    }

    if (!cached_transform_.has_value()) {
      return;
    }

    geometry_msgs::msg::PoseStamped odom_pose;
    tf2::doTransform(utm_pose, odom_pose, *cached_transform_);

    nav_msgs::msg::Odometry odom;
    odom.header = odom_pose.header;
    odom.child_frame_id = child_frame_;
    odom.pose.pose = odom_pose.pose;
    odom.pose.covariance[0] = position_covariance_diagonal_[0];
    odom.pose.covariance[7] = position_covariance_diagonal_[1];
    odom.pose.covariance[14] = position_covariance_diagonal_[2];

    if (latest_speed_.has_value()) {
      odom.twist.twist.linear.x = *latest_speed_;
    }

    odom_pub_->publish(odom);
  }

  geometry_msgs::msg::Quaternion make_orientation() const {
    const double roll = angle_to_rad(latest_roll_.value_or(0.0));
    const double pitch = angle_to_rad(latest_pitch_.value_or(0.0));
    const auto heading = select_heading();
    const double yaw = heading.has_value() ? heading_to_yaw(*heading) : 0.0;

    tf2::Quaternion quaternion;
    quaternion.setRPY(roll, pitch, yaw);
    quaternion.normalize();

    geometry_msgs::msg::Quaternion msg;
    msg.x = quaternion.x();
    msg.y = quaternion.y();
    msg.z = quaternion.z();
    msg.w = quaternion.w();
    return msg;
  }

  std::optional<double> select_heading() const {
    if (prefer_heading_) {
      return latest_heading_.has_value() ? latest_heading_ : latest_course_;
    }
    return latest_course_.has_value() ? latest_course_ : latest_heading_;
  }

  double angle_to_rad(double angle) const {
    if (angle_unit_ == "rad" || angle_unit_ == "radian" ||
        angle_unit_ == "radians") {
      return angle;
    }
    return angle * kPi / 180.0;
  }

  double heading_to_yaw(double heading) const {
    if (angle_unit_ == "rad" || angle_unit_ == "radian" ||
        angle_unit_ == "radians") {
      return (kPi * 0.5) - heading;
    }
    return degrees_to_enu_yaw(heading);
  }

  std::string make_utm_frame(const geodesy::UTMPoint &utm_point) const {
    if (!utm_frame_override_.empty()) {
      return utm_frame_override_;
    }
    return "utm_" + std::to_string(static_cast<int>(utm_point.zone)) + "_" +
           std::string(1, utm_point.band);
  }

  bool cache_transform(const std::string &utm_frame) {
    try {
      cached_transform_ = tf_buffer_.lookupTransform(
          odom_frame_, utm_frame, tf2::TimePointZero,
          tf2::durationFromSec(transform_timeout_s_));
      RCLCPP_INFO(get_logger(), "Cached constant transform %s -> %s",
                  utm_frame.c_str(), odom_frame_.c_str());
      return true;
    } catch (const tf2::TransformException &error) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                           "Cannot cache transform from %s to %s: %s",
                           utm_frame.c_str(), odom_frame_.c_str(),
                           error.what());
      return false;
    }
  }

  std::string robot_name_;
  std::string input_topic_prefix_;
  std::string position_topic_;
  std::string heading_topic_;
  std::string course_topic_;
  std::string speed_topic_;
  std::string roll_topic_;
  std::string pitch_topic_;
  std::string odom_topic_;
  std::string geopoint_topic_;
  std::string odom_frame_;
  std::string utm_frame_override_;
  std::string child_frame_;
  double publish_rate_hz_;
  double transform_timeout_s_;
  bool prefer_heading_;
  std::string angle_unit_;
  std::array<double, 3> position_covariance_diagonal_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<geographic_msgs::msg::GeoPoint>::SharedPtr geopoint_pub_;
  StringSub position_sub_;
  StringSub heading_sub_;
  StringSub course_sub_;
  StringSub speed_sub_;
  StringSub roll_sub_;
  StringSub pitch_sub_;
  rclcpp::TimerBase::SharedPtr timer_;

  tf2_ros::Buffer tf_buffer_;
  tf2_ros::TransformListener tf_listener_;
  std::optional<geometry_msgs::msg::TransformStamped> cached_transform_;

  std::optional<geographic_msgs::msg::GeoPoint> latest_geopoint_;
  std::optional<rclcpp::Time> latest_position_stamp_;
  std::optional<double> latest_heading_;
  std::optional<double> latest_course_;
  std::optional<double> latest_speed_;
  std::optional<double> latest_roll_;
  std::optional<double> latest_pitch_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MqttToRosAgentPublisher>());
  rclcpp::shutdown();
  return 0;
}
