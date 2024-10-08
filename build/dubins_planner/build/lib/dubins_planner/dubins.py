#!/usr/bin/python3

"""
Compute Dubins path between waypoints
"""

import math
import numpy as np
from enum import Enum


class TurnType(Enum):
    LSL = 1
    LSR = 2
    RSL = 3
    RSR = 4
    RLR = 5
    LRL = 6

class Waypoint:
    def __init__(self, x, y, psi):
        self.x = x
        self.y = y
        self.psi = psi

    def __str__(self):
        return 'x: {x}, y: {y}, psi: {psi}'.format(x=self.x, y=self.y, psi=self.psi)

class Param:
    def __init__(self, p_init, seg_final, turn_radius,):
        self.p_init = p_init
        self.seg_final = seg_final
        self.turn_radius = turn_radius
        self.type = 0

class Trajectory:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def wrapTo180(angle):
    angle =  angle % 360
    angle = (angle + 360) % 360
    if (angle > 180):
        angle -= 360;
    return angle

def calc_dubins_path(wpt1, wpt2, turn_radius):
    # Calculate a dubins path between two waypoints
    param = Param(wpt1, 0, 0)
    tz        = [0, 0, 0, 0, 0, 0]
    pz        = [0, 0, 0, 0, 0, 0]
    qz        = [0, 0, 0, 0, 0, 0]
    param.seg_final = [0, 0, 0]
    psi1 = wrapTo180(wpt1.psi)*math.pi/180
    psi2 = wrapTo180(wpt2.psi)*math.pi/180

    param.turn_radius = turn_radius
    dx = wpt2.x - wpt1.x
    dy = wpt2.y - wpt1.y
    D = math.sqrt(dx*dx + dy*dy)
    d = D/param.turn_radius # Normalize by turn radius

    theta = math.atan2(dy,dx) % (2*math.pi)
    alpha = (psi1 - theta) % (2*math.pi)
    beta  = (psi2 - theta) % (2*math.pi)
    best_word = -1
    lowest_cost = -1

    # Compute all Dubins paths between points
    tz[0], pz[0], qz[0] = dubinsLSL(alpha,beta,d)
    tz[1], pz[1], qz[1] = dubinsLSR(alpha,beta,d)
    tz[2], pz[2], qz[2] = dubinsRSL(alpha,beta,d)
    tz[3], pz[3], qz[3] = dubinsRSR(alpha,beta,d)
    tz[4], pz[4], qz[4] = dubinsRLR(alpha,beta,d)
    tz[5], pz[5], qz[5] = dubinsLRL(alpha,beta,d)

    # Pick the path with the lowest cost
    for k in range(len(tz)):
        if(tz[k]!=-1):
            cost = tz[k] + pz[k] + qz[k]
            if(cost<lowest_cost or lowest_cost==-1):
                best_word = k+1
                lowest_cost = cost
                param.seg_final = [tz[k],pz[k],qz[k]]

    param.type = TurnType(best_word)
    return param

# Compute all Dubins options
def dubinsLSL(alpha, beta, d):
    tmp0      = d + math.sin(alpha) - math.sin(beta)
    tmp1      = math.atan2((math.cos(beta)-math.cos(alpha)),tmp0)
    p_squared = 2 + d*d - (2*math.cos(alpha-beta)) + (2*d*(math.sin(alpha)-math.sin(beta)))
    if p_squared<0:
        # print('No LSL Path')
        p=-1
        q=-1
        t=-1
    else:
        t         = (tmp1-alpha) % (2*math.pi)
        p         = math.sqrt(p_squared)
        q         = (beta - tmp1) % (2*math.pi)
    return t, p, q

def dubinsRSR(alpha, beta, d):
    tmp0      = d - math.sin(alpha) + math.sin(beta)
    tmp1      = math.atan2((math.cos(alpha)-math.cos(beta)),tmp0)
    p_squared = 2 + d*d - (2*math.cos(alpha-beta)) + 2*d*(math.sin(beta)-math.sin(alpha))
    if p_squared<0:
        # print('No RSR Path')
        p=-1
        q=-1
        t=-1
    else:
        t         = (alpha - tmp1 ) % (2*math.pi)
        p         = math.sqrt(p_squared)
        q         = (-1*beta + tmp1) % (2*math.pi)
    return t, p, q

