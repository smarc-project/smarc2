#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2_ros/transform_listener.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "smarc_msgs/msg/topics.hpp"
#include "evolo_msgs/msg/topics.hpp"
#include "tf2_ros/buffer.h"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"
#include "visualization_msgs/msg/marker_array.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "evolo_obstacle_avoidance_simple_cpp/OdometryBuffer.hpp"

//using namespace std::chrono_literals;



class ObstacleAvoidanceNode : public rclcpp::Node
{
public:
  ObstacleAvoidanceNode() : Node("evolo_obstacle_avoidance")
  {

    // Declare parameters with default values
    this->declare_parameter<bool>("publish_viz", true);
    this->declare_parameter<float>("min_bearing_buffer", 10.0);
    this->declare_parameter<float>("max_bearing_buffer", 90.0);
    this->declare_parameter<float>("distance_threshold_outer", 50.0);
    this->declare_parameter<float>("distance_threshold_inner", 10.0);
    this->declare_parameter<float>("panic_distance", 10);

    publish_viz               = this->get_parameter("publish_viz").as_bool();
    min_bearing_buffer        = this->get_parameter("min_bearing_buffer").as_double();
    max_bearing_buffer        = this->get_parameter("max_bearing_buffer").as_double();
    distance_threshold_outer  = this->get_parameter("distance_threshold_outer").as_double();
    distance_threshold_inner  = this->get_parameter("distance_threshold_inner").as_double();
    panic_distance            = this->get_parameter("panic_distance").as_double();


    RCLCPP_INFO(this->get_logger(), "Parameters:");
    RCLCPP_INFO(this->get_logger(), "  publish_viz = %d", publish_viz);
    RCLCPP_INFO(this->get_logger(), "  min_bearing_buffer = %f", min_bearing_buffer);
    RCLCPP_INFO(this->get_logger(), "  max_bearing_buffer = %f", max_bearing_buffer);
    RCLCPP_INFO(this->get_logger(), "  distance_threshold_outer = %f", distance_threshold_outer);
    RCLCPP_INFO(this->get_logger(), "  distance_threshold_inner = %f", distance_threshold_inner);
    RCLCPP_INFO(this->get_logger(), "  panic_distance = %f", panic_distance);


    //Odometry buffer
    buffer_ = OdometryBuffer(100, rclcpp::Duration::from_seconds(5.0));

    //tf
    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    setpoint_publisher_ = this->create_publisher<nav_msgs::msg::Odometry>(evolo_msgs::msg::Topics::EVOLO_CONTROL_SETPOINT, 10);

    marker_publisher_ = this->create_publisher<visualization_msgs::msg::MarkerArray>("markers", 10);

    setpoint_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      evolo_msgs::msg::Topics::EVOLO_CONTROL_PLANNED, 10,
      std::bind(&ObstacleAvoidanceNode::setpoint_callback, this, std::placeholders::_1));

    robot_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      smarc_msgs::msg::Topics::ODOM_TOPIC, 10,
      std::bind(&ObstacleAvoidanceNode::robot_callback, this, std::placeholders::_1));

    obstacle_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      evolo_msgs::msg::Topics::EVOLO_CBF_OBSTACLES, 10,
      std::bind(&ObstacleAvoidanceNode::obstacle_callback, this, std::placeholders::_1));

    // Timer: fires every 5s
    timer_ = this->create_wall_timer(
      5000ms, std::bind(&ObstacleAvoidanceNode::timer_callback, this));

    RCLCPP_INFO(this->get_logger(), "Node started");
  }

