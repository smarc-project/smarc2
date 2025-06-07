from typing import Type
from rclpy.node import Node
from std_msgs.msg import String, Int8
from smarc_msgs.msg import Topics
from smarc_bt.vehicles.sensor import Sensor, SensorNames
import json
from copy import deepcopy
import enum
from std_srvs.srv import Trigger

# TODO: move this to a common place
class WaraPSTaskStates(enum.Enum):
    """
    The states of the WARAPS task
    """
    STARTED = "started"
    RUNNING = "running"
    PAUSED = "paused"
    RESUMED = "resumed"
    ENOUGH = "enough"
    ABORTED = "aborted"
    ERROR = "error"


    def __str__(self):
        return self.name
    
class WaraPSCommandSignals(enum.Enum):
    """
    The signals that can be sent to the WaraPS task
    """
    ABORT = "$abort"
    ENOUGH = "$enough"
    PAUSE = "$pause"
    CONTINUE = "$continue"
    CANCEL_ABORT = "$cancel_abort" 

    def __str__(self):
        return self.name

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

        # private: only this class should access this
        self._node = node

        # public: outsiders can access this        
        self._wara_ps_dict = wara_ps_dict
        self._robot_name = wara_ps_dict["name"]

        self.tasks_available = []
        self.past_tasks = []
        self.tasks_executing = []

        self.aborted_flag = False
        self.emergency_flag = False
        self.health_status = Topics.VEHICLE_HEALTH_ERROR
        
        self.health_last_time = self.current_time()

        self.mission_start_time = None
        self.mission_timeout = None


        
        # Publishers for Level 2 WARA-PS topics
        self._wara_ps_direct_execution_info_pub = node.create_publisher(String, Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC, 10)

        self._wara_ps_exec_response_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_RESPONSE_TOPIC, 10)
        self._wara_ps_exec_feedback_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_FEEDBACK_TOPIC, 10)


        # Publishers for Level 3 WARA-PS topics
        self._wara_ps_tst_exec_info_pub = node.create_publisher(String, Topics.WARA_PS_TST_EXEC_INFO_TOPIC, 10)

        self._wara_ps_tst_response_pub = node.create_publisher(String, Topics.WARA_PS_TST_RESPONSE_TOPIC, 10)
        self._wara_ps_tst_feedback_pub = node.create_publisher(String, Topics.WARA_PS_TST_FEEDBACK_TOPIC, 10)


        # subscribe to Level 1 heartbeat to trigger direct_execution_info
        # self._wara_ps_heartbeat_sub = node.create_subscription(String, Topics.WARA_PS_HEARTBEAT_TOPIC, self._publish_direct_execution_info_cb, 10)


        # Subscriptions for WARA-PS command topics
        self._wara_ps_exec_command_sub = node.create_subscription(String, Topics.WARA_PS_EXEC_COMMAND_TOPIC, self._exec_command_cb, 10)

        self._wara_ps_tst_command_sub = node.create_subscription(String, Topics.WARA_PS_TST_COMMAND_TOPIC, self._tst_command_cb, 10)

        # Subscriptions to action Server topics
        self._wara_ps_action_server_sub = node.create_subscription(String, Topics.WARA_PS_ACTION_SERVER_HB_TOPIC, self._action_hb_callback, 10)

        self._level_1_heartbeat_sub = node.create_subscription(String, Topics.WARA_PS_HEARTBEAT_TOPIC, self._read_level_1_heartbeat_cb, 1)

        # subscribe to ABORT topic
        self._wara_ps_abort_sub = node.create_subscription(String, Topics.WARA_PS_ABORT_TOPIC, self._bigredbutton_cb, 10)

        # subscribe to SMARC-wide abort topic
        self._smarc_abort_sub = node.create_subscription(String, Topics.ABORT_TOPIC, self._bigredbutton_cb, 10)

        # subscribe to smarc health topic
        self._vehicle_health_sub = node.create_subscription(Int8, Topics.VEHICLE_HEALTH_TOPIC, self._vehicle_health_cb, 10)


        if "direct_execution" in self._wara_ps_dict["levels"]:
            self._direct_execution_info_data = {
                "name": self._wara_ps_dict["name"],
                "rate": self._wara_ps_dict["pulse_rate"],
                "type": "DirectExecutionInfo",
                "stamp": "",
                # "tasks-available": self._wara_ps_dict["tasks-available"],
                "tasks-available": [], # empty list, read from relevant topic in callback for action server subscriptions
                "tasks-executing": self.tasks_executing,
            }

        # Add the reset emergency service
        self._reset_emergency_srv = self._node.create_service(
            Trigger,
            "reset_emergency",
            self._reset_emergency_cb
        )

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
        self._direct_execution_info_data["stamp"] = now_time


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
        self._direct_execution_info_data["tasks-executing"] = list_of_running_tasks

        # drop tasks that have not been seen for a while (3 seconds)
        popped_indices = []
        for i in range(len(self.tasks_available)):
            # self._node.get_logger().info(f"Checking task {i} with name {self.tasks_available[i]['name']}")
            task = self.tasks_available[i]
            # log (now_time - task["last_seen"])
            if float(now_time - task["last_seen"]) > 3.0:
                # remove the task from the list of available tasks
                popped_indices.append(i)
                self._node.get_logger().info(f"Removed task {task['name']} from available at time {now_time}, last seen at {task['last_seen']}")

        # remove the tasks from the list of available tasks
        for i in reversed(popped_indices):
            self.tasks_available.pop(i)


        self._direct_execution_info_data["tasks-available"] = self.tasks_available


        # publish the heartbeat data
        msg = String()
        msg.data = json.dumps(self._direct_execution_info_data)
        self._wara_ps_direct_execution_info_pub.publish(msg)
        # self._node.get_logger().info('Published Direct Execution Info message')
        
        return True    
    
    def lvl_3_heartbeat(self, now_time):
        """
        This method is called to publish the level 3 heartbeat.
        It is used to update the WaraPS dictionary with the latest data.
        """
        # find now_time from the stamp in the heartbeat data
        self._direct_execution_info_data["stamp"] = now_time
        self._direct_execution_info_data["type"] = "TSTExecutionInfo"

        # publish the heartbeat data
        msg = String()
        msg.data = json.dumps(self._direct_execution_info_data)
        self._wara_ps_tst_exec_info_pub.publish(msg)
        # self._node.get_logger().info('Published TST Execution Info message')

        # ABORT IF MISSION TIMOUT HAS BEEN EXCEEDED
        # do this only if there is a mission running
        if self.mission_start_time is not None and self.mission_timeout is not None and self.emergency_flag is False:
            if self.current_time() - self.mission_start_time > self.mission_timeout:
                self._node.get_logger().warn(f"Mission timeout exceeded. Aborting mission.")
                # set emergency flag
                self.emergency_flag = True
                # publish abort command
                abort_msg = {
                    "agent-uuid": self._wara_ps_dict["agent-uuid"],
                    "com-uuid": "",
                    "response": "mission timeout exceeded",
                    "response-to": ""
                }
                msg = String()
                msg.data = json.dumps(abort_msg)
                self._wara_ps_tst_feedback_pub.publish(msg)
                return False
            elif self.tasks_executing == []: # no tasks are executing
                # in the case that a mission was initiated and completed within time, reset mission timer to Nones
                self.mission_start_time = None
                self.mission_timeout = None
    
        return True
    
    def _read_level_1_heartbeat_cb(self, data: String):
        """
        This method is called to read the level 1 heartbeat.
        It is used to update the WaraPS dictionary with the latest data.
        """
        # parse the command
        if self._wara_ps_dict['agent-uuid'] is not None:
            return
        try:
            hb_data = json.loads(data.data)
        except json.JSONDecodeError as e:
            self._node.get_logger().error(f"Failed to decode JSON from heartbeat data: {e}")
            return
        # update the WaraPS dictionary with the heartbeat data
        # log
        self._node.get_logger().info(f"Received Level 1 heartbeat. Copying agent-uuid: {hb_data['agent-uuid']}")
        self._wara_ps_dict["agent-uuid"] = hb_data["agent-uuid"]

        # unregister the heartbeat subscriber
        self._node.destroy_subscription(self._level_1_heartbeat_sub)

    def _action_hb_callback(self, data: String):
        # this function is called when a new action server heartbeat is received

        # get the current time
        now_time = self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9

        # parse the command
        action_name = data.data
        # self._node.get_logger().info(f"Received action server heartbeat: {action_name}")

        # action name is the name of the action server, a ros topic ish. We want to get rid of the namespacing and just hold on to the last part of the name. Further, we want to replace the "_" with "-" in this last part of the name
        parsed_action_name = action_name.split("/")[-1]
        parsed_action_name = parsed_action_name.replace("_", "-")

        #TODO: remove this hacky shit, unless on drone
        # parsed_action_name = "move-to"

        # if this action server is not already in the list of available tasks, add it
        if parsed_action_name not in [task["name"] for task in self.tasks_available]:
            # add the action server to the list of available tasks
            task_dict = {
                "name": parsed_action_name,
                "signals": [
                    WaraPSCommandSignals.ABORT.value,
                    WaraPSCommandSignals.ENOUGH.value, 
                    WaraPSCommandSignals.PAUSE.value, 
                    WaraPSCommandSignals.CONTINUE.value
                ],
                "last_seen": now_time,
                "ros_name": action_name,
            }
            self.tasks_available.append(task_dict)

            # log last seen time
            self._node.get_logger().info(f"Found new action server: {action_name} at {now_time}")

            return

        # if this action server is already in the list of available tasks, update the last seen time
        else:
            # update the last seen time
            for i in range(len(self.tasks_available)):
                task = self.tasks_available[i]
                if task["name"] == parsed_action_name:
                    # update the last seen time
                    self.tasks_available[i]["last_seen"] = now_time
                    break
            # log last seen time
            # self._node.get_logger().info(f"Updated action server: {action_name} at {now_time}")
        

    def _exec_command_cb(self, data: String):
        # this function is called when a new command is received from the MQTT broker
        # parse the command
        command = json.loads(data.data)
        self._node.get_logger().info(f"Received command: {command}")

        # Refuse starts or signals if emergency flag is up
        if self.emergency_flag and command["command"] in ["start-task", "signal-task"]:
            response_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command.get("com-uuid", ""),
                "response": "rejected: emergency flag is up",
                "response-to": command.get("com-uuid", "")
            }
            msg = String()
            msg.data = json.dumps(response_msg)
            self._wara_ps_exec_response_pub.publish(msg)
            self._node.get_logger().warn("Rejected start/signal command due to emergency flag.")
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

            status_msg = "task not found"
            
            if command["task-uuid"] not in [task["task-uuid"] for task in self.tasks_executing]:
                self._node.get_logger().error("Invalid signal-task command: task not found in executing tasks")
                status_msg = "task not in current tasks"

            else: # if the task is found in executing tasks
                status_msg = "ok"
                # what is the signal asking for? options: enough, pause, continue, abort

                if command["signal"] == WaraPSCommandSignals.ABORT.value:
                    # abort the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"]:
                            task["status"] = WaraPSTaskStates.ABORTED.value
                            break
                elif command["signal"] == WaraPSCommandSignals.ENOUGH.value:
                    # enough of the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"]:
                            task["status"] = WaraPSTaskStates.ENOUGH.value
                            break
                elif command["signal"] == WaraPSCommandSignals.PAUSE.value:
                    # pause the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"]:
                            task["status"] = WaraPSTaskStates.PAUSED.value
                            break
                elif command["signal"] == WaraPSCommandSignals.CONTINUE.value:
                    # continue the task
                    for task in self.tasks_executing:
                        if task["task-uuid"] == command["task-uuid"] and task["status"] == WaraPSTaskStates.PAUSED.value:
                            task["status"] = WaraPSTaskStates.RESUMED.value
                            break

            valid_signals = [s.value for s in WaraPSCommandSignals]
            if command["signal"] not in valid_signals:
                self._node.get_logger().error("Invalid signal-task command: invalid signal")
                status_msg = "invalid signal"

            if command["signal"] in [WaraPSCommandSignals.ABORT.value, WaraPSCommandSignals.ENOUGH.value]:
                # remove the task from the executing tasks list
                for i in range(len(self.tasks_executing)):
                    task = self.tasks_executing[i]
                    if task["task-uuid"] == command["task-uuid"]:
                        self.past_tasks.append(task)
                        self.tasks_executing.pop(i)
                        self.aborted_flag = True
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
            status_msg = "task not found"
            
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

                # send response
                response_msg = {
                    "agent-uuid": self._wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "response": "task not found",
                    "response-to": command["com-uuid"]
                }
                msg = String()
                msg.data = json.dumps(response_msg)
                self._wara_ps_exec_response_pub.publish(msg)
                return
            
            # check if the task is available
            if command["task"]["name"] not in [task["name"] for task in self.tasks_available]:
                self._node.get_logger().error("Invalid start-task command: task not available")

                # send response
                response_msg = {
                    "agent-uuid": self._wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "response": "task not available",
                    "response-to": command["com-uuid"]
                }
                msg = String()
                msg.data = json.dumps(response_msg)
                self._wara_ps_exec_response_pub.publish(msg)
                return


            if not any(task["task-uuid"] == command["task-uuid"] for task in self.tasks_executing): # if this task is not already executing
                # add the task to the executing tasks list
                task_dict = {
                    "task-uuid": command["task-uuid"],
                    "task": command["task"],
                    "status": WaraPSTaskStates.STARTED.value,
                    "description": command["task"]["description"] if "description" in command["task"].keys() else "",
                }
                self.tasks_executing.append(task_dict)
                # self._node.get_logger().info(f"Starting task: {command['task']}")
                # publish the feedback
                feedback_msg = {
                    "agent-uuid": self.wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "task-uuid": command["task-uuid"],
                    "task": command["task"],
                    "status": WaraPSTaskStates.STARTED.value,
                }
                msg = String()
                msg.data = json.dumps(feedback_msg)
                self._wara_ps_exec_response_pub.publish(msg)

                self._node.get_logger().info('Published Start Task response message')

        return
    
    def _tst_command_cb(self, data: String):
        # This function is called when a new TST command is received from the MQTT broker
        command = json.loads(data.data)
        self._node.get_logger().info(f"Received TST command: {command}")

        # Refuse starts or signals if emergency flag is up
        if self.emergency_flag and command["command"] in ["start-tst"]:
            response_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command.get("com-uuid", ""),
                "response": "rejected: emergency flag is up",
                "response-to": command.get("com-uuid", "")
            }
            msg = String()
            msg.data = json.dumps(response_msg)
            self._wara_ps_tst_response_pub.publish(msg)
            self._node.get_logger().warn("Rejected start TST command due to emergency flag.")
            return

        # check if the command is valid
        if "command" not in command:
            self._node.get_logger().error("Invalid TST command: missing 'command' key")
            return

        # Example: handle signal-tst command
        elif command["command"] == "signal-unit":
            if "unit" not in command:
                self._node.get_logger().error("Invalid signal-task command: missing 'unit' key")
                return
                

            status_msg = "ok"
            if command["signal"] == WaraPSCommandSignals.ABORT.value:
                for task in self.tasks_executing:
                    task["status"] = WaraPSTaskStates.ABORTED.value
            elif command["signal"] == WaraPSCommandSignals.ENOUGH.value:
                for task in self.tasks_executing:
                    task["status"] = WaraPSTaskStates.ENOUGH.value
            elif command["signal"] == WaraPSCommandSignals.PAUSE.value:
                for task in self.tasks_executing:
                    task["status"] = WaraPSTaskStates.PAUSED.value
            elif command["signal"] == WaraPSCommandSignals.CONTINUE.value:
                for task in self.tasks_executing:
                    task["status"] = WaraPSTaskStates.RESUMED.value
            elif command["signal"] == WaraPSCommandSignals.CANCEL_ABORT.value:
                self.emergency_flag = False
                self.mission_start_time = None
                self.mission_timeout = None

            valid_signals = [s.value for s in WaraPSCommandSignals]
            if command["signal"] not in valid_signals:
                self._node.get_logger().error("Invalid signal-tst command: invalid signal")
                status_msg = "invalid signal"

            if command["signal"] in [WaraPSCommandSignals.ABORT.value, WaraPSCommandSignals.ENOUGH.value]:
                for i in range(len(self.tasks_executing)):
                    task = self.tasks_executing[0]
                    self.past_tasks.append(task)
                    self.tasks_executing.pop(0)
                
                # raise aborted flag
                self.aborted_flag = True

                if command["signal"] == WaraPSCommandSignals.ABORT.value:
                    self.emergency_flag = True



            response_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "com-uuid": command["com-uuid"],
                "response": status_msg,
                "response-to": command["com-uuid"]
            }
            msg = String()
            msg.data = json.dumps(response_msg)
            self._wara_ps_tst_response_pub.publish(msg)
            self._node.get_logger().info('Published TST Signal Task response message')

            
        elif command["command"] == "start-tst": 
            # '''
            # {"receiver":"shekharu_lolo","tst":{"common-params":{"execunit":"/shekharu_lolo","node-uuid":"e5bcb11a-2c8f-48cc-94c1-747c88ab516e"},"params":{},"children":[{"description":"1","task-uuid":"03acd059-73d2-412f-8d75-f3fd2b9efac0","params":{"waypoint":{"latitude":58.850523629300554,"longitude":17.674904712183004,"target_depth":10.0,"min_altitude":5.0,"rpm":1000.0,"timeout":1000.0}},"name":"auv-depth-move-to"},{"description":"2","task-uuid":"c83ff631-8b63-4c69-a260-9008782ee41a","params":{"waypoint":{"latitude":58.850628267523796,"longitude":17.675200365495684,"target_depth":15.0,"min_altitude":5.0,"rpm":1000.0,"timeout":1000.0}},"name":"auv-depth-move-to"}],"tst-uuid":"0536c8e2-0d23-45e0-9434-eed663b14ec0","description":"Lolo Test","name":"seq"},"command":"start-tst","com-uuid":"fe38f852-7ff4-4f4a-bd78-62011e0fca00","sender":"UnityGUI"}
            # '''
            # check if the command is valid
            if "tst" not in command.keys():
                self._node.get_logger().error("Invalid start-tst command: missing 'tst' key")
                response_msg = {
                    "agent-uuid": self._wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "response": "task not found",
                    "response-to": command["com-uuid"]
                }
                msg = String()
                msg.data = json.dumps(response_msg)
                self._wara_ps_tst_response_pub.publish(msg)
                return
                
            # start mission timer
            self.mission_start_time = self.current_time()
            
            # extract the mission timout from "params" key in tst
            if "params" in command["tst"].keys() and "mission-timeout" in command["tst"]["params"].keys():
                self.mission_timeout = command["tst"]["params"]["mission-timeout"]
                self._node.get_logger().info(f"Mission timeout set to {self.mission_timeout} seconds")
            else:
                self.mission_timeout = 1800 # default mission timeout
            self._node.get_logger().info(f"Default Mission timeout set to {self.mission_timeout} seconds")

            # extract the list of tasks from the command. They're the children of the tst key
            if "children" not in command["tst"]:
                self._node.get_logger().error("Invalid start-tst command: missing 'children' key in 'tst'")
                response_msg = {
                    "agent-uuid": self._wara_ps_dict["agent-uuid"],
                    "com-uuid": command["com-uuid"],
                    "response": "task not found",
                    "response-to": command["com-uuid"]
                }
                msg = String()
                msg.data = json.dumps(response_msg)
                self._wara_ps_tst_response_pub.publish(msg)
                return

            common_params = command["tst"]["common-params"] if "common-params" in command["tst"].keys() else {}
            tasks = command["tst"]["children"]

            # inject common params into each tasks params
            for task in tasks:
                if "params" not in task:
                    task["params"] = {}
                # merge common params into task params
                task["params"].update(common_params)
                # add the task to the executing tasks list
                task_dict = {
                    "task-uuid": task["task-uuid"],
                    "task": task,
                    "status": WaraPSTaskStates.STARTED.value,
                    "description": task["description"] if "description" in task.keys() else "",
                }
                self.tasks_executing.append(task_dict)

        return        
    
    def _vehicle_health_cb(self, data: Int8):
        """
        This method is called when a new vehicle health message is received.
        It is used to update the WaraPS dictionary with the latest data.
        """
        # log the time of the last health status update
        self.health_last_time = self.current_time()

        vehicle_health_status = data.data
        
        # update the health status
        if vehicle_health_status == Topics.VEHICLE_HEALTH_READY:
            self.health_status = Topics.VEHICLE_HEALTH_READY
            # self._node.get_logger().info("Vehicle health status: OK")
        elif vehicle_health_status == Topics.VEHICLE_HEALTH_WAITING:
            self.health_status = Topics.VEHICLE_HEALTH_WAITING
            # self._node.get_logger().warn("Vehicle health status: WARNING")
        elif vehicle_health_status == Topics.VEHICLE_HEALTH_ERROR:
            self.health_status = Topics.VEHICLE_HEALTH_ERROR
            # self._node.get_logger().error("Vehicle health status: ERROR")
        


    def clear_task_queue(self):
        """
        Clears the task queue.
        """
        self.tasks_executing = []

    def clear_current_task(self):
        """
        Clears the current task.
        """
        if len(self.tasks_executing) > 0:
            self.tasks_executing.pop(0)
        else:
            # log
            self._node.get_logger().error("No tasks executing")
            return None
        
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
        
    def get_current_task_status(self):
        """
        Returns the status of the current task.
        """
        if len(self.tasks_executing) > 0:
            return self.tasks_executing[0]["status"]
        else:
            # log
            self._node.get_logger().error("No tasks executing")
            return None
        
    def set_current_task_status(self, status):
        """
        Sets the status of the current task.
        """
        if len(self.tasks_executing) > 0:
            # Accept both enum and string for status
            if isinstance(status, WaraPSTaskStates):
                self.tasks_executing[0]["status"] = status.value
            else:
                self.tasks_executing[0]["status"] = status
        else:
            self._node.get_logger().error("No tasks executing")
            return None
        
    def move_task_to_past(self):
        """
        Moves the current task to the past tasks list.
        """
        if len(self.tasks_executing) > 0:
            self.past_tasks.append(self.tasks_executing[0])
            self.tasks_executing.pop(0)
        else:
            # log
            self._node.get_logger().error("No tasks executing")
            return None
        
    def __str__(self):
        """
        Returns the string representation of the WaraPSTaskHandler object. Should be a table of the tasks available, executing and past tasks.
        """

        # create a string representation of the tasks available
        tasks_available_str = "Tasks Available:\n"
        for task in self.tasks_available:
            tasks_available_str += f"\t{task['name']}\n"

        # create a string representation of the tasks executing
        tasks_executing_str = "Tasks Executing:\n"
        for task in self.tasks_executing:
            tasks_executing_str += f"\t{task['task']['name']}\n"

        # create a string representation of the past tasks
        past_tasks_str = "Past Tasks:\n"
        for task in self.past_tasks:
            past_tasks_str += f"\t{task['task']['name']}\n"

        return f"{tasks_available_str}{tasks_executing_str}" #{past_tasks_str}"
    
    def publish_feedback_to_current_task(self, feedback: str):
        """
        Publishes feedback to the current task.
        """
        if len(self.tasks_executing) > 0:
            # create a feedback message
            feedback_msg = {
                "agent-uuid": self._wara_ps_dict["agent-uuid"],
                "task-uuid": self.tasks_executing[0]["task-uuid"],
                "feedback": feedback,
                "status": self.tasks_executing[0]["status"]
            }
            msg = String()
            msg.data = json.dumps(feedback_msg)
            self._wara_ps_exec_feedback_pub.publish(msg)
            # self._node.get_logger().info('Published Feedback message')
        else:
            # log
            self._node.get_logger().error("No tasks executing")
            return None 

    def _bigredbutton_cb(self, data: String):
        """
        This method is called when the big red button is pressed.
        It will abort all tasks and set the aborted flag to True.
        """
        self._node.get_logger().info("Big Red Button pressed, aborting all tasks")
        self.emergency_flag = True
        # set all tasks executing to aborted
        for task in self.tasks_executing:
            task["status"] = WaraPSTaskStates.ABORTED.value
            self.past_tasks.append(task)
        
        # clear the executing tasks list
        self.tasks_executing = []

        # publish the response
        # create a response message
        response_msg = {
            "agent-uuid": self._wara_ps_dict["agent-uuid"],
            "response": "all tasks aborted",
            "response-to": data.data
        }
        msg = String()
        msg.data = json.dumps(response_msg)
        self._wara_ps_exec_response_pub.publish(msg)
        self._node.get_logger().info('Published Big Red Button response message')
        return
    
    def abort(self):
        """
        This method is called to abort all tasks and set the aborted flag to True.
        It is used to handle the big red button press.
        """
        self._bigredbutton_cb(String(data="Big Red Button pressed"))
        return True

    def _reset_emergency_cb(self, request, response):
        self.emergency_flag = False
        response.success = True
        response.message = "Emergency flag set to False."
        self._node.get_logger().info("Emergency flag reset to False by service call.")
        return response
    
    def get_available_tasks(self):
        """
        Returns the list of available tasks.
        """
        return self.tasks_available
    
    def current_time(self):
        """
        Returns the current time in seconds.
        """
        return self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9