def dubinsRSL(alpha,beta,d):
    tmp0      = d - math.sin(alpha) - math.sin(beta)
    p_squared = -2 + d*d + 2*math.cos(alpha-beta) - 2*d*(math.sin(alpha) + math.sin(beta))
    if p_squared<0:
        # print('No RSL Path')
        p=-1
        q=-1
        t=-1
    else:
        p         = math.sqrt(p_squared)
        tmp2      = math.atan2((math.cos(alpha)+math.cos(beta)),tmp0) - math.atan2(2,p)
        t         = (alpha - tmp2) % (2*math.pi)
        q         = (beta - tmp2) % (2*math.pi)
    return t, p, q

def dubinsLSR(alpha, beta, d):
    tmp0      = d + math.sin(alpha) + math.sin(beta)
    p_squared = -2 + d*d + 2*math.cos(alpha-beta) + 2*d*(math.sin(alpha) + math.sin(beta))
    if p_squared<0:
        # print('No LSR Path')
        p=-1
        q=-1
        t=-1
    else:
        p         = math.sqrt(p_squared)
        tmp2      = math.atan2((-1*math.cos(alpha)-math.cos(beta)),tmp0) - math.atan2(-2,p)
        t         = (tmp2 - alpha) % (2*math.pi)
        q         = (tmp2 - beta) % (2*math.pi)
    return t, p, q

def dubinsRLR(alpha, beta, d):
    tmp_rlr = (6 - d*d + 2*math.cos(alpha-beta) + 2*d*(math.sin(alpha)-math.sin(beta)))/8
    if(abs(tmp_rlr)>1):
        # print('No RLR Path')
        p=-1
        q=-1
        t=-1
    else:
        p = (2*math.pi - math.acos(tmp_rlr)) % (2*math.pi)
        t = (alpha - math.atan2((math.cos(alpha)-math.cos(beta)), d-math.sin(alpha)+math.sin(beta)) + p/2 % (2*math.pi)) % (2*math.pi)
        q = (alpha - beta - t + (p % (2*math.pi))) % (2*math.pi)

    return t, p, q

def dubinsLRL(alpha, beta, d):
    tmp_lrl = (6 - d*d + 2*math.cos(alpha-beta) + 2*d*(-1*math.sin(alpha)+math.sin(beta)))/8
    if(abs(tmp_lrl)>1):
        # print('No LRL Path')
        p=-1
        q=-1
        t=-1
    else:
        p = (2*math.pi - math.acos(tmp_lrl)) % (2*math.pi)
        t = (-1*alpha - math.atan2((math.cos(alpha)-math.cos(beta)), d+math.sin(alpha)-math.sin(beta)) + p/2) % (2*math.pi)
        q = ((beta % (2*math.pi))-alpha-t+(p % (2*math.pi))) % (2*math.pi)
        # print(t,p,q,beta,alpha)
    return t, p, q

# Build the trajectory from the lowest-cost path
def dubins_traj(param, step):
    x = 0
    length = (param.seg_final[0]+param.seg_final[1]+param.seg_final[2])*param.turn_radius
    path = []

    while x < length:
        path.append(dubins_path(param, x))
        x += step
    return np.array(path)

# Helper function for curve generation
def dubins_path(param, t):
    tprime = t/param.turn_radius
    p_init = np.array([0,0,wrapTo180(param.p_init.psi)*math.pi/180])
    #
    L_SEG = 1
    S_SEG = 2
    R_SEG = 3
    DIRDATA = np.array([[L_SEG,S_SEG,L_SEG],[L_SEG,S_SEG,R_SEG],[R_SEG,S_SEG,L_SEG],[R_SEG,S_SEG,R_SEG],[R_SEG,L_SEG,R_SEG],[L_SEG,R_SEG,L_SEG]])
    #
    types = DIRDATA[param.type.value-1][:]
    param1 = param.seg_final[0]
    param2 = param.seg_final[1]
    mid_pt1 = dubins_segment(param1,p_init,types[0])
    mid_pt2 = dubins_segment(param2,mid_pt1,types[1])

    if(tprime<param1):
        end_pt = dubins_segment(tprime,p_init,types[0])
    elif(tprime<(param1+param2)):
        end_pt = dubins_segment(tprime-param1,mid_pt1,types[1])
    else:
        end_pt = dubins_segment(tprime-param1-param2, mid_pt2, types[2])

    end_pt[0] = end_pt[0] * param.turn_radius + param.p_init.x
    end_pt[1] = end_pt[1] * param.turn_radius + param.p_init.y
    end_pt[2] = wrapTo180(math.degrees(end_pt[2] % (2*math.pi))) # [deg]

    return end_pt

