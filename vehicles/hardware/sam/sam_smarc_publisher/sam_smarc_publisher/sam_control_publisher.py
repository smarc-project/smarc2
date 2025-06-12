import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from smarc_msgs.msg import PercentStamped, ThrusterRPM, ThrusterFeedback
from sam_msgs.msg import ThrusterAngles
from sam_msgs.msg import Topics as SamTopics

class SAMStandardControlPublisher(Node):
    """
    This node listens to the custom smarc control messages from SAM and republishes them
    to standard control messages for the simulation. It also listens to the feedback messages
    from the simulation and republishes them to the custom SAM feedback topics.
    """
    def __init__(self):
        super().__init__('sam_standard_control_publisher')
        self.get_logger().info('SAM Standard Control Publisher Node has been started.')
        self.declare_parameter('robot_name', 'sam')
        self.robot_name = self.get_parameter('robot_name').get_parameter_value().string_value

        ##########################################################################
        # Subscribe to control topics from SAM custom topics and republishes to sim standard topics
        ##########################################################################
        self.vbs_sub = self.create_subscription(
            PercentStamped,
            SamTopics.VBS_CMD_TOPIC,
            self.vbs_callback,
            10
        )

        self.lcg_sub = self.create_subscription(
            PercentStamped,
            SamTopics.LCG_CMD_TOPIC,
            self.lcg_callback,
            10
        )

        self.thruster1_sub = self.create_subscription(
            ThrusterRPM,
            SamTopics.THRUSTER1_CMD_TOPIC,
            self.thruster1_callback,
            10
        )

        self.thruster2_sub = self.create_subscription(
            ThrusterRPM,
            SamTopics.THRUSTER2_CMD_TOPIC,
            self.thruster2_callback,
            10
        )

        self.thruster_vector_sub = self.create_subscription(
            ThrusterAngles,
            SamTopics.THRUST_VECTOR_CMD_TOPIC,
            self.thrust_vector_callback,
            10
        )
        
        self.vbs_pub = self.create_publisher(Float32, SamTopics.STD_VBS_CMD_TOPIC, 10)
        self.lcg_pub = self.create_publisher(Float32, SamTopics.STD_LCG_CMD_TOPIC, 10)
        self.thruster1_pub = self.create_publisher(Float32, SamTopics.STD_THRUSTER1_CMD_TOPIC, 10)
        self.thruster2_pub = self.create_publisher(Float32, SamTopics.STD_THRUSTER2_CMD_TOPIC, 10)
        self.thrust_vector_yaw_pub = self.create_publisher(Float32, SamTopics.STD_THRUST_VECTOR_YAW_CMD_TOPIC, 10)
        self.thrust_vector_pitch_pub = self.create_publisher(Float32, SamTopics.STD_THRUST_VECTOR_PITCH_CMD_TOPIC, 10)

        #############################################################################
        # Subscribe to Feedback topics from SIM and republishes to SAM custom topics
        #############################################################################
        self.vbs_feedback_sub = self.create_subscription(
            Float32,
            SamTopics.STD_VBS_FB_TOPIC,
            self.vbs_feedback_callback,
            10
        )

        self.lcg_feedback_sub = self.create_subscription(
            Float32,
            SamTopics.STD_LCG_FB_TOPIC,
            self.lcg_feedback_callback,
            10
        )

        self.rmp1_feedback_sub = self.create_subscription(
            Float32,
            SamTopics.STD_THRUSTER1_FB_TOPIC,
            self.thruster1_feedback_callback,
            10
        )

        self.rmp2_feedback_sub = self.create_subscription(
            Float32,
            SamTopics.STD_THRUSTER2_FB_TOPIC,
            self.thruster2_feedback_callback,
            10
        )

        self.vbs_feedback_pub = self.create_publisher(PercentStamped, SamTopics.VBS_FB_TOPIC, 10)
        self.lcg_feedback_pub = self.create_publisher(PercentStamped, SamTopics.LCG_FB_TOPIC, 10)
        self.thruster1_feedback_pub = self.create_publisher(ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC, 10)
        self.thruster2_feedback_pub = self.create_publisher(ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC, 10)

    
    def vbs_callback(self, msg):
        """
        Callback for VBS command messages.
        Converts PercentStamped to Float32 and publishes to standard topic.
        """
        std_msg = Float32()
        std_msg.data = msg.value
        self.vbs_pub.publish(std_msg)
    
    def lcg_callback(self, msg):
        """
        Callback for LCG command messages.
        Converts PercentStamped to Float32 and publishes to standard topic.
        """
        std_msg = Float32()
        std_msg.data = msg.value
        self.lcg_pub.publish(std_msg)

    def thruster1_callback(self, msg):
        """
        Callback for Thruster 1 command messages.
        Converts ThrusterRPM to Float32 and publishes to standard topic.
        """
        std_msg = Float32()
        std_msg.data = float(msg.rpm)
        self.thruster1_pub.publish(std_msg)

    def thruster2_callback(self, msg):
        """
        Callback for Thruster 2 command messages.
        Converts ThrusterRPM to Float32 and publishes to standard topic.
        """
        std_msg = Float32()
        std_msg.data = float(msg.rpm)
        self.thruster2_pub.publish(std_msg)

    def thrust_vector_callback(self, msg):
        """
        Callback for Thruster Angles command messages.
        Publishes yaw and pitch angles to standard topics.
        """
        yaw_msg = Float32()
        yaw_msg.data = msg.thruster_horizontal_radians
        self.thrust_vector_yaw_pub.publish(yaw_msg)

        pitch_msg = Float32()
        pitch_msg.data = msg.thruster_vertical_radians
        self.thrust_vector_pitch_pub.publish(pitch_msg)

    def vbs_feedback_callback(self, msg):
        """
        Callback for VBS feedback messages.
        Converts Float32 to PercentStamped and publishes to SAM custom topic.
        """
        sam_msg = PercentStamped()
        sam_msg.value = float(msg.data)
        self.vbs_feedback_pub.publish(sam_msg)

    def lcg_feedback_callback(self, msg):
        """
        Callback for LCG feedback messages.
        Converts Float32 to PercentStamped and publishes to SAM custom topic.
        """
        sam_msg = PercentStamped()
        sam_msg.value = float(msg.data)
        self.lcg_feedback_pub.publish(sam_msg)

    def standard_thruster_feedback_to_custom_msg(self, msg):
        """
        Converts standard thruster feedback message to SAM custom ThrusterFeedback message.
        Assumes msg.data is a Float32 representing RPM.
        All other fields are set to zero.
        """
        sam_msg = ThrusterFeedback()
        sam_msg.rpm.rpm = int(msg.data)
        sam_msg.dc.dc = 0.
        sam_msg.current = 0.
        sam_msg.torque = 0.
        return sam_msg

    def thruster1_feedback_callback(self, msg):
        """
        Callback for Thruster 1 feedback messages.
        Converts Float32 to custom ThrusterFeedback and publishes to SAM custom topic.
        """
        sam_msg = self.standard_thruster_feedback_to_custom_msg(msg)
        self.thruster1_feedback_pub.publish(sam_msg)

    def thruster2_feedback_callback(self, msg):
        """
        Callback for Thruster 2 feedback messages.
        Converts Float32 to custom ThrusterFeedback and publishes to SAM custom topic.
        """
        sam_msg = self.standard_thruster_feedback_to_custom_msg(msg)
        self.thruster2_feedback_pub.publish(sam_msg)


    
def main(args=None):
    rclpy.init(args=args)
    node = SAMStandardControlPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt, shutting down...')
    finally:
        node.get_logger().info('Shutting down SAM Standard Control Publisher Node.')
        node.destroy_node()
        rclpy.shutdown()
