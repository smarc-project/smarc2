import rclpy
from rclpy.node import Node, Optional
from rclpy.executors import Future, MultiThreadedExecutor

from std_srvs.srv import Trigger
from smarc_action_base.gentler_action_server import GentlerActionServer


class TriggerServiceActionServer:
    def __init__(self, node: Node):
        self._node = node

        node.declare_parameter("service_name", "unknown_trigger_service")
        self._service_name : str = node.get_parameter("service_name").get_parameter_value().string_value

        node.declare_parameter("task_name", f"{self._service_name}_action_server")
        self._task_name : str = node.get_parameter("task_name").get_parameter_value().string_value

        node.declare_parameter("loop_rate", 5.0)
        self._loop_rate : float = node.get_parameter("loop_rate").get_parameter_value().double_value

        self._srv = node.create_client(Trigger, self._service_name)
        while rclpy.ok() and not self._srv.wait_for_service(timeout_sec=5.0):
            node.get_logger().info(f"Waiting for service {self._service_name} to be available...")

        self._as = GentlerActionServer(
            self._node,
            self._task_name,
            self._on_goal_received,
            self._on_cancel_received,
            lambda: None,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = self._loop_rate
        )

        self._future : Optional[Future] = None



    def _on_goal_received(self, goal_request: dict) -> bool:
        if self._future is None:
            self._future = self._srv.call_async(Trigger.Request())
            self._node.get_logger().info(f"Received goal, calling service {self._service_name}...")
            return True
        else:
            self._node.get_logger().warn("Received new goal while still processing previous one, rejecting new goal")
            return False
        

    def _on_cancel_received(self) -> bool:
        if self._future is not None:
            self._future.cancel()
            self._future = None
            self._node.get_logger().info("Goal cancelled, cancelling service call")
        else: 
            self._node.get_logger().warn("Received cancel request but no goal is being processed, ignoring cancel request")
        return True
    

    def _loop_inner(self) -> bool|None:
        if self._future is None:
            self._node.get_logger().info("No goal being processed, doing nothing")
            return False
        
        if not self._future.done():
            return None
        
        try:
            ret = self._future.result()
            if ret is not None:
                res : Trigger.Response = ret
            else:
                self._node.get_logger().error("Service call future completed with no result, treating as failure")
                self._future = None
                return False
            
            if res.success:
                self._node.get_logger().info(f"Service call succeeded with message: {res.message}")
                self._future = None

                return True
            else:
                self._node.get_logger().error(f"Service call failed with message: {res.message}")
                self._future = None
                return False
            
        except Exception as e:
            self._node.get_logger().error(f"Service call failed with exception: {e}")
            self._future = None
            return False

    def _give_feedback(self) -> str:
        if self._future is None:
            return "No goal being processed"
        elif not self._future.done():
            return "Service call in progress..."
        else:
            return "Service call completed, waiting for next goal"
        

def main(args=None):
    rclpy.init(args=args)

    node = Node("trigger_service_action_server")

    trigger_service_action = TriggerServiceActionServer(node)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()