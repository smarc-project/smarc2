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


_ALL_AGENTS = '#'


def normalize_namespace(namespace):
    if not namespace or namespace == '/':
        return '/'
    text = namespace if namespace.startswith('/') else '/' + namespace
    return text.rstrip('/')


def endpoint_belongs_to_node(node_name, node_namespace, my_name, my_namespace):
    return node_name == my_name and normalize_namespace(node_namespace) == normalize_namespace(my_namespace)


def topic_in_namespace(absolute, namespace):
    ns = normalize_namespace(namespace)
    if ns == '/':
        return absolute.startswith('/')
    return absolute == ns or absolute.startswith(ns + '/')


def sensor_layout(position_topic):
    """Return (ros_root, sensor_dir) for Topics.WARA_PS_SENSOR_POSITION_TOPIC.

    'waraps/sensor/position' -> ('waraps', 'sensor').
    """
    prefix, sep, leaf = position_topic.rpartition('/')
    if not sep or not prefix or not leaf:
        return '', ''
    ros_root, sep, sensor_dir = prefix.partition('/')
    if not sep or not ros_root or not sensor_dir:
        return '', ''
    return ros_root, sensor_dir


def unit_prefix_and_agent(mqtt_namespace):
    """Split 'context/unit/domain/realsim/agent' into the unit and the agent."""
    text = (mqtt_namespace or '').strip().strip('/')
    unit, sep, agent = text.rpartition('/')
    if not sep or not unit or not agent or '/' in agent:
        return '', ''
    return unit, agent


def normalize_agents(value):
    """Accept a list, one name, or a comma-separated string. '#' means every agent."""
    if value is None:
        return []
    if isinstance(value, str):
        raw = value.split(',')
    else:
        raw = []
        for item in value:
            if isinstance(item, str):
                raw.extend(item.split(','))
    agents = []
    for agent in raw:
        name = agent.strip()
        if not name or name in agents:
            continue
        agents.append(name)
    return agents


def listen_filters(mqtt_namespace, agents, position_topic):
    """MQTT subscriptions for sensor topics of the named agents.

    '#' subscribes to every agent in the unit except this bridge's own agent.
    Returns (filters, agents_to_skip).
    """
    unit, local_agent = unit_prefix_and_agent(mqtt_namespace)
    _root, sensor_dir = sensor_layout(position_topic)
    names = normalize_agents(agents)
    if not unit or not sensor_dir or not names:
        return [], set()
    if _ALL_AGENTS in names:
        return [f'{unit}/+/{sensor_dir}/#'], {local_agent}
    filters = []
    for agent in names:
        if agent == _ALL_AGENTS or agent == '+' or '/' in agent:
            continue
        filters.append(f'{unit}/{agent}/{sensor_dir}/#')
    return filters, set()


def parse_listened_sensor(mqtt_topic, mqtt_namespace, position_topic):
    """Map a broker sensor topic to (agent, absolute ROS topic).

    Broker: '<unit>/<agent>/sensor/<name>' (name may contain slashes).
    ROS:    '/<agent>/waraps/sensor/<name>'.
    """
    unit, _local = unit_prefix_and_agent(mqtt_namespace)
    ros_root, sensor_dir = sensor_layout(position_topic)
    if not unit or not ros_root or not sensor_dir or not mqtt_topic:
        return None
    prefix = unit + '/'
    if not mqtt_topic.startswith(prefix):
        return None
    agent, sep, tail = mqtt_topic[len(prefix):].partition('/')
    if not sep or not agent or agent in ('+', _ALL_AGENTS) or '/' in agent:
        return None
    sensor_head = sensor_dir + '/'
    if not tail.startswith(sensor_head):
        return None
    sensor_name = tail[len(sensor_head):]
    if not sensor_name or sensor_name.startswith('/'):
        return None
    return agent, f'/{agent}/{ros_root}/{sensor_dir}/{sensor_name}'


class MqttAgentsToRos:
    """Publish other agents' sensor strings into '/<agent>/waraps/sensor/...'."""

    def __init__(self, rosnode, mqttclient, mqtt_namespace, agents):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self._mqtt_namespace = mqtt_namespace
        self._position_topic = Topics.WARA_PS_SENSOR_POSITION_TOPIC
        self._filters, self._skip_agents = listen_filters(
            mqtt_namespace, agents, self._position_topic)
        self._publishers = {}
        self._lock = threading.Lock()
        self._subscribed = False

    def on_reconnect(self):
        with self._lock:
            if self._subscribed or not self._filters:
                return
            self._subscribed = True
        for mqtt_filter in self._filters:
            self._rosnode.get_logger().info(f"MQTT->ROS sensors: {mqtt_filter}")
            self._mqttclient.subscribe(mqtt_filter)
            self._mqttclient.message_callback_add(mqtt_filter, self._mqtt_cb)

    def on_disconnect(self):
        with self._lock:
            was_subscribed = self._subscribed
            self._subscribed = False
        if not was_subscribed:
            return
        for mqtt_filter in self._filters:
            self._mqttclient.unsubscribe(mqtt_filter)
            self._mqttclient.message_callback_remove(mqtt_filter)

    def _mqtt_cb(self, client, userdata, mqtt_msg):
        payload = mqtt_msg.payload.decode() if isinstance(mqtt_msg.payload, bytes) else mqtt_msg.payload
        self.handle(mqtt_msg.topic, payload)

    def handle(self, mqtt_topic, payload):
        parsed = parse_listened_sensor(mqtt_topic, self._mqtt_namespace, self._position_topic)
        if parsed is None:
            return None
        agent, ros_topic = parsed
        if agent in self._skip_agents:
            return None
        if topic_in_namespace(ros_topic, self._rosnode.get_namespace()):
            return None
        publisher = self._publisher(ros_topic)
        message = String()
        message.data = payload
        publisher.publish(message)
        return ros_topic

    def _publisher(self, ros_topic):
        with self._lock:
            publisher = self._publishers.get(ros_topic)
            if publisher is None:
                self._rosnode.get_logger().info(f"MQTT->ROS: {ros_topic}")
                publisher = self._rosnode.create_publisher(String, ros_topic, 10)
                self._publishers[ros_topic] = publisher
            return publisher


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
        try:
            listen_agents = node.get_parameter("mqtt.to_ros_agents").value
        except Exception:
            listen_agents = []
        self._log(f"MQTT to ROS agents: {normalize_agents(listen_agents)}")
        
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
        self._agent_ingress = MqttAgentsToRos(node, self._mqtt_client, self._mqtt_namespace, listen_agents)
        self._sensor_discover_timer = node.create_timer(1.0, self._discover_sensor_topics)
        self._discover_sensor_topics()



    def _log(self, msg:str):
        self.node.get_logger().info(f'[WaraMQTTNode] {msg}')

    def _is_string_publisher(self, topic: str) -> bool:
        """True when some other node publishes this topic as a String.

        Publishers created by this bridge (MQTT mirrors) are ignored so a
        listened agent is not forwarded back to the broker.
        """
        my_name = self.node.get_name()
        my_namespace = self.node.get_namespace()
        for info in self.node.get_publishers_info_by_topic(topic):
            if info.topic_type != _STRING_MSG:
                continue
            if endpoint_belongs_to_node(info.node_name, info.node_namespace, my_name, my_namespace):
                continue
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
        self._agent_ingress.on_reconnect()

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
        self._agent_ingress.on_disconnect()


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("waraps_bridge",
                             allow_undeclared_parameters=True, 
                             automatically_declare_parameters_from_overrides=True)
    mqtt_node = WaraMQTTNode(node)
    mqtt_node.run()