private:

  //
  int unwrap_deg(int angle) {
    while(angle < 0) angle += 360;
    while(angle > 359) angle -= 360;
    return angle;
  }

  void timer_callback()
  {
    //Remove old entries from the obstacle buffer
    this->buffer_.update();
  }

  void robot_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
  {
    //RCLCPP_INFO(this->get_logger(), "Robot odom received");
    //TODO keep track of time
    robot_position = *msg;
  }

  void setpoint_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
  {
    //(1) Calculate yaw from setpoint
    tf2::Quaternion q(
      msg->pose.pose.orientation.x,
      msg->pose.pose.orientation.y,
      msg->pose.pose.orientation.z,
      msg->pose.pose.orientation.w);

    double roll_setpoint_rad, pitch_setpoint_rad, yaw_setpoint_rad, yaw_setpoint_deg;
    tf2::Matrix3x3(q).getRPY(roll_setpoint_rad, pitch_setpoint_rad, yaw_setpoint_rad);
    yaw_setpoint_deg = unwrap_deg(yaw_setpoint_rad*180.0 / M_PI);
    RCLCPP_INFO(this->get_logger(), "Yaw setpoint: %.2f", yaw_setpoint_deg);

    //(2) Calculate yaw robot odom
    tf2::Quaternion q_robot(
      robot_position.pose.pose.orientation.x,
      robot_position.pose.pose.orientation.y,
      robot_position.pose.pose.orientation.z,
      robot_position.pose.pose.orientation.w);

    double robot_roll, robot_pitch, robot_yaw_rad, robot_yaw_deg;
    tf2::Matrix3x3(q_robot).getRPY(robot_roll, robot_pitch, robot_yaw_rad);
    robot_yaw_deg = unwrap_deg(robot_yaw_rad*180.0 / M_PI);
    RCLCPP_INFO(this->get_logger(), "current_yaw: %.2f", robot_yaw_deg);

    //(3)Create bearing array
    int bearings[360] = {0};
    double closest_distance = 9999;
    
    //Loop through all obstacles and populate the bearing array
    for (const auto & entry : buffer_)
    {
      //Calcualte distance and bearing to obstacles
      double dx = entry.msg().pose.pose.position.x - robot_position.pose.pose.position.x;
      double dy = entry.msg().pose.pose.position.y - robot_position.pose.pose.position.y;
      double distance = sqrt(dx*dx + dy*dy);
      double bearing_rad = atan2(dy,dx);
      int bearing_deg = unwrap_deg(bearing_rad*180.0 / M_PI);
      if(distance < closest_distance) closest_distance = distance;

      if(distance < distance_threshold_outer) {
        float distance_inside_outer_radius = (distance_threshold_outer - distance); 
        float distance_to_inner_radius = std::max(0.f,(distance_threshold_outer - distance_inside_outer_radius) - distance_threshold_inner);
        float fraction = distance_to_inner_radius / (distance_threshold_outer - distance_threshold_inner);

        RCLCPP_INFO(this->get_logger(), "distance_inside_outer_radius: %.2f", distance_inside_outer_radius);
        RCLCPP_INFO(this->get_logger(), "distance_to_inner_radius: %.2f", distance_to_inner_radius);
        RCLCPP_INFO(this->get_logger(), "fraction: %.2f", fraction);

        int bearing_buffer = min_bearing_buffer + (1-fraction)*(max_bearing_buffer - min_bearing_buffer);
        RCLCPP_INFO(this->get_logger(), "bearing buffer: %d", bearing_buffer);
        for(int i=-bearing_buffer; i<bearing_buffer;i++) {
          int occupied_bearing = unwrap_deg(bearing_deg + i);
          bearings[occupied_bearing] = 1;
        }
      }
      
      std::cout << "ID: " << entry.child_frame_id()
                << "  x: " << entry.msg().pose.pose.position.x
                << "  y: " << entry.msg().pose.pose.position.y
                << " distance: " << distance
                << " bearing: " << bearing_deg
                << std::endl;
    } 

    //calculate prefered direction to turn
    int diff = unwrap_deg(yaw_setpoint_deg - robot_yaw_deg); //Does this work?
    if(diff > 180) diff -= 360; //-180 to 180
    int direction = (diff >= 0) ? 1 : -1;

    RCLCPP_INFO(this->get_logger(), "Angle to turn: %0.2f, direction: %d", (float) diff, direction);

    //calculate stuff
    int new_target_yaw_deg = robot_yaw_deg;
    bool possible_yaw_found = false;

    
    //Check if we need to turn to avoid an obstacle straight ahead
    if(bearings[(int) robot_yaw_deg] == 1) {
      RCLCPP_INFO(this->get_logger(), "Obstacle straight ahead");
      for(int i=1;i<180;i++) {
        int yaw_1 = unwrap_deg(robot_yaw_deg + i); 
        int yaw_2 = unwrap_deg(robot_yaw_deg - i); 

        if(bearings[yaw_1] == 0) {
          new_target_yaw_deg = yaw_1;
          possible_yaw_found = true;
          break;
        }

        if(bearings[yaw_2] == 0) {
          new_target_yaw_deg = yaw_2;
          possible_yaw_found = true;
          break;
        }
      }
    }
    else {
      possible_yaw_found = true;
    }

    if(possible_yaw_found) {
      RCLCPP_INFO(this->get_logger(), "Turn towards target heading %d, diff: %d", new_target_yaw_deg, diff);
      //Turn towards the target yaw until we either encounter a blocked bearing or we hit the target yaw
      int origial_new_yaw = new_target_yaw_deg;
      for (int i=0;i<abs(diff);i++) {
        int new_index = unwrap_deg(origial_new_yaw + i*direction);
        if(bearings[new_index] != 1) {
          new_target_yaw_deg = new_index; //Still OK
        }
        else break;
      }
    }

    //Output the new control setpoint
    tf2::Quaternion q2;

    //Check distance to closest obstacle
    if(panic_distance < panic_distance || !possible_yaw_found) {
      RCLCPP_INFO(this->get_logger(), "Panic distance or no new direction found");

      //No turning. Just stop
      q2.setRPY(roll_setpoint_rad, pitch_setpoint_rad, robot_yaw_rad);
      q2.normalize();
      msg->pose.pose.orientation.x = q2.x();
      msg->pose.pose.orientation.y = q2.y();
      msg->pose.pose.orientation.z = q2.z();
      msg->pose.pose.orientation.w = q2.w();
      //Speed 0
      msg->twist.twist.linear.x = 0; //Speed 0
    }
    else {
      //Adjust yaw
      q2.setRPY(roll_setpoint_rad, pitch_setpoint_rad, ((double) new_target_yaw_deg) * M_PI / 180.0);
      q2.normalize();
      msg->pose.pose.orientation.x = q2.x();
      msg->pose.pose.orientation.y = q2.y();
      msg->pose.pose.orientation.z = q2.z();
      msg->pose.pose.orientation.w = q2.w();
      RCLCPP_INFO(this->get_logger(), "New yaw: %d, old yaw %.2f", new_target_yaw_deg, yaw_setpoint_deg);
    }
    
    setpoint_publisher_->publish(*msg);
    RCLCPP_INFO(this->get_logger(), "Published setpoint\n");

    //Debug visualization
    if(publish_viz)
    {
      visualization_msgs::msg::MarkerArray marker_array;
      for(int i=0;i<360;i++) {
        visualization_msgs::msg::Marker marker;
        marker.header.frame_id = target_frame;
        marker.header.stamp = this->get_clock()->now();
        marker.ns = "angles";
        marker.id = i;
        marker.type = visualization_msgs::msg::Marker::SPHERE;
        marker.action = visualization_msgs::msg::Marker::ADD;

        marker.pose.position.x = robot_position.pose.pose.position.x + 10*cos(i*M_PI / 180.0);
        marker.pose.position.y = robot_position.pose.pose.position.y + 10*sin(i*M_PI / 180.0);
        marker.pose.position.z = 0.0;
        marker.pose.orientation.w = 1.0;

        marker.scale.x = 0.2;
        marker.scale.y = 0.2;
        marker.scale.z = 0.2;
        if(bearings[i] == 0) {
          marker.color.r = 0.0f;
          marker.color.g = 1.0f;
          marker.color.b = 0.0f;
          marker.color.a = 1.0f;
        }
        else {
          marker.color.r = 1.0f;
          marker.color.g = 0.0f;
          marker.color.b = 0.0f;
          marker.color.a = 1.0f;
        }

        marker.lifetime = rclcpp::Duration::from_seconds(1.0);

        marker_array.markers.push_back(marker); 
      }

      //arrow1 with current heading
      visualization_msgs::msg::Marker arrow1;
      arrow1.header.frame_id = target_frame;
      arrow1.header.stamp = this->get_clock()->now();
      arrow1.ns = "arrows";
      arrow1.id = 360;
      arrow1.type = visualization_msgs::msg::Marker::ARROW;
      arrow1.action = visualization_msgs::msg::Marker::ADD;

      arrow1.pose.position.x = robot_position.pose.pose.position.x;
      arrow1.pose.position.y = robot_position.pose.pose.position.y;
      arrow1.pose.position.z = 0.0;

      // Orientation determines the direction the arrow1 points
      tf2::Quaternion q_arrow1;
      q_arrow1.setRPY(0.0, 0.0, robot_yaw_rad);
      q_arrow1.normalize();
      arrow1.pose.orientation.x = q_arrow1.x();
      arrow1.pose.orientation.y = q_arrow1.y();
      arrow1.pose.orientation.z = q_arrow1.z();
      arrow1.pose.orientation.w = q_arrow1.w();

      // x = shaft length, y = shaft width, z = head width
      arrow1.scale.x = 4.0;
      arrow1.scale.y = 1.0;
      arrow1.scale.z = 2.0;

      arrow1.color.r = 0.0f;
      arrow1.color.g = 0.0f;
      arrow1.color.b = 1.0f;
      arrow1.color.a = 1.0f;
      arrow1.lifetime = rclcpp::Duration::from_seconds(1.0);
      marker_array.markers.push_back(arrow1);

      // arrow2 with target heading
      visualization_msgs::msg::Marker arrow2;
      arrow2.header.frame_id = target_frame;
      arrow2.header.stamp = this->get_clock()->now();
      arrow2.ns = "arrows";
      arrow2.id = 361;
      arrow2.type = visualization_msgs::msg::Marker::ARROW;
      arrow2.action = visualization_msgs::msg::Marker::ADD;

      arrow2.pose.position.x = robot_position.pose.pose.position.x;
      arrow2.pose.position.y = robot_position.pose.pose.position.y;
      arrow2.pose.position.z = 0.0;

      // Orientation determines the direction the arrow1 points
      tf2::Quaternion q_arrow2;
      q_arrow2.setRPY(0.0, 0.0, yaw_setpoint_rad);
      q_arrow2.normalize();
      arrow2.pose.orientation.x = q_arrow2.x();
      arrow2.pose.orientation.y = q_arrow2.y();
      arrow2.pose.orientation.z = q_arrow2.z();
      arrow2.pose.orientation.w = q_arrow2.w();

      // x = shaft length, y = shaft width, z = head width
      arrow2.scale.x = 5.0;
      arrow2.scale.y = 1.0;
      arrow2.scale.z = 2.0;

      arrow2.color.r = 1.0f;
      arrow2.color.g = 0.0f;
      arrow2.color.b = 0.0f;
      arrow2.color.a = 1.0f;
      arrow2.lifetime = rclcpp::Duration::from_seconds(1.0);
      marker_array.markers.push_back(arrow2);

      // arrow3 with new target heading
      visualization_msgs::msg::Marker arrow3;
      arrow3.header.frame_id = target_frame;
      arrow3.header.stamp = this->get_clock()->now();
      arrow3.ns = "arrows";
      arrow3.id = 362;
      arrow3.type = visualization_msgs::msg::Marker::ARROW;
      arrow3.action = visualization_msgs::msg::Marker::ADD;

      arrow3.pose.position.x = robot_position.pose.pose.position.x;
      arrow3.pose.position.y = robot_position.pose.pose.position.y;
      arrow3.pose.position.z = 0.0;

      // Orientation determines the direction the arrow1 points
      tf2::Quaternion q_arrow3;
      q_arrow3.setRPY(0.0, 0.0, new_target_yaw_deg * M_PI / 180.0);
      q_arrow3.normalize();
      arrow3.pose.orientation.x = q_arrow3.x();
      arrow3.pose.orientation.y = q_arrow3.y();
      arrow3.pose.orientation.z = q_arrow3.z();
      arrow3.pose.orientation.w = q_arrow3.w();

      // x = shaft length, y = shaft width, z = head width
      arrow3.scale.x = 6.0;
      arrow3.scale.y = 1.0;
      arrow3.scale.z = 2.0;

      arrow3.color.r = 0.0f;
      arrow3.color.g = 1.0f;
      arrow3.color.b = 0.0f;
      arrow3.color.a = 1.0f;
      arrow3.lifetime = rclcpp::Duration::from_seconds(1.0);
      marker_array.markers.push_back(arrow3);

      //Publish marker array
      marker_publisher_->publish(marker_array);
    }
  }

  void obstacle_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
  {
    //RCLCPP_INFO(this->get_logger(), "Received obstacle: x=%.2f y=%.2f",
    //  msg->pose.pose.position.x,
    //  msg->pose.pose.position.y);

    //Add obstacle to buffer

    //(1) change frame id if neeed
    if(msg->header.frame_id != this->target_frame)
    {
      try
      {
        geometry_msgs::msg::PoseStamped pose_in;
        pose_in.header = msg->header;
        pose_in.pose = msg->pose.pose;

        geometry_msgs::msg::PoseStamped pose_out;
        tf_buffer_->transform(pose_in, pose_out, this->target_frame);

        msg->header.frame_id = target_frame;
        msg->pose.pose = pose_out.pose;

        //RCLCPP_INFO(this->get_logger(), "Transformed obstacle to %s: x=%.2f y=%.2f from %s",
        //  target_frame.c_str(),
        //  msg->pose.pose.position.x,
        //  msg->pose.pose.position.y,
        //  pose_in.header.frame_id.c_str());
      }
      catch (const tf2::TransformException & ex)
      {
        RCLCPP_WARN(this->get_logger(), "Could not transform obstacle to map frame: %s", ex.what());
        return;
      }
    }

    //Add to buffer
    buffer_.add(*msg);
  }
  
  //Settings
  bool publish_viz = true;
  float min_bearing_buffer = 1; //+-1 deg at outer threshold distance
  float max_bearing_buffer = 90; //+-90 deg at inner threshold distance
  float distance_threshold_outer = 50; // distance to considering obstacles
  float distance_threshold_inner = 10; // distance where we have maximum avoidance
  float panic_distance = 4; // distance to obstacles where we put speed=0

  nav_msgs::msg::Odometry robot_position;
  std::string target_frame = "evolo/odom"; //rosparam for this?
  OdometryBuffer buffer_;
  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr setpoint_publisher_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_publisher_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr robot_subscription_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr setpoint_subscription_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr obstacle_subscription_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ObstacleAvoidanceNode>());
  rclcpp::shutdown();
  return 0;
}