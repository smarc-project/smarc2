#include "rclcpp/rclcpp.hpp"
#include <std_msgs/msg/float64.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Transform.h>
#include "rclcpp/executors/multi_threaded_executor.hpp"
#include "dead_reckoning_msgs/msg/topics.hpp"
#include "smarc_msgs/msg/dvl.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "sam_msgs/msg/topics.hpp"

using std::placeholders::_1;

class Odom_listener{

  public:
    rclcpp::Node *nh_;
    rclcpp::TimerBase::SharedPtr timer;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_pitch;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_roll;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_yaw;

    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_x;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_y;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_u;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_v;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_w;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_p;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_q;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feedback_r;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr feddback_alt;

    rclcpp::Subscription<smarc_msgs::msg::DVL>::SharedPtr dvl_sub;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub;
    std_msgs::msg::Float64 current_roll, current_pitch, current_yaw, current_depth, current_x, current_y, current_u, current_v, current_w, current_p, current_q, current_r, current_alt;
    double r,p,y;
    tf2::Quaternion tfq;
    Odom_listener(rclcpp::Node &nh) : nh_(&nh)
    {
      dvl_sub = nh_->create_subscription<smarc_msgs::msg::DVL>(
        sam_msgs::msg::Topics::DVL_TOPIC,
        10,
        std::bind(&Odom_listener::DVLCallback, this, _1)
      );
      odom_sub = nh_->create_subscription<nav_msgs::msg::Odometry>(
        dead_reckoning_msgs::msg::Topics::DR_ODOM_TOPIC,
        10,
        std::bind(&Odom_listener::OdomCallback, this, _1)
      );

        auto timer_callback = std::bind(&Odom_listener::publish_feedback, this);
      timer = nh_->create_wall_timer(std::chrono::milliseconds((int)(100)), timer_callback);

    feedback_pitch = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_PITCH_TOPIC, 10);
    feedback_roll = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ROLL_TOPIC, 10);
    feedback_yaw = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_YAW_TOPIC, 10);
    feedback_x = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_X_TOPIC, 10);
    feedback_y = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_Y_TOPIC, 10);
    feedback_u = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_U_TOPIC, 10);
    feedback_v = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_V_TOPIC, 10);
    feedback_w = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_W_TOPIC, 10);
    feedback_p = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_P_TOPIC, 10);
    feedback_q = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_Q_TOPIC, 10);
    feedback_r = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_R_TOPIC, 10);
    feddback_alt = nh_->create_publisher<std_msgs::msg::Float64>(dead_reckoning_msgs::msg::Topics::DR_ODOM_ALT_TOPIC, 10);

    }
    void DVLCallback(const smarc_msgs::msg::DVL::SharedPtr dvl_msg)
    {
        current_alt.data = dvl_msg->altitude;
    }
    
      void OdomCallback(const nav_msgs::msg::Odometry::SharedPtr odom_msg)
    {
        tf2::fromMsg(odom_msg->pose.pose.orientation, tfq);
    
        tf2::Matrix3x3(tfq).getEulerYPR(y,p,r);
        //orientation
        current_pitch.data= p;
        current_roll.data= r;
        current_yaw.data= y;
        current_x.data= odom_msg->pose.pose.position.x;
        current_y.data= odom_msg->pose.pose.position.y;
    
        //Velocity
        current_u.data= odom_msg->twist.twist.linear.x;
        current_v.data= odom_msg->twist.twist.linear.y;
        current_w.data= odom_msg->twist.twist.linear.z;
        current_p.data= odom_msg->twist.twist.angular.x;
        current_q.data= odom_msg->twist.twist.angular.y;
        current_r.data= odom_msg->twist.twist.angular.z;

    }
        void publish_feedback(){
    // rclcpp::Rate rate(10.0);
    if(rclcpp::ok())
    {
        feedback_pitch->publish(current_pitch);
        feedback_roll->publish(current_roll);
        feedback_yaw->publish(current_yaw);
        feedback_x->publish(current_x);
        feedback_y->publish(current_y);
        feedback_u->publish(current_u);
        feedback_v->publish(current_v);
        feedback_w->publish(current_w);
        feedback_p->publish(current_p);
        feedback_q->publish(current_q);
        feedback_r->publish(current_r);
        feddback_alt->publish(current_alt);
     }
    }
};


int main(int argc, char** argv){
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("Odom_listener");

  Odom_listener* odom_obj = new Odom_listener(*node);

  rclcpp::Rate loop_rate(10);
  while(rclcpp::ok())
  {
    rclcpp::spin_some(node);
    loop_rate.sleep();
  }

  delete odom_obj;
  RCLCPP_INFO(node->get_logger(), "odom listener finished");

  return 0;
}
