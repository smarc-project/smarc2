#ifndef DUBINSPLANNER_BASE_H
#define DUBINSPLANNER_BASE_H

// 2d path planner using dubins curves
// 

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/srv/get_plan.hpp"
#include "path_planner_base.h"
#include <memory>


class DubinsPlanner : public PathPlanner {

    float r1,r2;
public:
    DubinsPlanner(float _r1 = 20, float _r2= 15) {
        r1 = _r1;
        r2 = _r2;
    };

    void plan_path(const std::shared_ptr<nav_msgs::srv::GetPlan::Request> request,
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
        
        
        int steps = 20;
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
};

#endif //DUBINSPLANNER_BASE_H