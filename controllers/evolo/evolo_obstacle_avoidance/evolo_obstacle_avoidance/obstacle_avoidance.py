#! /usr/bin/env python3

import math
import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.time import Duration, Time
from std_msgs.msg import String, Float32
from geometry_msgs.msg import TwistStamped
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped, Polygon, Point, PolygonStamped
from visualization_msgs.msg import Marker, MarkerArray
from tf_transformations import euler_from_quaternion
from tf2_ros import Buffer, TransformException, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped

from transforms3d.euler import quat2euler, euler2quat

from evolo_msgs.msg import Topics as EvoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics
import json


class cbf_avoidance(Node):
    def __init__(self):
        super().__init__("cbf_avoidance")
        self.logger = self.get_logger()
        self.logger.info("CBF obstacle avoidance initiated!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"update rate: {self.update_rate}")
        self.robot_name = self.get_parameter("robot_name").value

        self.yaw_setpoint = None
        self.yaw_setpoint_time = None

        # Tf listener
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )

        # Odom sub
        self.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC , self.odom_cb, 1)

        # Requested control input sub
        self.yaw_des = 0.0
        self.agent_speed = 0.0
        self.requested_ctrl_topic = self.get_parameter("requested_ctrl_topic").value
        self.requested_ctrl_sub = self.create_subscription(Odometry, 
                                 f"{self.requested_ctrl_topic}", self.requested_ctrl_cb, 1)
        self.logger.info(f"Reciving requested control messages from /{self.robot_name}/{self.requested_ctrl_topic}")
        
        # Obstacle sub
        self.max_n_obst = 10
        self.last_time = 0
        self.n_obst = 0
        self.obst_list = np.zeros((self.max_n_obst, 3))
        self.obst_header = None
        self.obstacle_topic = self.get_parameter("obstacle_topic").value
        self.obstacle_sub = self.create_subscription(Odometry, 
                                 f"{self.obstacle_topic}", self.obstacle_cb, self.max_n_obst)
        self.logger.info(f"Reciving obstacle messages from /{self.robot_name}/{self.obstacle_topic}")

        # Output
        self.safe_ctrl_topic = self.get_parameter("safe_ctrl_topic").value
        self.safe_ctrl_pub = self.create_publisher(Odometry,
                                                f"{self.safe_ctrl_topic}", 1)
        self.logger.info(f"Sending ctrl messages to /{self.robot_name}/{self.safe_ctrl_topic}")

        # CBF halfplane publisher
        self.halfplane_length = 40.0
        self.halfplane_array = MarkerArray()
        self.halfplane_pub = self.create_publisher(MarkerArray, "rviz/cbfHalfplanes", self.max_n_obst)

        # Safe path publisher
        self.safe_steps = 30
        self.safe_dt = 0.5
        self.safe_path_pub = self.create_publisher(Path, "rviz/safe_path", 1)

        # CBF parameters
        self.is_sim = False
        self.agent_radius = 2.0
        self.p = 2.0 # Of the simulated P-controller
        self.max_yaw_diff = 20.0 # In [deg/s]
        self.max_yaw_diff = self.max_yaw_diff * np.pi / 180.0
        self.w_max = self.max_yaw_diff * self.p # In [rad/s]

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def declare_node_parameters(self):
        self.declare_parameter("update_rate", 1)
        self.declare_parameter("robot_name", "")
        self.declare_parameter("requested_ctrl_topic", "")
        self.declare_parameter("obstacle_topic", "")
        self.declare_parameter("safe_ctrl_topic", "")

    def odom_cb(self,msg : Odometry):
        """Get current heading."""
        _,_,self.yaw_current = quat2euler([msg.pose.pose.orientation.w,
                                            msg.pose.pose.orientation.x,
                                            msg.pose.pose.orientation.y,
                                            msg.pose.pose.orientation.z],
                                            axes='sxyz')

    def obstacle_cb(self, msg):
        """Callback when reciving a new obstacle."""
        # obs_time = msg.header.stamp.sec * int(1e9) + msg.header.stamp.nanosec
        # Check if from new time
        # if obs_time > self.last_time:
        #     self.last_time = obs_time
        #     self.n_obst = 0
        #     self.obst_header = msg.header

        # Add to obstacle list
        self.n_obst = 0
        self.obst_list[self.n_obst, 2] = msg.pose.covariance[0]

        pose_stamped = PoseStamped()
        pose_stamped.header = msg.header
        pose_stamped.pose = msg.pose.pose

        t = self._tf_buffer.lookup_transform(
                target_frame="base_footprint",
                source_frame=msg.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1),
            )
        tf_msg = do_transform_pose_stamped(pose_stamped, t)

        # if self.n_obst < self.max_n_obst:
        self.obst_list[self.n_obst, 0] = tf_msg.pose.position.x
        self.obst_list[self.n_obst, 1] = tf_msg.pose.position.y
        
        self.n_obst = 1
        self.logger.info(f"Recived obstacle x: {tf_msg.pose.position.x}, y: {tf_msg.pose.position.y}, r: {msg.pose.covariance[0]}")
        self.logger.info(f"From frame: {msg.header.frame_id}")

    def vec2_directed_angle(v1, v2):
        """
        # Author: Ozer Ozkahraman (ozkahramanozer@gmail.com)
        # Date: 2018-07-10

        returns the shortest angle from v1 to v2 in radians.
        v1 + angle = v2.

        positive value means ccw rotation from v1 to v2.
        negative value means cw.

        v1, v2 can be (N,2)
        """
        v1 = np.array(np.atleast_2d(v1))
        v2 = np.array(np.atleast_2d(v2))
        assert v1.shape == v2.shape

        x1s = v1[:,0]
        x2s = v2[:,0]
        y1s = v1[:,1]
        y2s = v2[:,1]

        dots = x1s*x2s + y1s*y2s
        dets = x1s*y2s - y1s*x2s

        angles = np.arctan2(dets,dots)

        N,_ = v1.shape
        if N == 1:
            return angles[0]
        else:
            return angles

    def requested_ctrl_cb(self, msg):
        """Callback when reciving a new desired yaw"""
        # Recive the message
        _,_,self.yaw_des = quat2euler([msg.pose.pose.orientation.w,
                                        msg.pose.pose.orientation.x,
                                        msg.pose.pose.orientation.y,
                                        msg.pose.pose.orientation.z],
                                        axes='sxyz')
        v1 = np.array([np.cos(self.yaw_current), np.sin(self.yaw_current)])
        v2 = np.array([np.cos(self.yaw_des), np.sin(self.yaw_des)])

        yaw_diff = self.vec2_directed_angle(v1, v2)
        yaw_diff = max(-self.max_yaw_diff, min(self.max_yaw_diff, yaw_diff))
        self.agent_speed = msg.twist.twist.linear.x

        # Approximate w_des by P-controller approximation
        w_des = yaw_diff * self.p

        # Apply the CBF
        w_safe = self.calc_safe_control(w_des)

        #  Calculate safe heading
        safe_diff = w_safe / self.p
        yaw_safe = self.yaw_current + safe_diff
        self.logger.info(f"Requested yaw = {self.yaw_des}, safe yaw = {yaw_safe}, having {self.n_obst} obstacles")
        self.logger.info(f"Requested quat: w {msg.pose.pose.orientation.w}, x {msg.pose.pose.orientation.x}, y {msg.pose.pose.orientation.y}, z {msg.pose.pose.orientation.z}")

        # Publish the safe control
        w, x, y, z = euler2quat(0.0, 0.0, yaw_safe, axes='sxyz')
        msg.pose.pose.orientation.w = w
        msg.pose.pose.orientation.x = x
        msg.pose.pose.orientation.y = y
        msg.pose.pose.orientation.z = z

        self.logger.info(f"     Safe quat: w {w}, x {x}, y {y}, z {z}")
        self.safe_ctrl_pub.publish(msg)
        self.extrapolate_path(w_safe)
    
    def calc_safe_control(self, w_des):
        """To handle multiple obstacles"""
        # Get the parameters
        x = [0.0, 0.0, 0.0, self.agent_speed]

        # Calculate references for the halfplane orientations
        w_safe = w_des
        max_u_diff = 0
        self.logger.info(f"Desired control: {w_des}")
        self.halfplane_array = MarkerArray()
        for i in range(self.n_obst):
            if i < self.max_n_obst:
                o = [self.obst_list[i, 0], self.obst_list[i, 1]]
                self.logger.info(f"Obstacle at x: {self.obst_list[i, 0]}, y: {self.obst_list[i, 1]}, r: {self.obst_list[i, 2]}")
                # TODO: Dynamic and smart mu
                mu = -1
                if o[1] < 0:
                    mu = 1
                self.th_mid = float(np.arctan2(x[1] - o[1], x[0] - o[0]))

                # Find optimal plane orientation for each obstacle
                u, _, h = self.part_circle_grid(w_des, i, mu)
                self.logger.info(f"Safe control: {u}")
                u_diff = np.abs(u - w_des)
                if u_diff > max_u_diff:
                    w_safe = u
                    max_u_diff = u_diff
                    self.h = h

        return w_safe

    def part_circle_grid(self, w_des, obst_i, mu, res=11, spread=0.4 * np.pi):
        """Perform a semi-circle grid optimization"""
        # Grid search
        dth = spread
        nth = res
        th_add = np.linspace(-dth, dth, nth)

        u_mid, opt_found, h_opt = self.calc_safe_u(w_des, obst_i, self.th_mid, mu)
        u_diff_th = float(np.abs(w_des - u_mid))
        u_opt_th = u_mid
        th_opt = self.th_mid

        if res > 1:
            for i in range(nth):
                th = self.th_mid + th_add[i]
                u, optimal, h_test = self.calc_safe_u(w_des, obst_i, th, mu)
                if optimal:
                    opt_found = True
                    if np.abs(w_des - u) < u_diff_th:
                        u_opt_th = u
                        u_diff_th = float(np.abs(w_des - u_opt_th))
                        h_opt = h_test
                        th_opt = th

        # Send polygon halfplane to rviz
        self.poly_from_point(obst_i, th_opt, mu)

        return u_opt_th, opt_found, h_opt

    def calc_safe_u(self, w_des, obst_i, th, mu):
        """For a single fixed plane and fixed turning direction, calculate safe u"""
        opt_type = True
        x = [0.0, 0.0, 0.0, self.agent_speed]
        o = [self.obst_list[obst_i, 0], self.obst_list[obst_i, 1], 0.0, 0.0]
        # Calculate abbreviations
        r_min = x[3] / self.w_max
        v_h = np.cos(th) * o[2] + np.sin(th) * o[3]
        if np.abs(v_h) < x[3]:
            gamma = np.arcsin(v_h / x[3])
        else:
            gamma = np.pi * 0.5
        beta = mu * (th - x[2]) - 0.5 * np.pi
        beta = ((gamma + np.pi) % (2 * np.pi)) - gamma

        # Calculate h, lfh and lgh
        lfh = np.cos(th) * (np.cos(x[2]) * x[3] - o[2])
        lfh += np.sin(th) * (np.sin(x[2]) * x[3] - o[3])
        lgh = 0

        h = np.cos(th) * (x[0] - o[0])
        h += np.sin(th) * (x[1] - o[1])
        h -= self.agent_radius + self.obst_list[obst_i, 2]

        # Check if plane is ok
        if h < 0:
            opt_type = False

        # If the distance is decreasing
        self.b = 0.0
        if lfh < 0:
            h -= r_min * (np.cos(gamma) - np.cos(beta))
            h -= r_min * (beta + gamma) * v_h / x[3]
            lgh += mu * r_min * (np.sin(beta) + v_h / x[3])

        u = 0

        # Check if plane is ok
        if h < 0:
            u = mu * self.w_max
            opt_type = False

        # If constraint not activated
        elif lfh + w_des * lgh >= -self.alpha(h):
            u = w_des

        # If constraint not possible
        elif lfh + mu * self.w_max * lgh < -self.alpha(h):
            u = mu * self.w_max
            opt_type = False

        # If optimal u exists
        else:
            if lfh < 0:
                u = (-self.alpha(h) - lfh) / lgh
            else:
                raise ValueError

        return u, opt_type, h

    def poly_from_point(self, obst_i, th_opt, mu):
        """Given the point and the direction, calculate the points of the halfplane"""

        # First find the middle point on the line (including safety distance)
        r = self.agent_radius + self.obst_list[obst_i, 2]
        x_mid = self.obst_list[obst_i, 0] + r * np.cos(th_opt)
        y_mid = self.obst_list[obst_i, 1] + r * np.sin(th_opt)

        # Then extend the line
        p1 = Point()
        p1.x = x_mid - self.halfplane_length * np.sin(th_opt)
        p1.y = y_mid + self.halfplane_length * np.cos(th_opt)
        p1.z = 0.0
        
        p2 = Point()
        p2.x = x_mid + self.halfplane_length * np.sin(th_opt)
        p2.y = y_mid - self.halfplane_length * np.cos(th_opt)
        p2.z = 0.0

        p3 = Point()
        p3.x = x_mid
        p3.y = y_mid
        p3.z = 0.0

        p4 = Point()
        p4.x = self.obst_list[obst_i, 0]
        p4.y = self.obst_list[obst_i, 1]
        p4.z = 0.0

        # Construct the message and publish

        hp = Marker()
        hp.header = self.obst_header

        hp.ns = "halfplanes"
        hp.id = obst_i
        hp.type = Marker.LINE_STRIP
        hp.action = Marker.ADD

        hp.scale.x = 0.15  # line width

        if mu > 0:
            hp.color.r = 0.0
            hp.color.g = 1.0
        else:
            hp.color.r = 1.0
            hp.color.g = 0.0
        hp.color.b = 0.0
        hp.color.a = 1.0

        hp.lifetime.sec = 1
        hp.lifetime.nanosec = 0

        hp.points.append(p1)
        hp.points.append(p2)
        hp.points.append(p3)
        hp.points.append(p4)

        self.halfplane_array.markers.append(hp)
        self.halfplane_pub.publish(self.halfplane_array)

    def extrapolate_path(self, ctrl):
        """Extrapolates the path given the given control"""
        if self.obst_header is not None:
            # Current pose in the agent's frame
            x = 0.0
            y = 0.0
            w = 0.0

            # Set up the message
            safe_path = Path()
            safe_path.header = self.obst_header
            p0 = PoseStamped()
            p0.header = self.obst_header
            p0.pose.position.x = x
            p0.pose.position.y = y
            safe_path.poses.append(p0)

            # Extrapolate path
            for _ in range(self.safe_steps):
                x += self.safe_dt * self.agent_speed * np.cos(w)
                y += self.safe_dt * self.agent_speed * np.sin(w)
                w += self.safe_dt * ctrl
                p = PoseStamped()
                p.header = self.obst_header
                p.pose.position.x = x
                p.pose.position.y = y
                safe_path.poses.append(p)

            self.safe_path_pub.publish(safe_path)

    def update(self):
        pass

    def alpha(self, x):
        """A very simple alpha function"""
        return x


def main(args=None, namespace=None):
    rclpy.init(args=args)
    control_node = cbf_avoidance()

    control_node.create_timer(1.0/control_node.update_rate, control_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(control_node)
    executor.spin()
