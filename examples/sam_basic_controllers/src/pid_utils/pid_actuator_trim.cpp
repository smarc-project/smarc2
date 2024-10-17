// #include <ros/ros.h>
#include "rclcpp/rclcpp.hpp"
// #include <std_msgs/Float64.h>
#include "std_msgs/msg/float64.hpp"
// #include "sam_msgs/PercentStamped.h"
#include "smarc_msgs/msg/percent_stamped.hpp"
#include "std_msgs/msg/bool.hpp"

using std::placeholders::_1;

class PIDTrim{

  public:
    std::string topic_from_controller_, topic_to_actuator_, topic_from_plant_, setpoint_req_, setpoint_res_, setpoint_reached_;
    rclcpp::Node *nh_;
    // Gotta well-define it all in ros2 now.
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr     pid_action_sub, sp_sub, state_sub;

    // rclcpp::Publisher<sam_msgs::msg::PercentStamped>::SharedPtr control_action_pub;
    rclcpp::Publisher<smarc_msgs::msg::PercentStamped>::SharedPtr control_action_pub;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr        setpoint_pub;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr           sp_reached_pub_;

    double setpoint_, error_t_, setpoint_tolerance_, neutral_setpoint_, ff_term_;
    bool setpoint_rcv_;
    std_msgs::msg::Bool sp_reached_;

    PIDTrim(rclcpp::Node &nh) : nh_(&nh)
    {
      // First declare all params with a name and a default value.
      // Type inferred from default value
      // I'd make these string keys into enums... /Ozer
      nh_->declare_parameter("topic_from_controller", "control_action");
      nh_->declare_parameter("topic_to_actuator", "core/lcg_cmd");
      nh_->declare_parameter("topic_from_plant", "dr/pitch");
      nh_->declare_parameter("setpoint_req", "setpoint");
      nh_->declare_parameter("setpoint_res", "setpoint_pid");
      nh_->declare_parameter("setpoint_reached", "setpoint_reached");
      // Alternatively, declare a bunch at the same time if theyre all the same type
      // The first (empty) string is a namespace that can be added, which would make
      // the params "namespace.key" if that string is "namespace"
      nh_->declare_parameters<std::double_t>("", {
        {"setpoint_tolerance", 0.1},
        {"neutral_point", 0.1},
        {"ff_term", 0.1}
      });
      // Alternatively, define these in a yaml file instead!
      // No really, thats even cleaner than doing it here...

      // Then get them when needed like this:
      // auto x = nh_->get_parameter("topic_from_controller");

      setpoint_rcv_ = false;

      // initiate subscribers
      // pid_action_sub = nh_->subscribe(topic_from_controller_, 1, &PIDTrim::PIDCallback, this);
      pid_action_sub = nh_->create_subscription<std_msgs::msg::Float64>(
        nh_->get_parameter("topic_from_controller").as_string(),
        10, //Qos is different than "queue_size".
        std::bind(&PIDTrim::PIDCallback, this, _1)
        );

      // sp_sub = nh_->subscribe(setpoint_req_, 1, &PIDTrim::SetpointCallback, this);
      sp_sub = nh_->create_subscription<std_msgs::msg::Float64>(
        nh_->get_parameter("setpoint_req").as_string(),
        10,
        std::bind(&PIDTrim::SetpointCallback, this, _1)
      );

      // state_sub = nh_->subscribe(topic_from_plant_, 1, &PIDTrim::PlantCallback, this);
      state_sub = nh_->create_subscription<std_msgs::msg::Float64>(
        nh_->get_parameter("topic_from_plant").as_string(),
        10,
        std::bind(&PIDTrim::PlantCallback, this, _1)
      );

      // initiate publishers
      // control_action_pub = nh_->advertise<sam_msgs::PercentStamped>(topic_to_actuator_, 10);
      control_action_pub = nh_->create_publisher<smarc_msgs::msg::PercentStamped>(
        nh_->get_parameter("topic_to_actuator").as_string(),
        10
      );
      // setpoint_pub = nh_->advertise<std_msgs::Float64>(setpoint_res_, 10);
      setpoint_pub = nh_->create_publisher<std_msgs::msg::Float64>(
        nh_->get_parameter("setpoint_res").as_string(),
        10
      );
      // sp_reached_pub_ = nh_->advertise<std_msgs::Bool>(setpoint_reached_, 10, true);
      sp_reached_pub_ = nh_->create_publisher<std_msgs::msg::Bool>(
        nh_->get_parameter("setpoint_reached").as_string(),
        10
      );
    }

    // Gets setpoint from GUI
    void SetpointCallback(const std_msgs::msg::Float64 & setpoint)
    {
      setpoint_ = setpoint.data;
      setpoint_rcv_ = true;
      sp_reached_.data = false;
      sp_reached_pub_->publish(sp_reached_);
    }

    // Checks current error in the controller: if over tolerance, publish setpoint to PID. Else, stop PID
    // by not publishing setpoints anymore
    void PlantCallback(const std_msgs::msg::Float64 &plant_state)
    {
      if (setpoint_rcv_){
        if (fabs(setpoint_ - plant_state.data) > setpoint_tolerance_){
          std_msgs::msg::Float64 msg;
          msg.data = setpoint_;
          setpoint_pub->publish(msg);

        }
        else{
          RCLCPP_INFO(nh_->get_logger(), "Setpoint reached %f", plant_state.data);
          setpoint_rcv_ = false;

          // When the setpoint has been reached, set actuator to neutral to maintain position
          smarc_msgs::msg::PercentStamped control_action;
          control_action.value = neutral_setpoint_;
          control_action_pub->publish(control_action);

          sp_reached_.data = true;
          sp_reached_pub_->publish(sp_reached_);
        }
      }
    }

    // This one just republishes adding the feedforward term
    void PIDCallback(const std_msgs::msg::Float64 &control_msg)
    {
      smarc_msgs::msg::PercentStamped control_action;
      control_action.value = control_msg.data + ff_term_;
      control_action_pub->publish(control_action);
    }
};


int main(int argc, char** argv){
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("pid_actuator");

  PIDTrim* pid_obj = new PIDTrim(*node);

  rclcpp::Rate loop_rate(10);
  while(rclcpp::ok())
  {
    rclcpp::spin_some(node);
    loop_rate.sleep();
  }

  delete pid_obj;
  RCLCPP_INFO(node->get_logger(), "PID trim finished");

  return 0;
}
