#include <chrono>
#include <memory>
#include <mutex>
#include <optional>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "lolo_msgs/msg/topics.hpp"
#include "smarc_msgs/msg/topics.hpp"
#include "diagnostic_msgs/msg/diagnostic_status.hpp"
#include "diagnostic_updater/diagnostic_updater.hpp"
#include "diagnostic_updater/publisher.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"



#include "pid/Pid.h"

using namespace std::chrono_literals;
using diagnostic_msgs::msg::DiagnosticStatus;

class Lolocontrol : public rclcpp::Node
{
public:
  Lolocontrol() : Node("lolo_controller_node"), updater_(this)
  {
    // Publish period is configurable: ros2 run ... --ros-args -p update_rate:=10
    float update_rate = this->declare_parameter<float>("update_rate", 10);
    min_altitude = this->declare_parameter<float>("min_altitude", 2.0);
    max_rpm = this->declare_parameter<float>("max_rpm", 900);
    differential_thrust_gain = this->declare_parameter<float>("differential_thrust_gain", 1200.0);
    int period_ms = 1000.0 / update_rate;

    //Rosparam for PID settings
    double pid_yaw_p = this->declare_parameter<double>("pid_yaw_p", 1.0);
    double pid_yaw_i = this->declare_parameter<double>("pid_yaw_i", 0.0);
    double pid_yaw_d = this->declare_parameter<double>("pid_yaw_d", 0.0);
    double pid_yaw_limit = this->declare_parameter<double>("pid_yaw_limit", 1.0);
    double pid_yaw_i_limit = this->declare_parameter<double>("pid_yaw_i_limit", 1.0);

    double pid_yaw_rate_p = this->declare_parameter<double>("pid_yaw_rate_p", 1.0);
    double pid_yaw_rate_i = this->declare_parameter<double>("pid_yaw_rate_i", 0.0);
    double pid_yaw_rate_d = this->declare_parameter<double>("pid_yaw_rate_d", 0.0);
    double pid_yaw_rate_limit = this->declare_parameter<double>("pid_yaw_rate_limit", 1.0);
    double pid_yaw_rate_i_limit = this->declare_parameter<double>("pid_yaw_rate_i_limit", 1.0);

    double pid_roll_p = this->declare_parameter<double>("pid_roll_p", 0.1);
    double pid_roll_i = this->declare_parameter<double>("pid_roll_i", 0.0);
    double pid_roll_d = this->declare_parameter<double>("pid_roll_d", 0.0);
    double pid_roll_limit = this->declare_parameter<double>("pid_roll_limit", 0.2);
    double pid_roll_i_limit = this->declare_parameter<double>("pid_roll_i_limit", 0.3);

    double pid_depth_p = this->declare_parameter<double>("pid_depth_p", 1.0);
    double pid_depth_i = this->declare_parameter<double>("pid_depth_i", 0.0);
    double pid_depth_d = this->declare_parameter<double>("pid_depth_d", 0.0);
    double pid_depth_limit = this->declare_parameter<double>("pid_depth_limit", 1.0);
    double pid_depth_i_limit = this->declare_parameter<double>("pid_depth_i_limit", 1.0);

    double pid_pitch_p = this->declare_parameter<double>("pid_pitch_p", 1.0);
    double pid_pitch_i = this->declare_parameter<double>("pid_pitch_i", 0.0);
    double pid_pitch_d = this->declare_parameter<double>("pid_pitch_d", 0.0);
    double pid_pitch_limit = this->declare_parameter<double>("pid_pitch_limit", 1.0);
    double pid_pitch_i_limit = this->declare_parameter<double>("pid_pitch_i_limit", 1.0);

    double pid_speed_p = this->declare_parameter<double>("pid_speed_p", 1.0);
    double pid_speed_i = this->declare_parameter<double>("pid_speed_i", 0.0);
    double pid_speed_d = this->declare_parameter<double>("pid_speed_d", 0.0);
    double pid_speed_limit = this->declare_parameter<double>("pid_speed_limit", 1.0);
    double pid_speed_i_limit = this->declare_parameter<double>("pid_speed_i_limit", 1.0);
  
    //PID regulators
    pid_yaw = PID(
      pid_yaw_p,
      pid_yaw_i,
      pid_yaw_d,
      pid_yaw_limit,
      pid_yaw_i_limit);

    pid_yaw_rate = PID(
      pid_yaw_rate_p,
      pid_yaw_rate_i,
      pid_yaw_rate_d,
      pid_yaw_rate_limit,
      pid_yaw_rate_i_limit);

    pid_roll = PID(
      pid_roll_p,
      pid_roll_i,
      pid_roll_d,
      pid_roll_limit,
      pid_roll_i_limit);

    pid_depth = PID(
      pid_depth_p,
      pid_depth_i,
      pid_depth_d,
      pid_depth_limit,
      pid_depth_i_limit);

    pid_pitch = PID(
      pid_pitch_p,
      pid_pitch_i,
      pid_pitch_d,
      pid_pitch_limit,
      pid_pitch_i_limit);

    pid_speed = PID(
      pid_speed_p,
      pid_speed_i,
      pid_speed_d,
      pid_speed_limit,
      pid_speed_i_limit);


    //Setpoints
    subscription_cmd_wp = this->create_subscription<geometry_msgs::msg::PointStamped>(lolo_msgs::msg::Topics::WP_SETPOINT, 10, std::bind(&Lolocontrol::waypoint_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_yaw = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::YAW_SETPOINT, 10, std::bind(&Lolocontrol::yaw_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_yawrate = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::YAW_RATE_SETPOINT, 10, std::bind(&Lolocontrol::yaw_rate_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_roll = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::ROLL_SETPOINT, 10, std::bind(&Lolocontrol::roll_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_altitude = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::ALTITUDE_SETPOINT, 10, std::bind(&Lolocontrol::altitude_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_pitch = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::PITCH_SETPOINT, 10, std::bind(&Lolocontrol::pitch_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_depth = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::DEPTH_SETPOINT, 10, std::bind(&Lolocontrol::depth_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_speed = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::SPEED_SETPOINT, 10, std::bind(&Lolocontrol::speed_cmd_cb, this, std::placeholders::_1));
    subscription_cmd_rpm = this->create_subscription<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::RPM_SETPOINT, 10, std::bind(&Lolocontrol::rpm_cmd_cb, this, std::placeholders::_1));

    //Feedback
    subscription_fb_odom = this->create_subscription<nav_msgs::msg::Odometry>(smarc_msgs::msg::Topics::ODOM_TOPIC, 10, std::bind(&Lolocontrol::odom_fb_cb, this, std::placeholders::_1));
    subscription_fb_altitude = this->create_subscription<std_msgs::msg::Float32>(smarc_msgs::msg::Topics::ALTITUDE_TOPIC, 10, std::bind(&Lolocontrol::altitude_fb_cb, this, std::placeholders::_1));

    //Output
    publisher_elevator = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::ELEVATOR_CMD, 10);
    publisher_rudder = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::RUDDER_CMD, 10);
    publisher_elevon_port = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::ELEVON_PORT_CMD, 10);
    publisher_elevon_strb = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::ELEVON_STRB_CMD, 10);
    publisher_thruster_port = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::THRUSTER_PORT_CMD, 10);
    publisher_thruster_strb = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::THRUSTER_STRB_CMD, 10);
    publisher_vertical_thruster_front_port = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::VERTICAL_THRUSTER_FRONT_PORT_CMD, 10);
    publisher_vertical_thruster_front_strb = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::VERTICAL_THRUSTER_FRONT_STRB_CMD, 10);
    publisher_vertical_thruster_back_port = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::VERTICAL_THRUSTER_BACK_PORT_CMD, 10);
    publisher_vertical_thruster_back_strb = this->create_publisher<std_msgs::msg::Float32>(lolo_msgs::msg::Topics::VERTICAL_THRUSTER_BACK_STRB_CMD, 10);

    //Diagnostic publisher
    updater_.setHardwareID("lolo_controllers");
    updater_.add("pid-regulators", this, &Lolocontrol::diagnostic_update);

    //TF
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    //Initialize timer vaiables in the past
    wp_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    yaw_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    yaw_rate_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    roll_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    altitude_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    depth_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    pitch_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    speed_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    rpm_cmd_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    odom_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);
    altitude_fb_received_time  = this->now() - rclcpp::Duration::from_seconds(100.0);

    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(period_ms),
      std::bind(&Lolocontrol::on_timer, this));
  }

