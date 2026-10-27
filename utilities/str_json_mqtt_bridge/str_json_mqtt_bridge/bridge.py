#!/usr/bin/python3

import threading
import typing
import rclpy, rclpy.node
from std_msgs.msg import String
from smarc_msgs.msg import Topics
import paho.mqtt.client as mqtt
import json
import ast

# Keep identical to string_topics_under_sensor in wasp_bt.waraps.waraps_vehicle.
_STRING_MSG = 'std_msgs/msg/String'


def string_topics_under_sensor(topics, namespace, position_topic, is_string_publisher):
    """String publishers under the WARA-PS sensor prefix, inside ``namespace``.

    ``position_topic`` is Topics.WARA_PS_SENSOR_POSITION_TOPIC. The prefix is
    that name with the last segment removed. Relative names may contain
    slashes. Returns (relative_name, sensor_name) sorted by relative name.
    """
    head, sep, tail = position_topic.rpartition('/')
    if not sep or not head or not tail:
        return []
    needle = '/' + head + '/'

    ns = namespace.rstrip('/')
    found = []
    for absolute, types in topics:
        if _STRING_MSG not in types:
            continue
        if not isinstance(absolute, str) or not absolute.startswith('/'):
            continue
        if ns in ('', '/'):
            relative = absolute[1:]
        elif absolute.startswith(ns + '/'):
            relative = absolute[len(ns) + 1:]
        else:
            continue
        if not relative:
            continue
        idx = absolute.find(needle)
        if idx < 0:
            continue
        sensor_name = absolute[idx + len(needle):]
        if not sensor_name:
            continue
        if not is_string_publisher(absolute):
            continue
        found.append((relative, sensor_name))
    found.sort(key=lambda item: item[0])
    return found


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
    def __init__(self, rosnode: rclpy.node.Node, mqttclient: mqtt.Client, topic: str, mqtt_namespace: str):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self._ros_topic = topic
        self._mqtt_topic = f"{mqtt_namespace}/{topic}"
        self._subscription = None
        self._lock = threading.Lock()
        # self._rosnode.create_subscription(String, topic, self._ros_cb, 10)
        # self._rosnode.get_logger().info(f"ROS->MQTT: {self._ros_topic}->{self._mqtt_topic}")

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

        # self._rosnode.get_logger().info(f"{self._ros_topic}-->{self._mqtt_topic}: {json_str}")
        self._mqttclient.publish(self._mqtt_topic, json_str)

    def on_reconnect(self):
        """ Subscribes to the ROS topic once. A second call does not add another subscription. """
        with self._lock:
            if self._subscription is not None:
                return
            self._rosnode.get_logger().info(f"Re-subscribing to {self._ros_topic} after reconnect")
            self._subscription = self._rosnode.create_subscription(String, self._ros_topic, self._ros_cb, 10)

    def on_disconnect(self):
        self._rosnode.get_logger().info(f"Unsubscribing from {self._ros_topic} on disconnect")
        with self._lock:
            subscription = self._subscription
            self._subscription = None
        if subscription is not None:
            self._rosnode.destroy_subscription(subscription)


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
        self._bridges_lock = threading.Lock()
        self.ros_to_mqtt_bridges = []
        self.mqtt_to_ros_bridges = []

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

        self._mqtt_namespace = node.get_parameter("mqtt.namespace").value
        self._log(f"ROS to MQTT topics: {ros_to_mqtt_topics}")
        self._log(f"MQTT to ROS topics: {mqtt_to_ros_topics}")
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

        self.ros_to_mqtt_bridges = [RosToMqtt(node, self._mqtt_client, topic, self._mqtt_namespace) for topic in ros_to_mqtt_topics]
        self.mqtt_to_ros_bridges = [MqttToRos(node, self._mqtt_client, topic, self._mqtt_namespace) for topic in mqtt_to_ros_topics]
        self._sensor_discover_timer = node.create_timer(1.0, self._discover_sensor_topics)
        self._discover_sensor_topics()



    def _log(self, msg:str):
        self.node.get_logger().info(f'[WaraMQTTNode] {msg}')

    def _is_string_publisher(self, topic: str) -> bool:
        for info in self.node.get_publishers_info_by_topic(topic):
            if info.topic_type == _STRING_MSG:
                return True
        return False

    def _discover_sensor_topics(self):
        """Open one RosToMqtt for each new String topic under the sensor prefix.

        Heartbeat, exec, and tst stay on the yaml list. A topic that yaml
        already lists is not subscribed a second time.
        """
        found = string_topics_under_sensor(
            self.node.get_topic_names_and_types(),
            self.node.get_namespace(),
            Topics.WARA_PS_SENSOR_POSITION_TOPIC,
            self._is_string_publisher,
        )
        for relative, _sensor_name in found:
            self._open_ros_to_mqtt(relative)

    def _open_ros_to_mqtt(self, relative: str):
        with self._bridges_lock:
            for bridge in self.ros_to_mqtt_bridges:
                if bridge._ros_topic == relative:
                    return
            bridge = RosToMqtt(self.node, self._mqtt_client, relative, self._mqtt_namespace)
            self.ros_to_mqtt_bridges.append(bridge)
        self._log(f"ROS to MQTT sensor topic: {relative}")
        if self._mqtt_client.is_connected():
            bridge.on_reconnect()

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
        with self._bridges_lock:
            ros_to_mqtt = list(self.ros_to_mqtt_bridges)
            mqtt_to_ros = list(self.mqtt_to_ros_bridges)
        for bridge in mqtt_to_ros:
            bridge.on_reconnect()
        for bridge in ros_to_mqtt:
            bridge.on_reconnect()

    def _on_disconnect(self, client, userdata, response_code):
        self.node.get_logger().info('MQTT disconnected')
        # unsubscribe from MQTT topics
        with self._bridges_lock:
            ros_to_mqtt = list(self.ros_to_mqtt_bridges)
            mqtt_to_ros = list(self.mqtt_to_ros_bridges)
        for bridge in mqtt_to_ros:
            bridge.on_disconnect()
        for bridge in ros_to_mqtt:
            bridge.on_disconnect()


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("waraps_bridge",
                             allow_undeclared_parameters=True, 
                             automatically_declare_parameters_from_overrides=True)
    mqtt_node = WaraMQTTNode(node)
    mqtt_node.run()