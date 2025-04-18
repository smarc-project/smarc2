from typing import Type
from rclpy.node import Node
from std_msgs.msg import String
from smarc_msgs.msg import Topics
from smarc_bt.vehicles.sensor import Sensor, SensorNames
import json
from copy import deepcopy

class HasWaraPSTaskHandler:
    """
    This class is used to mark a class as having an MQTT interactor. This is used to make sure that the class has the methods that are needed for the MQTT interactor to work.
    """
    def __init__(self):
        self._wara_ps_task_handler = None
        self._wara_ps_dict = None
        self._robot_name = None

    @property
    def wara_ps_task_handler(self):
        """
        Returns the WaraPSTaskHandler object that is used to handle the MQTT interactor.
        """
        return self._wara_ps_task_handler

    @wara_ps_task_handler.setter
    def wara_ps_task_handler(self, value):
        """
        Sets the WaraPSTaskHandler object that is used to handle the MQTT interactor.
        """
        self._wara_ps_task_handler = value

    @property
    def wara_ps_dict(self):
        """
        Returns the WaraPS dictionary that is used to handle the MQTT interactor.
        """
        return self._wara_ps_dict
    
    @wara_ps_dict.setter
    def wara_ps_dict(self, value):
        """
        Sets the WaraPS dictionary that is used to handle the MQTT interactor.
        """
        self._wara_ps_dict = value
        self._robot_name = value["name"] if value else None