private:

  //WP
  void waypoint_cmd_cb(geometry_msgs::msg::PointStamped::SharedPtr _msg) {
    // Already in the target frame, nothing to do
    if (_msg->header.frame_id == target_frame_) {
      std::lock_guard<std::mutex> lock(mutex_);
      wp_goal_cmd = *_msg;
      wp_received_time = this->now();
      return;
    }
 
    geometry_msgs::msg::TransformStamped tf;
    try {
      tf = tf_buffer_->lookupTransform(
        target_frame_, _msg->header.frame_id, tf2::TimePointZero); // latest available transform
    } catch (const tf2::TransformException & ex) {
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 2000,
        "Could not transform %s -> %s: %s",
        _msg->header.frame_id.c_str(), target_frame_.c_str(), ex.what());
      return;
    }
 
    geometry_msgs::msg::PointStamped out;
    tf2::doTransform(*_msg, out, tf);  // sets out.header.frame_id to target_frame_
    
    std::lock_guard<std::mutex> lock(mutex_);
    wp_goal_cmd = out;
    wp_received_time = this->now();
  }

  void yaw_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    yaw_cmd = _msg->data;
    yaw_cmd_received_time = this->now();
  }

  void yaw_rate_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    yaw_rate_cmd = _msg->data;
    yaw_rate_cmd_received_time = this->now();
  }

  void roll_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    roll_cmd = _msg->data;
    roll_cmd_received_time = this->now();
  }

  void pitch_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    pitch_cmd = _msg->data;
    pitch_cmd_received_time = this->now();
  }

  void depth_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    depth_cmd = _msg->data;
    depth_cmd_received_time = this->now();
  }

  void altitude_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    altitude_cmd = _msg->data;
    altitude_cmd_received_time = this->now();
  }

  void speed_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    speed_cmd = _msg->data;
    speed_cmd_received_time = this->now();
  }

  void rpm_cmd_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    rpm_cmd = _msg->data;
    rpm_cmd_received_time = this->now();
  }

  void odom_fb_cb(const nav_msgs::msg::Odometry::SharedPtr _msg) {
    
    // Already in the target frame, nothing to do
    if (_msg->header.frame_id == target_frame_) {
      std::lock_guard<std::mutex> lock(mutex_);
      robot_position = *_msg;
      odom_received_time = this->now();
      return;
    }
 
    geometry_msgs::msg::TransformStamped tf;
    try {
      tf = tf_buffer_->lookupTransform(
        target_frame_, _msg->header.frame_id, tf2::TimePointZero); // latest available transform
    } catch (const tf2::TransformException & ex) {
      RCLCPP_WARN_THROTTLE(
        this->get_logger(), *this->get_clock(), 2000,
        "Could not transform %s -> %s: %s",
        _msg->header.frame_id.c_str(), target_frame_.c_str(), ex.what());
      return;
    }
 
    // Transform the pose (incl. covariance) into the target frame
    geometry_msgs::msg::PoseWithCovarianceStamped pose_in, pose_out;
    pose_in.header = _msg->header;
    pose_in.pose = _msg->pose;
    tf2::doTransform(pose_in, pose_out, tf);
 
    nav_msgs::msg::Odometry out;
    out.header.stamp = _msg->header.stamp;
    out.header.frame_id = target_frame_;
    out.pose = pose_out.pose;
    // Twist is expressed in child_frame_id, so it is unchanged
    out.child_frame_id = _msg->child_frame_id;
    out.twist = _msg->twist;

    //save converted odometry to class vaiable
    std::lock_guard<std::mutex> lock(mutex_);
    robot_position = out;
    odom_received_time = this->now();
  }

  void altitude_fb_cb(const std_msgs::msg::Float32::SharedPtr _msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    altitude_fb = _msg->data;
    altitude_fb_received_time = this->now();
  }

  void on_timer()
  {
    //Lock so no new setpoints are received when accessing them
    std::lock_guard<std::mutex> lock(mutex_);
    RCLCPP_INFO(this->get_logger(), "Calculating control");

    //1. Check that odom has been received
    if ((this->now() - odom_received_time) > rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tOdom feedback old");
      return;
    }

    //2. Get pitch roll yaw from Odom
    // Roll, pitch, yaw (radians) of the transformed orientation
    tf2::Quaternion q;
    tf2::fromMsg(robot_position.pose.pose.orientation, q);
    double robot_roll, robot_pitch, robot_yaw, robot_yaw_rate;
    tf2::Matrix3x3(q).getRPY(robot_roll, robot_pitch, robot_yaw);
    robot_yaw_rate = robot_position.twist.twist.angular.z;
 
    RCLCPP_DEBUG(
      this->get_logger(), "roll: %.3f, pitch: %.3f, yaw: %.3f [rad]",
      robot_roll, robot_pitch, robot_yaw);

    bool steering_set = false;
    double yaw_setpoint;
    double yaw_rate_setpoint;
    double yaw_rate_error;
    //steering_actuation

    bool depth_set = false;
    double depth_error = 0;;
    double depth_setpoint;
    double pitch_setpoint;
    //pitch_actuation

    bool roll_set = false;
    double roll_setpoint;
    //roll_actuation

    bool speed_set = false;
    double speed_setpoint;
    //thruster_actuation

    //3. calculate control
    rclcpp::Time t = this->now();
    double time_now_seconds = t.seconds();
    
    
    //***********************Steering*********************
    //high level = WP -> gives yaw
    if ((this->now() - wp_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tWP_CONTROL");
      double dx = wp_goal_cmd.point.x - robot_position.pose.pose.position.x;
      double dy = wp_goal_cmd.point.y - robot_position.pose.pose.position.y;
      yaw_setpoint = atan2(dy,dx);
      depth_setpoint = -wp_goal_cmd.point.z;
      steering_set = true;
      depth_set = true;
    }
    //Yaw
    if ((this->now() - yaw_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tYAW_CONTROL");
      yaw_setpoint = yaw_cmd;
      steering_set = true;
    }
    //
    if(steering_set) {
        double d = yaw_setpoint - robot_yaw;
        double error = std::atan2(std::sin(d), std::cos(d));
        yaw_rate_setpoint = pid_yaw.update_error(error, time_now_seconds);
    }
    if ((this->now() - yaw_rate_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tYAWRATE_CONTROL");
      yaw_rate_setpoint = yaw_rate_cmd;
      steering_set = true;
    }
    if(steering_set) {
        yaw_rate_error = yaw_rate_setpoint - robot_yaw_rate;
        steering_actuation = pid_yaw_rate.update_error(yaw_rate_error, time_now_seconds);
    }

    //*************************depth**********************
    if ((this->now() - depth_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tDEPTH_CONTROL");
      depth_setpoint = depth_cmd;
      depth_set = true;

      //Adjust depth based on altitude
      float altitude_setpoint = min_altitude;
      if ((this->now() - altitude_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
        altitude_setpoint = std::max(altitude_setpoint, altitude_cmd);
      }

      if ((this->now() - altitude_fb_received_time) < rclcpp::Duration::from_seconds(3.0)) {
        depth_setpoint = std::min(depth_setpoint, (-robot_position.pose.pose.position.z+altitude_fb) - altitude_setpoint);
      }
      else {
        RCLCPP_WARN(this->get_logger(), "\t\tWarning no altitude feedback. Only doing depth control");
      }
    }

    if(depth_set) {
      depth_error = depth_setpoint - (-robot_position.pose.pose.position.z);
      pitch_setpoint = pid_depth.update_error(depth_error, time_now_seconds);
    }

    if ((this->now() - pitch_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tPITCH_CONTROL");
      pitch_setpoint = pitch_cmd;
      depth_set = true;
    }

    if(depth_set) {
      double error = pitch_setpoint - robot_pitch;
      pitch_actuation = pid_pitch.update_error(error, time_now_seconds);
    }

    //**************************roll***********************
    if ((this->now() - roll_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tROLL_CONTROL");
      roll_setpoint = roll_cmd;
      roll_set = true;
    }
    //Automaticaly set roll=0 if either steering or depth control is active
    if(!roll_set && (depth_set || steering_set)) { 
      roll_setpoint = 0;
      roll_set = 0;
    }
    if(roll_set) {
      double error = roll_setpoint - robot_roll;
      roll_actuation = pid_roll.update_error(error, time_now_seconds);
    }

    //**************************Speed**********************
    if ((this->now() - speed_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tSPEED_CONTROL");
      speed_setpoint = speed_cmd;
      speed_set = true;
    }
    if(speed_set) {
      double error = speed_setpoint - robot_position.twist.twist.linear.x;
      thruster_actuation = pid_speed.update_error(error, time_now_seconds);
    }
    if ((this->now() - rpm_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      RCLCPP_INFO(this->get_logger(), "\tRPM_CONTROL");
      thruster_actuation = rpm_cmd;
      speed_set = true;
    }

    //************************Mixing*********************
    std_msgs::msg::Float32 elevator;
    std_msgs::msg::Float32 rudder;
    std_msgs::msg::Float32 elevon_port;
    std_msgs::msg::Float32 elevon_strb;
    std_msgs::msg::Float32 thruster_port;
    std_msgs::msg::Float32 thruster_strb;
    std_msgs::msg::Float32 vertical_thruster_front_port;
    std_msgs::msg::Float32 vertical_thruster_front_strb;
    std_msgs::msg::Float32 vertical_thruster_back_port;
    std_msgs::msg::Float32 vertical_thruster_back_strb;

    bool diving = robot_position.pose.pose.position.z <= -0.8;

    //dive help (Vertical thrusters)
    /*
    if ((this->now() - depth_cmd_received_time) < rclcpp::Duration::from_seconds(1.0)) {
      if(robot_position.pose.pose.position.z > 0.75 and depth_cmd > 0.1) {
        //vertical thrusters
        vertical_thruster_front_port.data = -2000.0;
        vertical_thruster_front_strb.data = -2000.0;
      }
    }
    */

    //Yaw error bucket
    yaw_error_bucket += std::abs(yaw_rate_error);
    yaw_error_bucket = std::max(0.0, yaw_error_bucket-yaw_error_bucket_leak);
    yaw_error_bucket = std::min(yaw_error_bucket, yaw_error_bucket_max);

    RCLCPP_INFO(this->get_logger(), "Yaw error bucket: %f", yaw_error_bucket);

    //Steering
    if(steering_set) {
      //Rudder
      if(diving) { //diving
          rudder.data = -steering_actuation;
      }
      else{
        rudder.data = -steering_actuation*0.2;
      }

      //differential trust (on the surface and if we have problems steering under water)
      yaw_actuation_filtered = (1.0-yaw_actuation_filter_setting)*yaw_actuation_filtered + yaw_actuation_filter_setting*steering_actuation;
      yaw_error_bucket += std::abs(yaw_actuation_filtered);

      //Only use thrusters if speed / rpm setpoint is acive
      if(speed_set && (!diving || yaw_error_bucket > yaw_error_bucket_limit) ) {
        thruster_port.data = -1 * differential_thrust_gain*yaw_actuation_filtered;
        thruster_strb.data = differential_thrust_gain*yaw_actuation_filtered;
        if(diving) { //Clamp differential thrust when diving
          thruster_port.data = std::clamp(thruster_port.data, -dive_diff_thrust_limit, dive_diff_thrust_limit);
          thruster_strb.data = std::clamp(thruster_strb.data, -dive_diff_thrust_limit, dive_diff_thrust_limit);
        } else { //reduce forward speed if steering error is big on the surface
          double scaling_factor = std::max(0.0, 1.0 - 1.5*(std::abs(yaw_actuation_filtered)));
          thruster_actuation *= scaling_factor;
          RCLCPP_INFO(this->get_logger(), "RPM scaled by: %f", scaling_factor);
        }
      }
    }

    //Depth, Altitude, Pitch
    if(depth_set) {
      elevator.data = -pitch_actuation;
      elevon_port.data = -pitch_actuation;
      elevon_strb.data = -pitch_actuation;
      //TODO static diving with vertical thrusters
    }

    //Roll
    if(roll_set) {
      elevon_port.data += -roll_actuation;
      elevon_strb.data += roll_actuation;
      //TODO staic roll contol using vertical thrusters
    }

    //thrusters
    if(speed_set) {
      thruster_port.data += thruster_actuation;
      thruster_strb.data += thruster_actuation;

      thruster_port.data = std::clamp(thruster_port.data, -max_rpm, max_rpm);
      thruster_strb.data = std::clamp(thruster_strb.data, -max_rpm, max_rpm);

      if(std::abs(thruster_port.data) < 50) thruster_port.data = 0;
      if(std::abs(thruster_strb.data) < 50) thruster_strb.data = 0;
    }

    thruster_counter+=1;
    thruster_counter %= thruster_publish_interval;

    //Publish setpoints to actuators
    publisher_elevator->publish(elevator);
    publisher_rudder->publish(rudder);
    publisher_elevon_port->publish(elevon_port);
    publisher_elevon_strb->publish(elevon_strb);
    if(thruster_counter == 0) {
      publisher_thruster_port->publish(thruster_port);
      publisher_thruster_strb->publish(thruster_strb);
    }
    publisher_vertical_thruster_front_port->publish(vertical_thruster_front_port);
    publisher_vertical_thruster_front_strb->publish(vertical_thruster_front_strb);
    publisher_vertical_thruster_back_port->publish(vertical_thruster_back_port);
    publisher_vertical_thruster_back_strb->publish(vertical_thruster_back_strb);

  }

  void diagnostic_update(diagnostic_updater::DiagnosticStatusWrapper & stat)
  {
    stat.summary(DiagnosticStatus::OK, "OK probably?");
    // Key/value pairs

    //Yaw pid
    stat.add("pid_yaw_output", pid_yaw.get_last_output());
    stat.add("pid_yaw_proportional_output", pid_yaw.get_p_component());
    stat.add("pid_yaw_integral_output", pid_yaw.get_i_component());
    stat.add("pid_yaw_derivative_output", pid_yaw.get_d_component());
    //Yaw rate pid
    stat.add("pid_yaw_rate_output", pid_yaw_rate.get_last_output());
    stat.add("pid_yaw_rate_proportional_output", pid_yaw_rate.get_p_component());
    stat.add("pid_yaw_rate_integral_output", pid_yaw_rate.get_i_component());
    stat.add("pid_yaw_rate_derivative_output", pid_yaw_rate.get_d_component());
    //Roll pid
    stat.add("pid_roll_output", pid_roll.get_last_output());
    stat.add("pid_roll_proportional_output", pid_roll.get_p_component());
    stat.add("pid_roll_integral_output", pid_roll.get_i_component());
    stat.add("pid_roll_derivative_output", pid_roll.get_d_component());
    //depth pid
    stat.add("pid_depth_output", pid_depth.get_last_output());
    stat.add("pid_depth_proportional_output", pid_depth.get_p_component());
    stat.add("pid_depth_integral_output", pid_depth.get_i_component());
    stat.add("pid_depth_derivative_output", pid_depth.get_d_component());
    //Pitch pid
    stat.add("pid_pitch_output", pid_pitch.get_last_output());
    stat.add("pid_pitch_proportional_output", pid_pitch.get_p_component());
    stat.add("pid_pitch_integral_output", pid_pitch.get_i_component());
    stat.add("pid_pitch_derivative_output", pid_pitch.get_d_component());
    //Speed pid
    stat.add("pid_speed_output", pid_speed.get_last_output());
    stat.add("pid_speed_proportional_output", pid_speed.get_p_component());
    stat.add("pid_speed_integral_output", pid_speed.get_i_component());
    stat.add("pid_speed_derivative_output", pid_speed.get_d_component());
    //Yaw error bucket
    stat.add("yaw_error_bucket", yaw_error_bucket);
  }

  // ============ local variables =============
  //WP
  geometry_msgs::msg::PointStamped wp_goal_cmd;
  geometry_msgs::msg::PointStamped wp_start_cmd; //preparation for future XTE correction
  rclcpp::Time wp_received_time;

  //Yaw
  float yaw_cmd = 0;
  rclcpp::Time yaw_cmd_received_time;
  float yaw_rate_cmd = 0;
  rclcpp::Time yaw_rate_cmd_received_time;

  //Roll
  float roll_cmd = 0;
  rclcpp::Time roll_cmd_received_time;

  //Altitude
  float min_altitude; // from rosparam
  float altitude_cmd = 0;
  rclcpp::Time altitude_cmd_received_time;

  //Depth
  float depth_cmd = 0;
  rclcpp::Time depth_cmd_received_time;

  //Pitch
  float pitch_cmd = 0;
  rclcpp::Time pitch_cmd_received_time;

  //Speed
  float speed_cmd = 0;
  rclcpp::Time speed_cmd_received_time;

  //RPM
  float rpm_cmd = 0;
  rclcpp::Time rpm_cmd_received_time;

  //yaw_error_bucket
  double yaw_error_bucket = 0;
  double yaw_error_bucket_leak = 0.3;
  double yaw_error_bucket_limit = 15;
  double yaw_error_bucket_max = 20;
  //diferential thrust limits
  float dive_diff_thrust_limit = 300;
  float max_rpm = 1000;
  int thruster_counter = 0;
  int thruster_publish_interval = 5;
  //Yaw actuation smoothing
  double yaw_actuation_filtered = 0;
  double yaw_actuation_filter_setting = 1.0/30.0;
  double differential_thrust_gain = 0;

  //Feedback Odom
  nav_msgs::msg::Odometry robot_position;
  rclcpp::Time odom_received_time;
  //Feedback Altitude
  float altitude_fb = 0;
  rclcpp::Time altitude_fb_received_time;

  //Output values
  float steering_actuation;
  float pitch_actuation;
  float roll_actuation;
  float thruster_actuation;


  //============= Subscribers & publishers ============
  //Setpoints
  rclcpp::Subscription<geometry_msgs::msg::PointStamped>::SharedPtr subscription_cmd_wp;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_yaw;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_yawrate;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_roll;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_altitude;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_depth;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_pitch;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_speed;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_cmd_rpm;
  //Feedback
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_fb_odom;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_fb_altitude;
  //Publishers
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_elevator;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_rudder;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_elevon_port;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_elevon_strb;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_thruster_port;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_thruster_strb;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_vertical_thruster_front_port;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_vertical_thruster_front_strb;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_vertical_thruster_back_port;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_vertical_thruster_back_strb;

  //Timer
  rclcpp::TimerBase::SharedPtr timer_;

  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  std::string target_frame_ = "lolo/odom";


  std::mutex mutex_; //Only one thread is allowed to access variables at a time

  //PID regulators
  PID pid_yaw;
  PID pid_yaw_rate;
  PID pid_roll;
  PID pid_depth;
  PID pid_pitch;
  PID pid_speed;

  //Diagnostic updater
  diagnostic_updater::Updater updater_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Lolocontrol>());
  rclcpp::shutdown();
  return 0;
}