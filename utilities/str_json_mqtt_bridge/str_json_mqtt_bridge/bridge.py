#!/usr/bin/python3

import threading
import typing
import rclpy, rclpy.node
from std_msgs.msg import String
from smarc_msgs.msg import Topics
from smarc_utilities.topic_utils import node_string_topics_under
import paho.mqtt.client as mqtt
import json
import ast

from str_json_mqtt_bridge.names import ALL_AGENTS, mirror_target, mqtt_sensor_folder, unit_and_agent


# lifted from the mqtt_bridge package
def mqtt_client_factory(params: typing.Dict) -> mqtt.Client:
    """ MQTT Client factory """
    def param_to_value(param_dict) -> typing.Dict:
        return {k: v.value for k, v in param_dict.items()}

    # create client
    client_params = params.get('client', {})
    client_params = param_to_value(client_params)
    client = mqtt.Client(**client_params)

    # configure tls
    tls_params = params.get('tls', {})
    if tls_params:
        tls_params = param_to_value(tls_params)
        tls_insecure = tls_params.pop('tls_insecure', False)
        client.tls_set(**tls_params)
        client.tls_insecure_set(tls_insecure)

    # configure username and password
    account_params = params.get('account', {})
    if account_params:
        account_params = param_to_value(account_params)
        client.username_pw_set(**account_params)

    # configure message params
    message_params = params.get('message', {})
    if message_params:
        message_params = param_to_value(message_params)
        inflight = message_params.get('max_inflight_messages')
        if inflight is not None:
            client.max_inflight_messages_set(inflight)
        queue_size = message_params.get('max_queued_messages')
        if queue_size is not None:
            client.max_queued_messages_set(queue_size)
        retry = message_params.get('message_retry')
        if retry is not None:
            client.message_retry_set(retry)

    # configure userdata
    userdata = params.get('userdata', {})
    if userdata:
        userdata = param_to_value(userdata)
        client.user_data_set(userdata)

    # configure will params
    will_params = params.get('will', {})
    if will_params:
        will_params = param_to_value(will_params)
        client.will_set(**will_params)

    return client



class RosToMqtt:
    def __init__(self, rosnode: rclpy.node.Node, mqttclient: mqtt.Client, ros_topic: str, mqtt_topic: str):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self.ros_topic = ros_topic
        self.mqtt_topic = mqtt_topic
        self._subscription = None

    def _ros_cb(self, msg: String):
        # We do this clownshow because ros strings can not contain valid json string inside
        # since ros uses single quotes for strings and json requires double quotes
        # so if the first character is a single quote, we assume the publisher of this string put their json string inside a ros string
        # before sending it
        # otherwise, the string is likely coming from json.dumps put into a ros string, where double quotes become single quotes
        # so we convert the ros string to a python dict, then convert that to a json string
        # self._rosnode.get_logger().info(f"{self._ros_topic}-->{self._mqtt_topic}: {msg.data}")
        if(msg.data[0] == "'" or msg.data[0] == '"'):
            json_str = msg.data[1:-1] # remove the single quotes so the inner string is a valid json string
        else:
            try:
                json_obj = ast.literal_eval(msg.data)
            except (SyntaxError, ValueError) as e:
                self._rosnode.get_logger().error(f"Error converting to python dict: {msg.data}")
                return
            try:
                json_str = json.dumps(json_obj) 
            except TypeError as e:
                self._rosnode.get_logger().error(f"Error converting to json: {e}, non-json type: {type(json_obj)}")
                return

        # self._rosnode.get_logger().info(f"{self.ros_topic}-->{self.mqtt_topic}: {json_str}")
        self._mqttclient.publish(self.mqtt_topic, json_str)

    def on_reconnect(self):
        """ Subscribes to the ROS topic. A second call while subscribed does nothing. """
        if self._subscription is not None:
            return
        self._rosnode.get_logger().info(f"ROS->MQTT: {self.ros_topic} -> {self.mqtt_topic}")
        self._subscription = self._rosnode.create_subscription(String, self.ros_topic, self._ros_cb, 10)

    def on_disconnect(self):
        self._rosnode.get_logger().info(f"Unsubscribing from {self.ros_topic} on disconnect")
        if self._subscription is not None:
            self._rosnode.destroy_subscription(self._subscription)
            self._subscription = None