def dubins_segment(seg_param, seg_init, seg_type):
    L_SEG = 1
    S_SEG = 2
    R_SEG = 3
    seg_end = np.array([0.0,0.0,0.0])
    if( seg_type == L_SEG ):
        seg_end[0] = seg_init[0] + math.sin(seg_init[2]+seg_param) - math.sin(seg_init[2])
        seg_end[1] = seg_init[1] - math.cos(seg_init[2]+seg_param) + math.cos(seg_init[2])
        seg_end[2] = seg_init[2] + seg_param
    elif( seg_type == R_SEG ):
        seg_end[0] = seg_init[0] - math.sin(seg_init[2]-seg_param) + math.sin(seg_init[2])
        seg_end[1] = seg_init[1] + math.cos(seg_init[2]-seg_param) - math.cos(seg_init[2])
        seg_end[2] = seg_init[2] - seg_param
    elif( seg_type == S_SEG ):
        seg_end[0] = seg_init[0] + math.cos(seg_init[2]) * seg_param
        seg_end[1] = seg_init[1] + math.sin(seg_init[2]) * seg_param
        seg_end[2] = seg_init[2]

    return seg_end

# Compute angles between waypoints and return list of Waypoints objects
# Waypoints in input only have [x,y] coordinates
def waypoints_with_yaw(waypoints):
    pts = waypoints
    angles = []
    Wptz = []
    for i in (range(len(pts))):
        if i != len(pts)-1:
            angle = math.degrees(math.atan2(pts[i+1,1] - pts[i,1], pts[i+1,0] - pts[i,0]))
        else:
            angle = math.degrees(math.atan2(pts[len(pts)-1,1] - pts[len(pts)-2,1], pts[len(pts)-1,0] - pts[len(pts)-2,0]))
        angles.append(angle)
        Wptz.append(Waypoint(pts[i,0], pts[i,1], angle))
    return Wptz, angles

