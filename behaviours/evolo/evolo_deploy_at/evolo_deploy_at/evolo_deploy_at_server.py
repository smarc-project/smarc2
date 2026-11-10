import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.gentler_action_client import GentlerActionClient
from smarc_action_base.smarc_action_base import ActionClientState, FAILURE_STATES
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics
from geographic_msgs.msg import GeoPoint
import json

class EvoloDeployAt():

    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself
        self.unit_to_deploy = None
        self.waypoint : GeoPoint = None

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

        self.action_clients = []
        self.action_goals = []
        self.current_action = 0 #Index of currently running action

        move_to_client = GentlerActionClient(self._node, 'move_to')
        deploy_client = GentlerActionClient(self._node, 'deploy')

        self.action_clients.append(move_to_client)
        self.action_clients.append(deploy_client)

        self._node.get_logger().info(f"[CONSTRUCTOR] Action goals: {self.action_goals}, Action clients: {self.action_clients}")

        for ac in self.action_clients:
            ac.get_ready()
        
    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it

        try: 
            unit_to_deploy = goal_request['unit']
            wp = goal_request['waypoint']

            waypoint : GeoPoint = GeoPoint()
            waypoint.latitude = float(wp['latitude'])
            waypoint.longitude = float(wp['longitude'])
            
            self._node.get_logger().info(f"Waypoint:  {waypoint}")
            self._node.get_logger().info(f"unit:  {unit_to_deploy}")

            #Create goals

            # Move to goal
            move_to_goal_dict = {
                "waypoint": 
                {
                    "latitude": waypoint.latitude,
                    "longitude": waypoint.longitude,
                    "altitude": waypoint.altitude,
                    "tolerance": 10.0,  
                    "rostype": "GeoPoint"
                },
                "speed": goal_request['speed']
            }

            self._node.get_logger().info(f"Move to goal created")

            # Deploy goal
            deploy_goal_dict = {
                "unit": unit_to_deploy
            }

            self._node.get_logger().info(f"Deploy goal created")

            #Add goals to list, one JSON string per action client
            self.action_goals = [json.dumps(move_to_goal_dict), json.dumps(deploy_goal_dict)]

            self._node.get_logger().info(f"Action goals: {self.action_goals}, Action clients: {self.action_clients}")

            #Make sure we have the same numer of goals as action clients
            assert len(self.action_clients) == len(self.action_goals)

            self._node.get_logger().info(f"Assert OK")

            return True
        except Exception as e:
            self._node.get_logger().error(f"Error parsing goal: {e}")
        return False
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Cancel whatever sub-action is running. The loop sees CANCELLED as a
        # failure state and finishes on its own.
        if self.current_action < len(self.action_clients):
            self.action_clients[self.current_action].cancel()
        return True

    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal
        self.current_action = 0
        for ac in self.action_clients:
            ac.get_ready()

    def _loop_inner(self) -> bool | None:

        if(self.current_action  >= len(self.action_clients)):
            #We have reached the end of the list of action servers. Must be good..
            return True
        
        action_client : GentlerActionClient = self.action_clients[self.current_action]
        self._node.get_logger().info(f"Action client state: {action_client.state.name}.")

        if(action_client.state == ActionClientState.READY): #Action client is ready. Send goal
            #Send goal
            action_client.send(self.action_goals[self.current_action])
            self._node.get_logger().info("Goal sent")

        # Action has failed
        if (action_client.state in FAILURE_STATES):
              return False

        #Previous action client is done. Mone on to the next
        if(action_client.state == ActionClientState.DONE):
            self.current_action += 1
        
        return None

    def _give_feedback(self) -> str:
        feedback = "Deploy feedback"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback

def main():
    rclpy.init()
    node = Node("evolo_deploy_action_server")
    
    action_server = EvoloDeployAt(node, "deploy_at")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down evolo deploy at acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()