#include "rclcpp/rclcpp.hpp"
#include "rclcpp/executors.hpp"
#include "nav_msgs/srv/get_plan.hpp"
#include "nav_msgs/srv/get_map.hpp"
#include "nav_msgs/srv/set_map.hpp"
#include "path_planner_base.h"
#include "dubins_planner.h"

#include <functional>
#include <memory>

using std::placeholders::_1;
using std::placeholders::_2;


int main(int argc, char **argv)
{

    //Create pathplanner object
    //PathPlanner path_planner;
    DubinsPlanner path_planner(10);
    rclcpp::init(argc, argv);

    std::shared_ptr<rclcpp::Node> node = rclcpp::Node::make_shared("lolo_2d_path_planner");
    
    rclcpp::Service<nav_msgs::srv::GetPlan>::SharedPtr plan_path_service =
    node->create_service<nav_msgs::srv::GetPlan>("plan_path",
        std::bind(&PathPlanner::plan_path_callback, &path_planner, _1, _2));

    rclcpp::Service<nav_msgs::srv::SetMap>::SharedPtr set_map_service =
    node->create_service<nav_msgs::srv::SetMap>("set_map",
        std::bind(&PathPlanner::set_map_callback, &path_planner, _1, _2));

    rclcpp::Service<nav_msgs::srv::GetMap>::SharedPtr get_map_service =
    node->create_service<nav_msgs::srv::GetMap>("get_map",
        std::bind(&PathPlanner::get_map_callback, &path_planner, _1, _2));
    
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Ready to plan a path");
    

    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);
    executor.spin();
    rclcpp::shutdown();
}