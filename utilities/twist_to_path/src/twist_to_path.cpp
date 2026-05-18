/**
 * @author Niklas Rolleberg
 * @author_email nrol@kth.se
 */
#include <iostream>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/header.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "nav_msgs/msg/path.hpp"
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

class TwistToPath : public rclcpp::Node {
 public:
    TwistToPath() : Node("TwistToPath") {

    //Parameters
    this->declare_parameter("subscribe_topic", "subscribe_topic");
    this->declare_parameter("publish_topic", "publish_topic");
    this->declare_parameter("integration_time", 10.0); //s
    this->declare_parameter("integration_dt", 0.5); //s

    std::string subscribe_topic = this->get_parameter("subscribe_topic").as_string();
    std::string publish_topic = this->get_parameter("publish_topic").as_string();
    integration_time = this->get_parameter("integration_time").as_double();
    integration_dt = this->get_parameter("integration_dt").as_double();

    //Subscriber
    _twistStamped_sub = this->create_subscription<geometry_msgs::msg::TwistStamped>(
      subscribe_topic, 10, std::bind(&TwistToPath::twist_callback, this, std::placeholders::_1)
    );

    //output pub
    _path_pub = this->create_publisher<nav_msgs::msg::Path>(publish_topic, 10);
  }

 private:

  // Parameters
  float integration_time;
  float integration_dt;

  // Subscriber
  rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr _twistStamped_sub;

  // Publisher
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr _path_pub;

  // -----------------------------------------------------------------------
  void twist_callback(const geometry_msgs::msg::TwistStamped msg) {
    std::cout << "Twist callback \n";

    //Add header for path
    nav_msgs::msg::Path path;
    path.header.frame_id = msg.header.frame_id;
    path.header.stamp = msg.header.stamp;

    // Time to increment header each integation step
    rclcpp::Duration dt_duration = rclcpp::Duration::from_seconds(integration_dt);

    //initial position is always 0
    geometry_msgs::msg::PoseStamped start_pose;
    start_pose.header = msg.header;

    //Add start point to the path
    path.poses.push_back(start_pose);

    //Linear velocity
    tf2::Vector3 v_body(
          msg.twist.linear.x,
          msg.twist.linear.y,
          msg.twist.linear.z);
    
    // quaternoin to rotate with
    tf2::Quaternion omega_q(
          msg.twist.angular.x,
          msg.twist.angular.y,
          msg.twist.angular.z,
          0.0);
    
    geometry_msgs::msg::PoseStamped current_pose = start_pose;

    for(float t = 0; t < integration_time; t += integration_dt) {
      
      // Convert orientation to tf2 quaternion
      tf2::Quaternion q;
      tf2::fromMsg(current_pose.pose.orientation, q);

      // Rotate linear velocity from body frame to current pose frame
      tf2::Vector3 v_pose = tf2::quatRotate(q, v_body);

      //Integrate position with linear speed
      current_pose.pose.position.x += v_pose.x() * integration_dt;
      current_pose.pose.position.y += v_pose.y() * integration_dt;
      current_pose.pose.position.z += v_pose.z() * integration_dt;

      // Update orientation
      tf2::Quaternion q_dot = q * omega_q;
      q_dot *= 0.5;

      // update orientation
      q += q_dot * integration_dt;
      q.normalize();
      current_pose.pose.orientation = tf2::toMsg(q);

      //Update time
      rclcpp::Time current_time(current_pose.header.stamp);
      current_time += dt_duration;
      current_pose.header.stamp = current_time;

      // Add new pose to path
      path.poses.push_back(current_pose);
    }

    _path_pub->publish(path);
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TwistToPath>());
  rclcpp::shutdown();
  return 0;
}
