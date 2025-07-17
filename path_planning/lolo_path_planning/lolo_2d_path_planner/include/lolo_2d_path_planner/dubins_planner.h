#ifndef DUBINSPLANNER_H
#define DUBINSPLANNER_H

// 2d path planner using dubins curves
// Algorithm translated to c++ from 
// https://github.com/smarc-project/smarc2/blob/humble/utilities/dubins_planner/dubins_planner/dubins.py
// and
// https://github.com/AndrewWalker/Dubins-Curves

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/srv/get_plan.hpp"
#include "path_planner_base.h"
#include <memory>
#include <cmath>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>


class DubinsPlanner : public PathPlanner {

    //Type of dubins curve
    enum TurnType {
        LSL,
        LSR,
        RSL,
        RSR,
        RLR,
        LRL
    };

    //Type of segment
    enum Segment {
        L_SEG,
        S_SEG,
        R_SEG
    };

    /* The segment types for each of the Path types */
    const Segment DIRDATA[6][3] = {
        { L_SEG, S_SEG, L_SEG },
        { L_SEG, S_SEG, R_SEG },
        { R_SEG, S_SEG, L_SEG },
        { R_SEG, S_SEG, R_SEG },
        { R_SEG, L_SEG, R_SEG },
        { L_SEG, R_SEG, L_SEG }
    };



    //Variables
    float turn_radius;


public:
    DubinsPlanner(float _turn_radius = 20) {
        turn_radius = _turn_radius;
    };

    void plan_path(const std::shared_ptr<nav_msgs::srv::GetPlan::Request> request,
            std::shared_ptr<nav_msgs::srv::GetPlan::Response> response) 
    {       
        geometry_msgs::msg::PoseStamped start = request->start;
        geometry_msgs::msg::PoseStamped goal = request->goal;
        double start_yaw = getYaw(start);
        double goal_yaw = getYaw(goal);

        // Calculate a dubins path between two waypoints
        float tz[] = {0, 0, 0, 0, 0, 0}; /* The translated initial configuration */ 
        float pz[] = {0, 0, 0, 0, 0, 0}; /* end-of segment 1 */
        float qz[] = {0, 0, 0, 0, 0, 0}; /* end-of segment 2 */

        float psi1 = std::fmod(start_yaw, M_PI); //[-PI, PI]
        float psi2 = std::fmod(goal_yaw, M_PI); //[-PI, PI]

        
        float dx = goal.pose.position.x - start.pose.position.x;
        float dy = goal.pose.position.y - start.pose.position.y;
        float D = sqrt(dx*dx + dy*dy);
        float d = D/turn_radius; // Normalize by turn radius

        float theta = unwrap_2pi(atan2(dy,dx)); // [0:2*PI]
        float alpha = unwrap_2pi(psi1 - theta); // [0:2*PI]
        float beta  = unwrap_2pi(psi2 - theta); // [0:2*PI]
        int best_index = -1;
        float lowest_cost = -1;
        float segment_times[] = {0,0,0}; //Contains time of each segment normalized by turn radius

        // Compute all Dubins paths between points
        dubinsLSL(alpha,beta,d, tz[0], pz[0], qz[0]);
        dubinsLSR(alpha,beta,d, tz[1], pz[1], qz[1]);
        dubinsRSL(alpha,beta,d, tz[2], pz[2], qz[2]);
        dubinsRSR(alpha,beta,d, tz[3], pz[3], qz[3]);
        dubinsRLR(alpha,beta,d, tz[4], pz[4], qz[4]);
        dubinsLRL(alpha,beta,d, tz[5], pz[5], qz[5]);

        //Pick the path with the lowest cost
        for(int k=0;k<6;k++) {
            if(tz[k]!=-1) { //Path exists?
                float time_cost = tz[k] + pz[k] + qz[k];
                float temp_segment_times[3] = {tz[k], pz[k], qz[k]};
                float stepsize = 1; //Course path for calculating cost
                float map_cost = create_dubins_path(start, goal, temp_segment_times, DIRDATA[k], stepsize, nullptr, true);
                RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Map cost %f", map_cost);
                if((time_cost+map_cost)<lowest_cost || lowest_cost==-1) {
                    best_index = k;
                    lowest_cost = time_cost+map_cost;
                    segment_times[0] = tz[k];
                    segment_times[1] = pz[k];
                    segment_times[2] = qz[k];
                }
            }
        }

        //Crete the final path
        float stepsize = 2;
        create_dubins_path(start, goal, segment_times, DIRDATA[best_index], stepsize, &response->plan, false);

    };
        


