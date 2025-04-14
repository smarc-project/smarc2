import rclpy
from action_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.action.client import ClientGoalHandle
from smarc_action_base.smarc_action_base import ActionType, SMARCActionClient
from smarc_mission_msgs.action import GotoSetpoint


class GeopointClient(SMARCActionClient):
    def __init__(
        self, node: rclpy.node.Node, action_name: str, action_type: ActionType, **kwargs
    ):
        super().__init__(node, action_name, action_type)
        self.logger = self._node.get_logger()
        self.declare_parameters()

    def declare_parameters(self):
        node = self._node
        self.robot_name = node.declare_parameter("robot_name", "Quadrotor").value

    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Result when a goal is sent to the server."""
        if not goal_handle.accepted:
            self.logger.info("Goal was not accepted")
            return
        self._goal_handle = goal_handle

        self.get_result(goal_handle)

    def feedback_callback(self, feedback_msg: ActionType.Feedback):
        """Result when a goal is sent to the server."""
        self.logger.info(f"Received feedback {feedback_msg.distance_remaining}")

    def result_callback(self, result: ActionType.Result, status: GoalStatus):
        """Result when a goal is sent to the server."""
        self.logger().info(f"Waypoint reached boolean: {result}")

    def test_geopoint(self):
        goal_msg = GotoSetpoint.Goal()
        goal_msg.setpoint = GeoPoint()
        # https://awsm-tools.com/utm-to-lat-long?form%5Beasting%5D=652698.125&form%5Bnorthing%5D=6524250.5&form%5Bzone%5D=33&form%5Bband%5D=V&form%5Bellipsoid%5D=WGS+84
        # goal_msg.setpoint.latitude = 58.83099123563405
        # goal_msg.setpoint.longitude = 17.645308490070622
        goal_msg.setpoint.latitude = 58.82332
        goal_msg.setpoint.longitude = 17.635227
        goal_msg.setpoint.altitude = 10.0
        self.logger.info(f"Sending empty geopoint {goal_msg.setpoint}")
        self.send_goal(goal_msg, server_timeout_sec=1)


def main(args=None):
    rclpy.init(args=args)
    node_name = "setpoint_client"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(GotoSetpoint)
    setpoint = GeopointClient(node, "go_to_setpoint", action_type)
    setpoint.test_geopoint()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