def discover_sensor_bridges(rosnode, mqttclient, mqtt_namespace, robot_root, bridges):
    """Open a RosToMqtt for each String topic under the sensor prefix that has none yet.

    ``robot_root`` is '/<robot_name>'; the sensor topics hang off it as
    '/<robot_name>/waraps/sensor/<name>', published by the robot's own nodes
    (another robot's bridge mirroring us from its namespace does not count,
    or the message would go round the broker forever). ``bridges`` is the
    live list of RosToMqtt; new ones are appended and returned. Topics the
    yaml already lists are in that list and are not opened twice.
    """
    known = {bridge.ros_topic for bridge in bridges}
    folder = mqtt_sensor_folder(Topics.WARA_PS_SENSOR_PREFIX)
    opened = []
    for found in node_string_topics_under(rosnode, robot_root, Topics.WARA_PS_SENSOR_PREFIX):
        if found.absolute in known:
            continue
        bridge = RosToMqtt(rosnode, mqttclient, found.absolute, f"{mqtt_namespace}/{folder}/{found.name}")
        bridges.append(bridge)
        opened.append(bridge)
        if mqttclient.is_connected():
            bridge.on_reconnect()
    return opened


class MqttAgentsToRos:
    """Other agents' sensor strings, taken off the broker and republished on
    '/<agent>/waraps/sensor/<name>' so nodes on this vehicle can read them.

    ``agents`` are broker ids like 'kkalem_sam' (the last segment of their
    mqtt namespace). '#' means every agent in our unit. Our own agent is never
    mirrored back.
    """

    def __init__(self, rosnode: rclpy.node.Node, mqttclient: mqtt.Client, mqtt_namespace: str, agents: list[str]):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self._unit, self._own_agent = unit_and_agent(mqtt_namespace)
        folder = mqtt_sensor_folder(Topics.WARA_PS_SENSOR_PREFIX)
        wanted = ['+'] if ALL_AGENTS in agents else [a for a in agents if a != self._own_agent]
        self.filters = [f"{self._unit}/{agent}/{folder}/#" for agent in wanted]
        self._publishers: dict[str, rclpy.publisher.Publisher] = {}
        self._lock = threading.Lock()

    def on_reconnect(self):
        for mqtt_filter in self.filters:
            self._rosnode.get_logger().info(f"MQTT->ROS agents: {mqtt_filter}")
            self._mqttclient.subscribe(mqtt_filter)
            self._mqttclient.message_callback_add(mqtt_filter, self._mqtt_cb)

    def on_disconnect(self):
        for mqtt_filter in self.filters:
            self._mqttclient.unsubscribe(mqtt_filter)
            self._mqttclient.message_callback_remove(mqtt_filter)

    def _mqtt_cb(self, client, userdata, mqtt_msg: mqtt.MQTTMessage):
        self.mirror(mqtt_msg.topic, mqtt_msg.payload.decode())

    def mirror(self, mqtt_topic: str, payload: str) -> str | None:
        """Publish one broker message into ROS. Returns the ROS topic, or None if it was not ours to mirror."""
        ros_topic = mirror_target(mqtt_topic, self._unit, self._own_agent, Topics.WARA_PS_SENSOR_PREFIX)
        if ros_topic is None:
            return None
        with self._lock:
            publisher = self._publishers.get(ros_topic)
            if publisher is None:
                self._rosnode.get_logger().info(f"MQTT->ROS: {mqtt_topic} -> {ros_topic}")
                publisher = self._rosnode.create_publisher(String, ros_topic, 10)
                self._publishers[ros_topic] = publisher
        publisher.publish(String(data=payload))
        return ros_topic


class MqttToRos:
    def __init__(self, rosnode: rclpy.node.Node, mqttclient: mqtt.Client, topic: str, mqtt_namespace: str):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self._ros_topic = topic
        self._rospub = self._rosnode.create_publisher(String, self._ros_topic, 10)
        self._mqtt_topic = f"{mqtt_namespace}/{topic}"
        # self._mqttclient.subscribe(self._mqtt_topic)
        # self._mqttclient.message_callback_add(self._mqtt_topic, self._mqtt_cb)
        # self._rosnode.get_logger().info(f"MQTT->ROS: {self._mqtt_topic}->{self._ros_topic}")

    def _mqtt_cb(self, client: mqtt.Client, userdata: typing.Dict, mqtt_msg: mqtt.MQTTMessage):
        ros_msg = String()
        ros_msg.data = mqtt_msg.payload.decode()
        self._rosnode.get_logger().info(f"{self._mqtt_topic}-->{self._ros_topic}: {ros_msg.data}")
        self._rospub.publish(ros_msg)

    def on_reconnect(self):
        """ Re-subscribes to the MQTT topic after a reconnect """
        self._rosnode.get_logger().info(f"Re-subscribing to {self._mqtt_topic} after reconnect")
        self._mqttclient.subscribe(self._mqtt_topic)
        self._mqttclient.message_callback_add(self._mqtt_topic, self._mqtt_cb)

    def on_disconnect(self):
        self._rosnode.get_logger().info(f"Unsubscribing from {self._mqtt_topic} on disconnect")
        self._mqttclient.unsubscribe(self._mqtt_topic)
        self._mqttclient.message_callback_remove(self._mqtt_topic)