    // Compute all Dubins options
    void dubinsLSL(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp0      = d + sin(alpha) - sin(beta);
        float tmp1      = atan2((cos(beta)-cos(alpha)),tmp0);
        float p_squared = 2 + d*d - (2*cos(alpha-beta)) + (2*d*(sin(alpha)-sin(beta)));
        if (p_squared<0) {
            // print('No LSL Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            t = unwrap_2pi(tmp1-alpha); //[0:2*PI]
            p = sqrt(p_squared);
            q = unwrap_2pi(beta - tmp1); //[0:2*M_PI]
        }        
    };

    void dubinsRSR(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp0      = d - sin(alpha) + sin(beta);
        float tmp1      = atan2((cos(alpha)-cos(beta)),tmp0);
        float p_squared = 2 + d*d - (2*cos(alpha-beta)) + 2*d*(sin(beta)-sin(alpha));
        if(p_squared<0) {
            //# print('No RSR Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            t         = unwrap_2pi(alpha - tmp1); //[2*M_PI];
            p         = sqrt(p_squared);
            q         = unwrap_2pi(-1*beta + tmp1); //[2*M_PI];
        }
    };

    void dubinsRSL(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp0      = d - sin(alpha) - sin(beta);
        float p_squared = -2 + d*d + 2*cos(alpha-beta) - 2*d*(sin(alpha) + sin(beta));
        if (p_squared<0) {
            //# print('No RSL Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            p         = sqrt(p_squared);
            float tmp2      = atan2((cos(alpha)+cos(beta)),tmp0) - atan2(2,p);
            t         = unwrap_2pi(alpha - tmp2); //[0:2*M_PI]
            q         = unwrap_2pi(beta - tmp2); //[0:2*M_PI]
        }
        
    };

    void dubinsLSR(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp0      = d + sin(alpha) + sin(beta);
        float p_squared = -2 + d*d + 2*cos(alpha-beta) + 2*d*(sin(alpha) + sin(beta));
        if (p_squared<0) {
            //# print('No LSR Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            p         = sqrt(p_squared);
            float tmp2      = atan2((-1*cos(alpha)-cos(beta)),tmp0) - atan2(-2,p);
            t         = unwrap_2pi(tmp2 - alpha); //[0:2*pi]
            q         = unwrap_2pi(tmp2 - beta); //[0:2*pi]
        }
    
    };

    void dubinsRLR(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp_rlr = (6 - d*d + 2*cos(alpha-beta) + 2*d*(sin(alpha)-sin(beta)))/8.f;
        float phi  = atan2((cos(alpha)-cos(beta)), d-sin(alpha)+sin(beta));
        if(fabs(tmp_rlr)>1) {
            //# print('No RLR Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            p = unwrap_2pi(2*M_PI - acos(tmp_rlr)); //[0:2*pi]
            t = unwrap_2pi(alpha - phi + unwrap_2pi(p/2.f));
            q = unwrap_2pi(alpha - beta - t + p); //[0:2*PI]
        }
    };

    void dubinsLRL(float alpha, float beta, float d, float &t, float &p, float &q) {
        float tmp_lrl = (6 - d*d + 2*cos(alpha-beta) + 2*d*(-1*sin(alpha)+sin(beta)))/8.f;
        double phi = atan2((cos(alpha)-cos(beta)), d+sin(alpha)-sin(beta));
        if(fabs(tmp_lrl)>1) {
            //# print('No LRL Path')
            p=-1;
            q=-1;
            t=-1;
        }
        else {
            p = unwrap_2pi(2*M_PI - acos(tmp_lrl)); //[0:2*PI]
            t = unwrap_2pi(-1*alpha - phi  + p/2); // [0:2*pi]
            q = unwrap_2pi(unwrap_2pi(beta)-alpha-t+(p)); //[0:2*PI]
        }
    };

