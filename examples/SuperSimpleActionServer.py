import rclpy

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer


class SuperSimple():
    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        # Initialize the action server with the node and action name
        # Give it all the necessary callbacks
        self._as = GentlerActionServer(
            node,
            action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=5.0
        )

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself
        self._looped_for = 0
        self._loop_max = 100

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it
        return True
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it
        return True
    
    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        self._looped_for = 0
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal

    def _loop_inner(self) -> bool | None:
        self._looped_for += 1
        if self._looped_for >= self._loop_max:
            self._node.get_logger().info("Reached maximum loop iterations, completing action")
            return True
        # Here you would typically perform the main logic of the action
        # Return True to indicate success, False for failure, or None to continue
        # This is run after _prepare_loop call at "loop_frequency" Hz
        return None
    
    def _give_feedback(self) -> str:
        feedback = f"Action is in progress: {self._looped_for}/{self._loop_max}"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback

def main():
    rclpy.init()
    node = Node("search_auv_action_node")
    
    SuperSimple(node, "alars_search")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Search AUV Action server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