class WaraMQTTNode:
    def __init__(self, node: rclpy.node.Node):
        self.node = node

        # construct the bridge the same way as in app.py of the mqtt_bridge package
        mqtt_client_params = {
            "client" :  node.get_parameters_by_prefix("mqtt.client"),
            "tls" : node.get_parameters_by_prefix("mqtt.tls"),
            "account" : node.get_parameters_by_prefix("mqtt.account"),
            "userdata" : node.get_parameters_by_prefix("mqtt.userdata"),
            "message" : node.get_parameters_by_prefix("mqtt.message"),
            "will"  : node.get_parameters_by_prefix("mqtt.will")
        }
        self._mqtt_client = mqtt_client_factory(mqtt_client_params)
        mqtt_connection_params = node.get_parameters_by_prefix("mqtt.connection")
        # not sure why, but the original code updates the dictionary in place like this
        for key in mqtt_connection_params.keys():
            mqtt_connection_params.update({key : mqtt_connection_params[key].value})

        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect

        try:
            ros_to_mqtt_topics = node.get_parameter("mqtt.to_mqtt").value
        except:
            self._log("No mqtt.to_mqtt parameter found, defaulting to empty list")
            ros_to_mqtt_topics = []
        try:
            mqtt_to_ros_topics = node.get_parameter("mqtt.to_ros").value
        except:
            self._log("No mqtt.to_ros parameter found, defaulting to empty list")
            mqtt_to_ros_topics = []

        # with allow_undeclared_parameters, a parameter that was never set reads as None
        to_ros_agents = node.get_parameter("mqtt.to_ros_agents").value or []
        robot_name = node.get_parameter("robot_name").value
        self._robot_root = f"/{robot_name}" if robot_name else None
        if self._robot_root is None:
            self._log("No robot_name parameter, sensor topics under waraps/sensor will not be discovered")

        self._mqtt_namespace = node.get_parameter("mqtt.namespace").value
        self._log(f"ROS to MQTT topics: {ros_to_mqtt_topics}")
        self._log(f"MQTT to ROS topics: {mqtt_to_ros_topics}")
        self._log(f"MQTT to ROS agents: {to_ros_agents}")
        self._log(f"MQTT namespace: {self._mqtt_namespace}")
        
        while True:
            try:
                self._log(f"Connecting to MQTT broker at {mqtt_connection_params['host']}:{mqtt_connection_params['port']}")
                self._mqtt_client.connect(**mqtt_connection_params)
                break
            except Exception as e:
                self._log(f'Error connecting to MQTT: {e}')
                self._log(f'Retrying in 5 seconds')
                rclpy.spin_once(node, timeout_sec=5)

        self.ros_to_mqtt_bridges = [
            RosToMqtt(node, self._mqtt_client, node.resolve_topic_name(topic), f"{self._mqtt_namespace}/{topic}")
            for topic in ros_to_mqtt_topics]
        self.mqtt_to_ros_bridges = [MqttToRos(node, self._mqtt_client, topic, self._mqtt_namespace) for topic in mqtt_to_ros_topics]
        self.agents_to_ros = MqttAgentsToRos(node, self._mqtt_client, self._mqtt_namespace, to_ros_agents)
        if self._robot_root is not None:
            self._discover_timer = node.create_timer(1.0, self._discover_sensor_topics)


    def _discover_sensor_topics(self):
        for bridge in discover_sensor_bridges(self.node, self._mqtt_client, self._mqtt_namespace,
                                             self._robot_root, self.ros_to_mqtt_bridges):
            self._log(f"Found sensor topic {bridge.ros_topic}")

    def _log(self, msg:str):
        self.node.get_logger().info(f'[WaraMQTTNode] {msg}')

    def run(self):
        # start MQTT loop
        self._mqtt_client.loop_start()

        try:
            rclpy.spin(self.node)
        except KeyboardInterrupt:
            self.node.get_logger().info('Ctrl-C detected')
            self._mqtt_client.disconnect()
            self._mqtt_client.loop_stop()

        # destroy the node
        self.node.destroy_node()


    def _on_connect(self, client, userdata, flags, response_code):
        self.node.get_logger().info('MQTT connected')
        # re-subscribe to MQTT topics
        for bridge in self.mqtt_to_ros_bridges:
            bridge.on_reconnect()
        for bridge in list(self.ros_to_mqtt_bridges):   # the discovery timer appends from another thread
            bridge.on_reconnect()
        self.agents_to_ros.on_reconnect()

    def _on_disconnect(self, client, userdata, response_code):
        self.node.get_logger().info('MQTT disconnected')
        # unsubscribe from MQTT topics
        for bridge in self.mqtt_to_ros_bridges:
            bridge.on_disconnect()
        for bridge in list(self.ros_to_mqtt_bridges):
            bridge.on_disconnect()
        self.agents_to_ros.on_disconnect()


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("waraps_bridge",
                             allow_undeclared_parameters=True, 
                             automatically_declare_parameters_from_overrides=True)
    mqtt_node = WaraMQTTNode(node)
    mqtt_node.run()