    float create_dubins_path(geometry_msgs::msg::PoseStamped &start, geometry_msgs::msg::PoseStamped &goal, float segment_times[3], const Segment segment_types[3], float stepsize, nav_msgs::msg::Path* path, bool calcualteMapCost) {
        
        float map_cost = 0;

        //Add header for path
        if(path != nullptr) {
            path->header = start.header;
            path->poses.push_back(start);
        }
        
        float start_yaw = getYaw(start);


        //Calculate intermediate points (reduces integration errors)
        geometry_msgs::msg::PoseStamped mid1 = dubins_segment(segment_times[0], start_yaw, segment_types[0]);
        mid1.pose.position.x = start.pose.position.x + (mid1.pose.position.x * turn_radius);
        mid1.pose.position.y = start.pose.position.y + (mid1.pose.position.y * turn_radius);
        mid1.pose.position.z = start.pose.position.z;
        float mid1_yaw = getYaw(mid1);
    
        geometry_msgs::msg::PoseStamped mid2 = dubins_segment(segment_times[1], mid1_yaw, segment_types[1]);
        mid2.pose.position.x = mid1.pose.position.x + (mid2.pose.position.x * turn_radius);
        mid2.pose.position.y = mid1.pose.position.y + (mid2.pose.position.y * turn_radius);
        mid2.pose.position.z = mid1.pose.position.z;
        float mid2_yaw = getYaw(mid2);

        float length = (segment_times[0]+segment_times[1]+segment_times[2])*turn_radius;
        //RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Length of path %f", length);
        float x = 0;
        while (x < length) {
   
            float tprime = x/turn_radius;            
            
            geometry_msgs::msg::PoseStamped next_pos;
            if(tprime<segment_times[0]) {
                next_pos = dubins_segment(tprime,start_yaw,segment_types[0]);
                next_pos.pose.position.x = start.pose.position.x + (next_pos.pose.position.x * turn_radius);
                next_pos.pose.position.y = start.pose.position.y + (next_pos.pose.position.y * turn_radius);
                next_pos.pose.position.z = start.pose.position.z;
            }
            else if(tprime<(segment_times[0]+segment_times[1])) {
                next_pos = dubins_segment(tprime-segment_times[0], mid1_yaw, segment_types[1]);
                next_pos.pose.position.x = mid1.pose.position.x + (next_pos.pose.position.x * turn_radius);
                next_pos.pose.position.y = mid1.pose.position.y + (next_pos.pose.position.y * turn_radius);
                next_pos.pose.position.z = mid1.pose.position.z;
            }
            else {
                next_pos = dubins_segment(tprime-segment_times[0]-segment_times[1], mid2_yaw, segment_types[2]);
                next_pos.pose.position.x = mid2.pose.position.x + (next_pos.pose.position.x * turn_radius);
                next_pos.pose.position.y = mid2.pose.position.y + (next_pos.pose.position.y * turn_radius);
                next_pos.pose.position.z = mid2.pose.position.z;
            }
            
            //set header
            next_pos.header = start.header;
            next_pos.header.stamp.sec += x; //Increase timestamp
            x += stepsize;

            //Add pose to path
            if(path != nullptr) {
                path->poses.push_back(next_pos);
            }
            

            if(calcualteMapCost) {
                map_cost += calculate_map_cost(next_pos);
            }
        }

        //Add goal as last wp
        if(path != nullptr) {
            path->poses.push_back(goal);  
        }
        
        
        //TODO return map cost
        return map_cost;
    }

    geometry_msgs::msg::PoseStamped dubins_segment(double dt, float start_yaw, Segment type)
    {
        geometry_msgs::msg::PoseStamped next_pos = geometry_msgs::msg::PoseStamped();
        float next_pose_yaw;
        
        //unit vector in the start direction
        double nx = cos(start_yaw);
        double ny = sin(start_yaw);

        //Left turn
        if( type == Segment::L_SEG ) {
            next_pose_yaw = start_yaw + dt;
            next_pos.pose.position.x = -ny + sin(next_pose_yaw);
            next_pos.pose.position.y = nx -cos(next_pose_yaw);
            
        }
        //Right turn
        else if( type == Segment::R_SEG ) {
            next_pose_yaw = start_yaw - dt;
            next_pos.pose.position.x = ny -sin(next_pose_yaw);
            next_pos.pose.position.y = -nx + cos(next_pose_yaw);
        }
        else if( type == Segment::S_SEG ) {
            next_pos.pose.position.x = nx * dt;
            next_pos.pose.position.y = ny * dt;
            next_pose_yaw = start_yaw;
        }
        setYaw(next_pos, next_pose_yaw);
        return next_pos;
    }

    float getYaw(geometry_msgs::msg::PoseStamped &pos) {
        //Calculate yaw from quaternion
        double roll, pitch, yaw;
        tf2::Quaternion q1(
            pos.pose.orientation.x,
            pos.pose.orientation.y,
            pos.pose.orientation.z,
            pos.pose.orientation.w);
        tf2::Matrix3x3 m1(q1);
        m1.getRPY(roll, pitch, yaw);
        return yaw;
    };

    void setYaw(geometry_msgs::msg::PoseStamped &pos, float yaw) {
        tf2::Quaternion quaternion_;
        quaternion_.setRPY(0,0,yaw);
        quaternion_ = quaternion_.normalize();
        pos.pose.orientation.x = quaternion_.x();
        pos.pose.orientation.y = quaternion_.y();
        pos.pose.orientation.z = quaternion_.z();
        pos.pose.orientation.w = quaternion_.w();
    };

    float unwrap_2pi(float x) {
        if(!(x==x) || std::isnan(x) || std::isinf(x)) {return 0;}
        uint8_t i = 1;
        while (x < 0.0 && i++ != 0){ x = x + 2*M_PI; }
        while (x > 2.0*M_PI && i++ != 0) { x = x - 2.0*M_PI; }
        return x;
    }

};

#endif //DUBINSPLANNER_H