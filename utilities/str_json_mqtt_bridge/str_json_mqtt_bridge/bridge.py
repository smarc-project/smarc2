#!/usr/bin/python3

import typing
import rclpy, rclpy.node
import paho.mqtt.client as mqtt
import json


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
        self._log(f'node params: {node.get_parameters_by_prefix("")}')
        self.mqtt_client = mqtt_client_factory(mqtt_client_params)
        mqtt_connection_params = node.get_parameters_by_prefix("mqtt.connection")
        # not sure why, but the original code updates the dictionary in place like this
        for key in mqtt_connection_params.keys():
            mqtt_connection_params.update({key : mqtt_connection_params[key].value})

        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.connect(**mqtt_connection_params)

    def _log(self, msg:str):
        self.node.get_logger().info(f'[WaraMQTTNode] {msg}')

    def run(self):
        # start MQTT loop
        self.mqtt_client.loop_start()

        try:
            rclpy.spin(self.node)
        except KeyboardInterrupt:
            self.node.get_logger().info('Ctrl-C detected')
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()

        self.mqtt_client.destroy_node()


    def _on_connect(self, client, userdata, flags, response_code):
        self.node.get_logger().info('MQTT connected')

    def _on_disconnect(self, client, userdata, response_code):
        self.node.get_logger().info('MQTT disconnected')


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("wara_mqtt_node")
    mqtt_node = WaraMQTTNode(node)
    mqtt_node.run()