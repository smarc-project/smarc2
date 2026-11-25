"""Actuator output created only when Captain is configured to own control."""

from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import PercentStamped, ThrusterRPM

from sam_captain.control_type import ActuatorCmd


class SAMActuatorPublisher:
    def __init__(self, cap) -> None:
        self.cap = cap
        self._vbs_pub = cap.create_publisher(PercentStamped, SamTopics.VBS_CMD_TOPIC, 10)
        self._lcg_pub = cap.create_publisher(PercentStamped, SamTopics.LCG_CMD_TOPIC, 10)
        self._rpm_front_pub = cap.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm_back_pub = cap.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)

    def publish(self, command: ActuatorCmd) -> None:
        """Publish one command, never replaying cached commands from a timer."""
        if not self.cap.control_output_enabled:
            return

        stamp = self.cap.get_clock().now().to_msg()
        vbs = PercentStamped()
        vbs.header.stamp = stamp
        vbs.value = float(command.vbs)
        lcg = PercentStamped()
        lcg.header.stamp = stamp
        lcg.value = float(command.lcg)

        self._vbs_pub.publish(vbs)
        self._lcg_pub.publish(lcg)
        self._rpm_front_pub.publish(ThrusterRPM(rpm=int(command.rpm_front)))
        self._rpm_back_pub.publish(ThrusterRPM(rpm=int(command.rpm_back)))
