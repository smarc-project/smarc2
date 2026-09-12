import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from smarc_action_base.gentler_action_server import GentlerActionServer
from wasp_bt.bt.client import BTActionClient as GentlerActionClient
from smarc_action_base.smarc_action_base import ActionClientState, ActionType
from smarc_msgs.action import BaseAction
import json
from rclpy.task import Future
import asyncio
import time

class EvoloMovePath():

    _failure_states = [
            ActionClientState.DISCONNECTED,
            ActionClientState.ERROR,
            ActionClientState.REJECTED,
            ActionClientState.CANCELLED
        ]

    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself
        self.goals : list = None
        self.current_goal = 0 #Index of currently running goal

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

        

        self.move_to_client = GentlerActionClient(
                node=self._node, 
                action_name='move_to', 
                action_type=ActionType(BaseAction)
                )
                
    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it

        try: 
            raw_speed = goal_request.get('speed', 'standard')
            if isinstance(raw_speed, (int, float)):
                self.speed = float(raw_speed)
            elif raw_speed == 'slow':
                self.speed = 4.63
            elif raw_speed == 'fast':
                self.speed = 6.0
            else:
                self.speed_kn = 4.9

            waypoints = goal_request.get('waypoints', [])
            if not waypoints:
                return False

            self.goals = []
            self.current_goal = 0

            for wp_params in waypoints:
                lat  = float(wp_params['latitude'])
                lon  = float(wp_params['longitude'])
                alt  = float(wp_params.get('altitude', 0.0))
                tol  = float(wp_params['tolerance'])
                
                #Create goal JSON for move-to action
                move_to_goal_dict = {
                    "waypoint": 
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "altitude": alt,
                        "tolerance": tol,  
                        "rostype": "GeoPoint"
                    },
                    "speed": goal_request['speed']
                }
    
                self._node.get_logger().info(f"Move to goal created")
    
                move_to_goal = BaseAction.Goal()
                move_to_goal.goal.data = json.dumps(move_to_goal_dict)
                self.goals.append(move_to_goal)
            return True
        except Exception as e:
            self._node.get_logger().info(f"Failed to parse goal request: {str(e)}")
            return False


    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it

        future :Future = Future()
        self.move_to_client.cancel_goal(future.set_result)

        for i in range(4000): #4s max sleep
            if(future.done()): break
            asyncio.sleep(0)
            time.sleep(0.01)
        #rclpy.spin_until_future_complete(self._node, future, timeout_sec=4)

        response = future.result()
        self._node.get_logger().info("future result: " + str(response))
        if response != None and len(response.goals_canceling) > 0:
            self._node.get_logger().info("Successfully canceled goal")
            return True
        else:
            self._node.get_logger().info("Failed to cancel goal")
            return False

    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal
        self.current_goal = 0
        self.move_to_client.get_ready()

    def _loop_inner(self) -> bool | None:

        if(self.current_goal  >= len(self.goals)):
            #We have reached the end of the list of action servers. Must be good..
            return True
        
        self._node.get_logger().info(f"Action client state: {self.move_to_client.state.name}.")

        if(self.move_to_client.state == ActionClientState.READY): #Action client is ready. Send goal
            #Send goal
            goal = self.goals[self.current_goal]
            self.move_to_client.send_goal(goal)
            self._node.get_logger().info("Goal sent")

        # Action has failed
        if (self.move_to_client.state in self._failure_states):
              return False

        #Previous action client is done. Mone on to the next
        if(self.move_to_client.state == ActionClientState.DONE):
            self.current_goal += 1
            self.move_to_client.get_ready()
        
        return None

    def _give_feedback(self) -> str:
        feedback = f"Move path feedback wp {self.current_goal}/{len(self.goals)}"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback

def main():
    rclpy.init()
    node = Node("evolo_move_path_action_server")
    
    action_server = EvoloMovePath(node, "move_path")

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
