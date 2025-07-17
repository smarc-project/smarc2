#ifndef PATHPLANNER_BASE_H
#define PATHPLANNER_BASE_H

// Base class for path planner with abstract methods for planning and checking if the path is valid

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/srv/get_plan.hpp"
#include "nav_msgs/srv/get_map.hpp"
#include "nav_msgs/srv/set_map.hpp"
#include "nav_msgs/msg/occupancy_grid.h"

#include <memory>


class PathPlanner {

protected:
    //Pathplanner map
    nav_msgs::msg::OccupancyGrid map;
    bool map_set = false;


public:
    PathPlanner() {};

    virtual void plan_path(const std::shared_ptr<nav_msgs::srv::GetPlan::Request> request,
            std::shared_ptr<nav_msgs::srv::GetPlan::Response> response) 
    {
        //plan a path between start and end point
        geometry_msgs::msg::PoseStamped start = request->start;
        geometry_msgs::msg::PoseStamped goal = request->goal;

        float dx = goal.pose.position.x - start.pose.position.x;
        float dy = goal.pose.position.y - start.pose.position.y;
        float dz = goal.pose.position.z - start.pose.position.z;
        
        //Add header for path
        response->plan.header = start.header;
        
        //Add start point to the path
        response->plan.poses.push_back(start);
        
        
        int steps = 10;
        for (int i=0;i<steps; i++) {
            geometry_msgs::msg::PoseStamped p;
            p.header = goal.header;
            p.pose.position.x = start.pose.position.x + i*(dx / steps);
            p.pose.position.y = start.pose.position.y + i*(dy / steps);
            p.pose.position.z = start.pose.position.z + i*(dz / steps);

            response->plan.poses.push_back(p);
        }
        
        
        //Add goal to path
        response->plan.poses.push_back(goal);
    }


    void plan_path_callback(const std::shared_ptr<nav_msgs::srv::GetPlan::Request> request,
            std::shared_ptr<nav_msgs::srv::GetPlan::Response> response)
    {
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Plan path callback");
        plan_path(request,response);
    }

    void set_map_callback(const std::shared_ptr<nav_msgs::srv::SetMap::Request> request,
            std::shared_ptr<nav_msgs::srv::SetMap::Response> response)
    {
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Set map callback");
        (void) request;
        //TODO delete old map
        
        //TODO save new map
        map.info = request->map.info;
        map.header = request->map.header;
        map.data = request->map.data;
        map_set = true;
        response->success = false;
    }

    void get_map_callback(const std::shared_ptr<nav_msgs::srv::GetMap::Request> request,
            std::shared_ptr<nav_msgs::srv::GetMap::Response> response)
    {
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Get map callback");
        (void) request;
        response->map = map;
    }

    // function for calculating cost of a point based on the map
    float calculate_map_cost(geometry_msgs::msg::PoseStamped &p) {
        
        
        //Map not set. cost = 0
        if(!map_set)
            return 0;

        //calculate coordinates for point in the map
        float x = p.pose.position.x - map.info.origin.position.x;
        float y = p.pose.position.y - map.info.origin.position.y;

        int col = (int) x;
        int row = (int) y;

        if(col >= 0 && col < map.info.width &&
           row >= 0 && row < map.info.height) {
            int map_value = map.data[row + col*map.info.width];
            if(map_value == -1) map_value = 0;
            return ((float) map_value) / 100;
        }
        //RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Error map index out of bounds (%d %d)", col, row);
        return 2;
    }
};

#endif //PATHPLANNER_BASE_H