class WaraPSTaskHandler:
    def __init__(self, node:Node, wara_ps_dict:Type[dict]):
        """
        A class to handle the parts of the BT that need to interact with MQTT. This will later double up as the Mission Command and Updator.

        It is the job of this interactor to listen and publish to the relevant ROS topics connected to the MQTT bridge, and handle WARA-PS actions.
        """

        # public: outsiders can access this        
        self._wara_ps_dict = wara_ps_dict
        self._robot_name = wara_ps_dict["name"]

        self.past_tasks = []
        self.tasks_executing = []


        # private: only this class should access this
        self._node = node


        
        # Publishers for Level 2 WARA-PS topics
        self._wara_ps_direct_execution_info_pub = node.create_publisher(String, Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC, 10)

        self._wara_ps_exec_response_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_RESPONSE_TOPIC, 10)
        self._wara_ps_exec_feedback_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_FEEDBACK_TOPIC, 10)

        # subscribe to Level 1 heartbeat to trigger direct_execution_info
        # self._wara_ps_heartbeat_sub = node.create_subscription(String, Topics.WARA_PS_HEARTBEAT_TOPIC, self._publish_direct_execution_info_cb, 10)


        # Subscriptions for WARA-PS command topics
        self._wara_ps_exec_command_sub = node.create_subscription(String, Topics.WARA_PS_EXEC_COMMAND_TOPIC, self._exec_command_cb, 10)



        if "direct_execution" in self._wara_ps_dict["levels"]:
            self._direct_execusion_info_data = {
                "name": self._wara_ps_dict["name"],
                "rate": self._wara_ps_dict["pulse_rate"],
                "type": "DirectExecutionInfo",
                "stamp": "",
                "tasks-available": self._wara_ps_dict["tasks-available"],
                "tasks-executing": self.tasks_executing,
            }


    



    # read only task_handler.wara_ps_dict
    @property
    def wara_ps_dict(self):
        """
        Returns the WaraPS dictionary that is used to handle the MQTT interactor.
        """
        return self._wara_ps_dict


    def lvl_2_heartbeat(self, now_time):
        """
        This method is called to publish the level 2 heartbeat.
        """
        # find now_time from the stamp in the heartbeat data
        self._direct_execusion_info_data["stamp"] = now_time


        # naming convention change
        list_of_running_tasks = deepcopy(self.tasks_executing)

        # for every dict in this list, rename the key "name" to "task-name"
        for i in range(len(list_of_running_tasks)):
            list_of_running_tasks[i]["task-name"] = list_of_running_tasks[i]["task"]["name"]
            # remove "task" param from dict
            list_of_running_tasks[i].pop("task", None)
            # remove "status" param from dict
            # list_of_running_tasks[i].pop("status", None)

        # update tasks executing
        self._direct_execusion_info_data["tasks-executing"] = list_of_running_tasks


        # publish the heartbeat data
        msg = String()
        msg.data = json.dumps(self._direct_execusion_info_data)
        self._wara_ps_direct_execution_info_pub.publish(msg)
        self._node.get_logger().info('Published Direct Execution Info message')
        
        return True    

    def _exec_command_cb(self, data: String):
        # this function is called when a new command is received from the MQTT broker
        # parse the command
        command = json.loads(data.data)
        self._node.get_logger().info(f"Received command: {command}")
        # check if the command is valid
        if "command" not in command:
            self._node.get_logger().error("Invalid command: missing 'command' key")
            return
        
        # handle ping command
        if command["command"] == "ping":
            # check if the command is valid
            if "com-uuid" not in command:
                self._node.get_logger().error("Invalid ping command: missing 'com-uuid' key")
                return
            # publish the response
            pong_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command["com-uuid"],
                "response": "pong",
                "response-to": command["com-uuid"]
            }

            msg = String()
            msg.data = json.dumps(pong_msg)
            self._wara_ps_exec_response_pub.publish(msg)
            self._node.get_logger().info('Published Ping response message')

        # handle signal-task command
        elif command["command"] == "signal-task":
            # check if the command is valid
            if "task-uuid" not in command:
                self._node.get_logger().error("Invalid signal-task command: missing 'task-uuid' key")

            status_msg = "task not found",
            
            if command["task-uuid"] not in [task["task-uuid"] for task in self.tasks_executing]:
                self._node.get_logger().error("Invalid signal-task command: task not found in executing tasks")

                status_msg = "task not in current tasks"

            else: # if the task is found in executing tasks

                status_msg = "ok"
              
                # what is the signal asking for? options: enough, pause, continue, abort
                if command["signal"] == "$abort" or command["signal"] == "$enough":
                    # remove the task from the executing tasks list
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"]:
                            self.tasks_executing.pop(self.tasks_executing.index(task))
                            break
                    # add the task to the completed tasks list
                    task_dict = {
                        "task-uuid": command["task-uuid"],
                        "status": command["signal"]
                    }
                    self.past_tasks.append(task_dict)
                
                elif command["signal"] == "$pause":
                    # pause the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"]:
                            task["status"] = "paused"
                            break
                elif command["signal"] == "$continue":
                    # continue the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"] and task["status"] == "paused":
                            task["status"] = "running"
                            break
                
            response_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command["com-uuid"],
                "response": status_msg,
                "response-to": command["com-uuid"]
            }
            
            msg = String()
            msg.data = json.dumps(response_msg)
            self._wara_ps_exec_response_pub.publish(msg)
            self._node.get_logger().info('Published Signal Task response message')

        # handle query-task command
        elif command["command"] == "query-task":
            # check if the command is valid
            if "task-uuid" not in command:
                self._node.get_logger().error("Invalid query-task command: missing 'task-uuid' key")
                return
            
            # check if the task is valid
            status_msg = "task not found",
            
            if command["task-uuid"] in self.tasks_executing:
                status_msg = "ok"
                # get the task status
                for task in self.tasks_executing:
                    if task["task-uuid"] == command["task-uuid"]:
                        status_msg = task["status"]
                        break
            
            response_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command["com-uuid"],
                "response": status_msg,
                "response-to": command["com-uuid"]
            }
            
            msg = String()
            msg.data = json.dumps(response_msg)
            self._wara_ps_exec_response_pub.publish(msg)
            self._node.get_logger().info('Published Query Task response message')

        # handle start-task command
        elif command["command"] == "start-task":
            # check if the task is valid
            if "task" not in command:
                self._node.get_logger().error("Invalid start-task command: missing 'task' key")
                return

            if not any(task["task-uuid"] == command["task-uuid"] for task in self.tasks_executing): # if this task is not already executing
            
                # add the task to the executing tasks list
                task_dict = {
                    "task-uuid": command["task-uuid"],
                    "task": command["task"],
                    "status": "started"
                }
                self.tasks_executing.append(task_dict)
                self._node.get_logger().info(f"Starting task: {command['task']}")
                # publish the feedback
                feedback_msg = {

                    "agent-uuid": self.wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "task-uuid": command["task-uuid"],
                    "task": command["task"],
                    "status": "started",
                }
                msg = String()
                msg.data = json.dumps(feedback_msg)
                self._wara_ps_exec_response_pub.publish(msg)

                self._node.get_logger().info('Published Start Task response message')
            

        return

    def clear_task_queue(self):
        """
        Clears the task queue.
        """
        self.tasks_executing = []
        
    def get_executing_tasks(self):
        """
        Returns the list of executing tasks.
        """
        return self.tasks_executing
    
    def get_current_task_params(self):
        """
        Returns the parameters of the current task.
        """
        if len(self.tasks_executing) > 0:
            return self.tasks_executing[0]["task"]["params"]
        else:
            # log
            self._node.get_logger().error("No tasks executing")
            return None