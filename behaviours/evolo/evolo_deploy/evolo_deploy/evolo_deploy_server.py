import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from smarc_action_base.gentler_action_server import GentlerActionServer
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics

class EvoloDeploy():

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
            loop_frequency=2
        )

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself

        #Callback groups
        self.publisher_callback_group = ReentrantCallbackGroup()

        # Publishers
        self.deploy_pub = self._node.create_publisher(String, evoloTopics.EVOLO_CAPTAIN_TO, 10, callback_group=self.publisher_callback_group)
        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it

        try: 
            self.unit_to_deploy = goal_request['unit']
            if(self.unit_to_deploy == "right"):
                self._node.get_logger().error(f"Dropping right puffin")
                command = String()
                command.data = "{\"Puffin\": \"dropRight\"}"
                self.deploy_pub.publish(command)
            elif(self.unit_to_deploy == "left"):
                self._node.get_logger().error(f"Dropping left puffin")
                command = String()
                command.data = "{\"Puffin\": \"dropLeft\"}"
                self.deploy_pub.publish(command)
            elif(self.unit_to_deploy == "both"):
                self._node.get_logger().error(f"Dropping both puffins")
                command = String()
                command.data = "{\"Puffin\": \"drop\"}"
                self.deploy_pub.publish(command)
            else:
                self._node.get_logger().error(f"Unknown puffin: {self.unit_to_deploy}")

        except Exception as e:
            self._node.get_logger().error(f"Error parsing goal: {e}")
            return False
        return True
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it
        return True

    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal

    def _loop_inner(self) -> bool | None:
        # Return true right away. Hopefully one publication of "realease" is enough.
        # Otherwire keep publishing here for a few seconds
        return True

    def _give_feedback(self) -> str:
        feedback = "Deploy feedback"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback

def main():
    rclpy.init()
    node = Node("evolo_deploy_action_server")
    
    action_server = EvoloDeploy(node, "deploy")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down evolo move to acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()