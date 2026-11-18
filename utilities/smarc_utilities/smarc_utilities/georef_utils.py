#!/usr/bin/python3
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32

import math

def compute_course_from_two_poses(prev_pose: PoseStamped, current_pose: PoseStamped) -> Float32:
    """
    Computes the course from the previous and current poses.
    Returns the course in degrees (0-360).
    """
    if prev_pose is None or current_pose is None:
        return None
    dx = current_pose.pose.position.x - prev_pose.pose.position.x
    dy = current_pose.pose.position.y - prev_pose.pose.position.y
    course_rad = math.atan2(dy, dx)
    course_deg = math.degrees(course_rad) % 360.0
    return Float32(data=course_deg)

def compute_speed_from_two_poses(prev_pose: PoseStamped, current_pose: PoseStamped) -> Float32:
    """
    Computes the speed from the previous and current poses.
    Returns the speed in meters per second.
    """
    if prev_pose is None or current_pose is None:
        return None
    dx = current_pose.pose.position.x - prev_pose.pose.position.x
    dy = current_pose.pose.position.y - prev_pose.pose.position.y
    dt = (current_pose.header.stamp.sec + current_pose.header.stamp.nanosec * 1e-9) - \
         (prev_pose.header.stamp.sec + prev_pose.header.stamp.nanosec * 1e-9)
    speed = math.sqrt(dx**2 + dy**2) / dt if dt > 0 else 0.0
    return Float32(data=speed)
