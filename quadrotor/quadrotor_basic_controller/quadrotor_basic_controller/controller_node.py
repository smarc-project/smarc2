import sys
import rclpy
from rclpy.node import Node
import numpy as np
from geodesy import utm
import time

import rclpy.time
from smarc_msgs.msg import ThrusterRPM, ThrusterFeedback
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Twist, Wrench

from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class ControllerNode(Node):
    def __init__(self) -> None:
        super().__init__('controller_node')

        # _w : world frame (Unity, y up)
        # _s : world frame (Taeyoung Lee, z down)
        # _a : body frame (Unity, y up)
        # _b : body frame (Taeyoung Lee, z down)

        # Measurements
        self.x_w = np.zeros(3)
        self.v_w = np.zeros(3)
        self.R_wa = np.zeros((3, 3))
        self.W_w = np.zeros(3)

        # Saved values
        self.t_prev = 0
        self.R_sb_d_prev = np.eye(3)
        self.W_d_b_prev = np.zeros(3)
        self.hold_control = True

        # Publishers
        self.prop1_cmd_pub = self.create_publisher(ThrusterRPM, '/prop1_cmd', 10)
        self.prop2_cmd_pub = self.create_publisher(ThrusterRPM, '/prop2_cmd', 10)
        self.prop3_cmd_pub = self.create_publisher(ThrusterRPM, '/prop3_cmd', 10)
        self.prop4_cmd_pub = self.create_publisher(ThrusterRPM, '/prop4_cmd', 10)

        self.prop1_cmd = ThrusterRPM()
        self.prop2_cmd = ThrusterRPM()
        self.prop3_cmd = ThrusterRPM()
        self.prop4_cmd = ThrusterRPM()

        # Subscribers
        #self.create_subscription(ThrusterFeedback, '/prop1_fb', self.fb_cb, 10)
        #self.create_subscription(ThrusterFeedback, '/prop2_fb', self.fb_cb, 10)
        #self.create_subscription(ThrusterFeedback, '/prop3_fb', self.fb_cb, 10)
        #self.create_subscription(ThrusterFeedback, '/prop4_fb', self.fb_cb, 10)

        self.create_subscription(NavSatFix, '/drone/gps', self.gps_cb, 10)
        self.create_subscription(Imu, '/drone/imu', self.imu_cb, 10)
        self.create_subscription(Twist, '/articulation_body/velocity', self.vel_cb, 10)

        self.pub = self.create_publisher(Wrench, '/drone/wrench', 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def publish_rpms(self, rpms) -> None:
        self.prop1_cmd.rpm = rpms[0]
        self.prop2_cmd.rpm = rpms[1]
        self.prop3_cmd.rpm = rpms[2]
        self.prop4_cmd.rpm = rpms[3]
        
        self.prop1_cmd_pub.publish(self.prop1_cmd)
        self.prop2_cmd_pub.publish(self.prop2_cmd)
        self.prop3_cmd_pub.publish(self.prop3_cmd)
        self.prop4_cmd_pub.publish(self.prop4_cmd)
    
    def fb_cb(self, msg: ThrusterFeedback) -> None:
        pass#self.get_logger().info(f"{msg.rpm}")

    def gps_cb(self, msg: NavSatFix) -> None:
        drone_utm = utm.fromLatLong(msg.latitude, msg.longitude)
        
        #if self.t_prev == 0:
        #    self.t_prev = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
        #else:
        #    t_now = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
        #    dt = t_now - self.t_prev
        #    self.t_prev = t_now
        #    self.v_w[0] = (drone_utm.easting - self.x_w[0])/dt
        #    self.v_w[1] = (drone_utm.northing - self.x_w[1])/dt
        #    self.v_w[2] = (msg.altitude - self.x_w[2])/dt
        #    self.hold_control = False
        #self.get_logger().info(f"v: {self.v_w}")
        
        self.x_w[0] = drone_utm.easting - 651301.133
        self.x_w[1] = drone_utm.northing - 6524094.583
        self.x_w[2] = msg.altitude - 3.8518
        #self.get_logger().info(f"x: {self.x_w}")
        self.hold_control = False

        #self.get_logger().info(f"Tra t: {msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9}")

    def imu_cb(self, msg: Imu) -> None:
        #if self.t_prev_ns == 0:
        #    self.t_prev_ns = msg.header.stamp.sec*1e9 + msg.header.stamp.nanosec
        #else:
        #    t_ns = msg.header.stamp.sec*1e9 + msg.header.stamp.nanosec
        #    dt = (t_ns - self.t_prev_ns)*1e-9
        #    self.t_prev_ns = t_ns
        #    self.v[0] = round(self.v[0] + msg.linear_acceleration.x*dt, 3)
        #    self.v[1] = round(self.v[1] + msg.linear_acceleration.y*dt, 3)
        #    self.v[2] = round(self.v[2] + msg.linear_acceleration.z*dt, 3)
        #self.get_logger().info(f"v: {self.v}")
        
        trying = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        self.R_wa = self._quat2mat((msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w))@trying.T
        self.get_logger().info(f"R: {self.R_wa}")
        
        self.W_w[0] = -msg.angular_velocity.y
        self.W_w[1] = msg.angular_velocity.x
        self.W_w[2] = msg.angular_velocity.z
        #self.get_logger().info(f"W: {self.W_w}")

        #self.get_logger().info(f"Rot t: {msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9}")

    def vel_cb(self, msg: Twist) -> None:
        self.v_w[0] = msg.linear.x
        self.v_w[1] = msg.linear.z
        self.v_w[2] = msg.linear.y

    def control_step(self, t: float, dt: float) -> np.ndarray:
        tf = self.tf_buffer.lookup_transform('sam0/base_link', 'utm', rclpy.time.Time(seconds=0)).transform
        self.get_logger().info(f"TF: {tf}")
        
        if self.hold_control:
            return np.zeros(4)
        
        # Parameters
        m = 4.34
        d = 0.315 #np.sqrt(2)*0.12 #np.sqrt(0.12**2 + 0.85**2)
        J = np.eye(3)*0.1
        c_tau_f = 8.004e-2
        g = 9.81
        e3 = np.array([0, 0, 1])

        # Gains
        kx = 16*m/10
        kv = 5.6*m/10
        kR = 8.81/10
        kW = 2.54/10

        # Rotation matrices
        R_ws = np.array([[0, 1, 0],
                         [1, 0, 0],
                         [0, 0, -1]])
        R_ab = R_ws
        R_sb = R_ws.T@self.R_wa@R_ab

        # Transformations
        x_s = R_ws.T@self.x_w
        v_s = R_ws.T@self.v_w
        W_b = R_sb.T@R_ws.T@self.W_w

        # Desired (in the {s} frame)
        #tf = 20
        x_d_s = lambda t: R_ws.T@np.array([0, 0, 1])#20*np.array([1 - np.cos(np.pi*t/self.tf), np.sin(np.pi*t/self.tf), 0]) + self.x0
        v_d_s = lambda t: np.zeros(3)#20*np.array([np.pi/self.tf*np.sin(np.pi*t/self.tf), np.pi/self.tf*np.cos(np.pi*t/self.tf), 0])
        a_d_s = lambda t: np.zeros(3)#20*np.array([np.pi**2/self.tf**2*np.cos(np.pi*t/self.tf), -np.pi**2/self.tf**2*np.sin(np.pi*t/self.tf), 0])
        b1d = np.array([1, 0, 0])
        
        # Errors
        ex = x_s-x_d_s(t)
        ev = v_s-v_d_s(t)

        pid = -kx*ex - kv*ev - m*g*e3 + m*a_d_s(t)
        b3d = -pid/np.linalg.norm(pid)
        b2d = np.cross(b3d, b1d)/np.linalg.norm(np.cross(b3d, b1d))
        R_sb_d = np.array([np.cross(b2d, b3d), b2d, b3d]).T

        W_d_b = self._vee(self._logm3(self.R_sb_d_prev.T@R_sb_d))/dt
        #W_d_b = compact_axis_angle_from_matrix(self.R_sb_d_prev.T@R_sb_d)/dt
        #self.get_logger().info(f"W_d_b: {W_d_b}")
        W_d_dot_b = (W_d_b - self.W_d_b_prev)/dt

        eR = 0.5*self._vee(R_sb_d.T@R_sb - R_sb.T@R_sb_d)
        eW = W_b - R_sb.T@R_sb_d@W_d_b

        f = np.dot(-pid, R_sb@e3)
        M = -kR*eR - kW*eW + np.cross(W_b, J@W_b) - J@(self._hat(W_b)@(R_sb.T@R_sb_d@W_d_b) - R_sb.T@R_sb_d@W_d_dot_b)

        self.R_sb_d_prev = R_sb_d
        self.W_d_b_prev = W_d_b

        wrench_b = np.array([M[0], M[1], M[2], 0, 0, -f])
        wrench_a = self._adjoint(R_ab.T, np.zeros(3)).T@wrench_b

        T = np.array([[1, 1, 1, 1], [d, 0, -d, 0], [0, -d, 0, d], [c_tau_f, -c_tau_f, c_tau_f, -c_tau_f]])
        F = np.linalg.inv(T)@np.array([wrench_a[5], wrench_a[0], wrench_a[1], wrench_a[2]])

        #pub_msg = Wrench()
        #pub_msg.torque.x = wrench_a[0]
        #pub_msg.torque.y = wrench_a[1]
        #pub_msg.torque.z = wrench_a[2]
        #pub_msg.force.x = wrench_a[3]
        #pub_msg.force.y = wrench_a[4]
        #pub_msg.force.z = wrench_a[5]
        #self.pub.publish(pub_msg)

        #return np.zeros(4)
        
        #self.get_logger().info(f"Errors: {np.round(ex, 3)}, {np.round(ev, 3)}, {np.round(eR, 3)}, {np.round(eW, 3)}")
        #self.get_logger().info(f"Wrench: {np.round(np.array([wrench_a[5], wrench_a[0], wrench_a[1], wrench_a[2]]), 3)} | F: {np.round(F, 3)}")
        #self.get_logger().info(f"{t}")
        #self.get_logger().info(f"{self.R_wa} {R_sb}")

        return F
    
    def _hat(self, v: np.ndarray) -> np.ndarray:
        return np.array([[0, -v[2], v[1]],
                         [v[2], 0, -v[0]],
                         [-v[1], v[0], 0]])
    
    def _vee(self, S: np.ndarray) -> np.ndarray:
        error = 1e-6
        assert S[0, 0] < error
        assert S[1, 1] < error
        assert S[2, 2] < error
        assert np.abs(S[1, 2] + S[2, 1]) < error
        assert np.abs(S[0, 2] + S[2, 0]) < error
        assert np.abs(S[0, 1] + S[1, 0]) < error
        return np.array([S[2, 1], S[0, 2], S[1, 0]])
    
    def _logm3(self, R: np.ndarray) -> np.ndarray:
        acosinput = (np.trace(R) - 1) / 2
        if acosinput >= 1:
            m_ret = np.zeros((3, 3))
        elif acosinput <= -1:
            if not self._near_zero(1 + R[2, 2]):
                omg = (1.0 / np.sqrt(2 * (1 + R[2, 2])))*np.array([R[0, 2], R[1, 2], 1 + R[2, 2]])
            elif not self._near_zero(1 + R[1, 1]):
                omg = (1.0 / np.sqrt(2 * (1 + R[1, 1])))*np.array([R[0, 1], 1 + R[1, 1], R[2, 1]])
            else:
                omg = (1.0 / np.sqrt(2 * (1 + R[0, 0])))*np.array([1 + R[0, 0], R[1, 0], R[2, 0]])
            m_ret = self._hat(np.pi * omg)
        else:
            theta = np.arccos(acosinput)
            m_ret = theta / 2 / np.sin(theta)*(R - R.T)
        #self.get_logger().info(f"R: {R}, Logm3: {m_ret}")
        return m_ret
    
    def _near_zero(self, val):
        return np.abs(val) < 1e-6
    
    def _adjoint(self, R: np.ndarray, p: np.ndarray) -> np.ndarray:
        return np.block([[R, np.zeros((3, 3))],
                         [self._hat(p)@R, R]])
    
    def _quat2mat(self, q: tuple):
        x, y, z, w = q
        Nq = w*w + x*x + y*y + z*z
        s = 2.0/Nq
        X = x*s
        Y = y*s
        Z = z*s
        wX = w*X; wY = w*Y; wZ = w*Z
        xX = x*X; xY = x*Y; xZ = x*Z
        yY = y*Y; yZ = y*Z; zZ = z*Z
        return np.array(
            [[ 1.0-(yY+zZ), xY-wZ, xZ+wY ],
            [ xY+wZ, 1.0-(xX+zZ), yZ-wX ],
            [ xZ-wY, yZ+wX, 1.0-(xX+yY) ]])

def controller():
    rclpy.init(args=sys.argv)
    node = ControllerNode()
    t0 = node.get_clock().now().nanoseconds*1e-9
    dt = 1/20

    def control_loop():
        t = node.get_clock().now().nanoseconds*1e-9 - t0
        #node.get_logger().info(f"t: {t}")
        #if t > node.tf:
        #    return
        F = node.control_step(t, dt)
        rpm2force = 5
        rpms = F*1000/rpm2force
        rpms = [int(rpm) for rpm in rpms]
        #node.get_logger().info(f"Setting RPMs to {rpms}")
        if np.sum(np.abs(rpms)) < 4*2**31:
            node.publish_rpms(rpms)

    node.create_timer(dt, control_loop)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

def test():
    rclpy.init(args=sys.argv)
    node = ControllerNode()

    rpm = 8000

    def loop():
        nonlocal rpm
        rpm = 10000 - rpm
        node.publish_rpms([rpm, rpm, rpm, rpm])
        #node.get_logger().info(f"Setting RPM to {rpm}")

    node.create_timer(0.5, loop)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    test()