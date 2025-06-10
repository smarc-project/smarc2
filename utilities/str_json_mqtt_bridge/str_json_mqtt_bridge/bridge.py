#!/usr/bin/python3

import typing
import rclpy, rclpy.node
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import json
import ast


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
        self._rosnode.create_subscription(String, topic, self._ros_cb, 10)
        self._rosnode.get_logger().info(f"ROS->MQTT: {self._ros_topic}->{self._mqtt_topic}")

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
        self._rosnode.get_logger().info(f"Re-subscribing to {self._ros_topic} after reconnect")
        # no need to unsubscribe, ros topics are persistent and will not be removed
        self._rosnode.create_subscription(String, self._ros_topic, self._ros_cb, 10)

    def on_disconnect(self):
        self._rosnode.get_logger().info(f"Unsubscribing from {self._ros_topic} on disconnect")
        # no need to unsubscribe, ros topics are persistent and will not be removed
        self._rosnode.destroy_subscription(self._ros_topic)


class MqttToRos:
    def __init__(self, rosnode: rclpy.node.Node, mqttclient: mqtt.Client, topic: str, mqtt_namespace: str):
        self._rosnode = rosnode
        self._mqttclient = mqttclient
        self._ros_topic = topic
        self._rospub = self._rosnode.create_publisher(String, self._ros_topic, 10)
        self._mqtt_topic = f"{mqtt_namespace}/{topic}"
        self._mqttclient.subscribe(self._mqtt_topic)
        self._mqttclient.message_callback_add(self._mqtt_topic, self._mqtt_cb)
        self._rosnode.get_logger().info(f"MQTT->ROS: {self._mqtt_topic}->{self._ros_topic}")

    def _mqtt_cb(self, client: mqtt.Client, userdata: typing.Dict, mqtt_msg: mqtt.MQTTMessage):
        ros_msg = String()
        ros_msg.data = mqtt_msg.payload.decode()
        self._rosnode.get_logger().info(f"{self._mqtt_topic}-->{self._ros_topic}: {ros_msg.data}")
        self._rospub.publish(ros_msg)

    def on_reconnect(self):
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

        ros_to_mqtt_topics = node.get_parameter("mqtt.to_mqtt").value
        mqtt_to_ros_topics = node.get_parameter("mqtt.to_ros").value
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
        for bridge in self.ros_to_mqtt_bridges:
            bridge.on_reconnect()

    def _on_disconnect(self, client, userdata, response_code):
        self.node.get_logger().info('MQTT disconnected')
        # unsubscribe from MQTT topics
        for bridge in self.mqtt_to_ros_bridges:
            bridge.on_disconnect()
        for bridge in self.ros_to_mqtt_bridges:
            bridge.on_disconnect()


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("waraps_bridge",
                             allow_undeclared_parameters=True, 
                             automatically_declare_parameters_from_overrides=True)
    mqtt_node = WaraMQTTNode(node)
    mqtt_node.run()