def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=False, tangent_tol=1e-5):
    """ Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.

    :param circle_center: The (x, y) location of the circle center
    :param circle_radius: The radius of the circle
    :param pt1: The (x, y) location of the first point of the segment
    :param pt2: The (x, y) location of the second point of the segment
    :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
    :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
    :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.

    Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
    """

    (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx ** 2.0 + dy ** 2.0)**.5
    big_d = x1 * y2 - x2 * y1
    discriminant = circle_radius ** 2.0 * dr ** 2.0 - big_d ** 2.0

    if discriminant < 0:  # No intersection between circle and line
        return []
    else:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2.0,
                cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2.0)
            for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
        if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
            fraction_along_segment = [
                (xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
            intersections = [pt for pt, frac in zip(
                intersections, fraction_along_segment) if 0 <= frac <= 1]
        # If line is tangent to circle, return just one point (as both intersections have same location)
        if len(intersections) == 2 and abs(discriminant) <= tangent_tol:
            return [intersections[0]]
        else:
            return intersections



def sample_between_wps(wp_from, wp_to, turn_radius, step):
    path = dubins_traj(calc_dubins_path(wp_from, wp_to, turn_radius), step)
    # ignore the first and last points in the path, since
    # the first is wp_from and last is step-close to wp_to
    return path[1:-1]


def sample_complete_plan(waypoints, turn_radius, step):
    """
    Sample between each WP in the list of Waypoints and return
    one list of waypoints with all the in-betweens and another list
    of indices.
    The indices in the second list correspond to
    which of the sampled-point-waypoints came from the
    original input directly.    
    """
    complete_path = []
    original_wp_indices = []
    # waypoints = A B C D
    # sampled between it becomes
    # A ... B ... C ... D
    # each loop adds A ... to the complete path
    # at the end, add D to the complete path
    for i in range(len(waypoints)-1):
        next_wp = waypoints[i+1]
        curr_wp = waypoints[i]
        sampled = sample_between_wps(curr_wp, next_wp, turn_radius, step)
        original_wp_indices.append(len(complete_path))
        complete_path.append((curr_wp.x, curr_wp.y, curr_wp.psi))
        complete_path.extend(sampled)
        
    original_wp_indices.append(len(complete_path))
    last_wp = waypoints[-1]
    complete_path.append((last_wp.x, last_wp.y, last_wp.psi))

    return complete_path, original_wp_indices





# Left here for future reference. This logic should not be here
# but in whatever is using this file.
# KISS.

# def create_dubins_path(vehicle,
#                        waypoints,
#                        step,
#                        turning_radius):
#     """
#     Read the waypoints of a missionplan and sample dubins waypoints for it
#     :param vehicle: The vehicle object. Used if the first waypoint has a heading
#     :param step: How many meters to leave between each sampled point on the dubins path
#     :param turning_radius: Turning radius in meters of the vehicle.
#     :return [waypoints...]: List of MissionPlan.Waypoint objects.
#     """
#     def heading_to_yaw(a):
#         return (90-a)%360
#     def yaw_to_heading(b):
#         return (-(b-90))%360

#     RADTODEG = 360 / (math.pi * 2)
#     def directed_angle(v1,v2):
#         """
#         returns angle in a directed fashion, from v1 to v2, v1+angle = v2
#         negative value means v2 is closer if v1 rotates cw
#         """
#         x1,x2 = v1[0],v2[0]
#         y1,y2 = v1[1],v2[1]

#         dot = x1*x2 + y1*y2      # dot product
#         det = x1*y2 - y1*x2      # determinant
#         angle_diff = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)

#         return angle_diff

#     dubins_wp = []
#     # for each user-given WP, we want to compute
#     # a sample path between such that the path leads into the
#     # next WP in the heading that it wants
#     for wp_i in range(len(waypoints)):
#         wp_current = waypoints[wp_i]

#         # so this WP wants a specific heading on arrival
#         # then we need to dubins from the previous one
#         if wp_i == 0:
#             # if this is the first planned WP
#             # previous WP is the current pose of the vehicle
#             d_wp_prev = Waypoint(vehicle.position_utm[0],
#                                 vehicle.position_utm[1],
#                                 heading_to_yaw(vehicle.heading))
#         else:
#             wp_prev = waypoints[wp_i-1]
#             d_wp_prev = Waypoint(wp_prev.wp.pose.pose.position.x,
#                                  wp_prev.wp.pose.pose.position.y,
#                                  heading_to_yaw(wp_prev.wp.arrival_heading))

#         x = wp_current.wp.pose.pose.position.x
#         y = wp_current.wp.pose.pose.position.y
#         if not wp_current.wp.use_heading:
#             # this WP doesnt care about the heading
#             # so we calculate the heading according to
#             # the next wp if it exists, previous wp if it doesnt
#             if wp_i == len(waypoints)-1:
#                 # last WP, use the prev_wp for the heading
#                 px = d_wp_prev.x
#                 py = d_wp_prev.y
#                 a = directed_angle((1,0), (x-px, y-py)) * RADTODEG
#             else:
#                 # there should be a next wp
#                 wp_next = waypoints[wp_i+1]
#                 nx = wp_next.wp.pose.pose.position.x
#                 ny = wp_next.wp.pose.pose.position.y
#                 a = directed_angle((1,0), (nx-x, ny-y)) * RADTODEG
#             # we set the arrival heading here so that the same heading is
#             # used again for the next wp's paths if needed
#             wp_current.wp.arrival_heading = yaw_to_heading(a)

#         d_wp_current = Waypoint(x,y,heading_to_yaw(wp_current.wp.arrival_heading))

#         print("Dubins from {} to {}".format(d_wp_prev, d_wp_current))

#         # now we have the simple waypoints so we can sample between them
#         # this path does not include the original wps
#         path = sample_between_wps(d_wp_prev,
#                                   d_wp_current,
#                                   turning_radius,
#                                   step)

#         # and then we add these to the final list of waypoints
#         for i,p in enumerate(path):
#             # the ones we generated here are too simple
#             # the mission plan requires detailed WPs like the ones in the input
#             goto_wp = GotoWaypoint()
#             # the x,y of the sampled stuff comes from the plan
#             goto_wp.pose.pose.position.x = p[0]
#             goto_wp.pose.pose.position.y = p[1]
#             goto_wp.pose.header.frame_id = wp_current.wp.pose.header.frame_id
#             # the goal tolerance of the intermittent points should be a little less
#             # than the distance between each point
#             goto_wp.goal_tolerance = step*0.8
#             # the speed and similar props come from the target WP
#             goto_wp.z_control_mode = wp_current.wp.z_control_mode
#             goto_wp.travel_altitude = wp_current.wp.travel_altitude
#             goto_wp.travel_depth = wp_current.wp.travel_depth
#             goto_wp.speed_control_mode = wp_current.wp.speed_control_mode
#             goto_wp.travel_rpm = wp_current.wp.travel_rpm
#             goto_wp.travel_speed = wp_current.wp.travel_speed
#             # latlon we will ask the WP object to fill in later
#             # heading from the interpolated point
#             goto_wp.arrival_heading = p[2]
#             # name based on the target wp
#             goto_wp.name = "{}_{}".format(wp_current.wp.name, i)

            
#             wp = mission_plan.Waypoint(goto_waypoint= goto_wp,
#                                        source="dubins")
#             dubins_wp.append(wp)

#         # and finally add the current WP after having added the method to get to it
#         dubins_wp.append(wp_current)

#     # and finally finally we have a list of WPs with interpolated and planned WPs in between
#     return dubins_wp