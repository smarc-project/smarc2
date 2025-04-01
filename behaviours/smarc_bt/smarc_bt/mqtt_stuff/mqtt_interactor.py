from typing import Type
# from smarc_msgs.msg import Topics
from smarc_bt.vehicles.vehicle import IVehicleStateContainer
from smarc_msgs.msg import Topics

class MQTTInteractor:
    def __init__(self, vehicle: Type[IVehicleStateContainer]):
        """
        A class to handle the parts of the BT that need to interact with MQTT. This will later double up as the Mission Command and Updator.

        It is the job of this interactor to listen and publish to the relevant ROS topics connected to the MQTT bridge, and handle WARA-PS actions.
        """
        self._vehicle = vehicle
        # self._heartbeat_topic = Topics.WARA_PS_HEARTBEAT_TOPIC
        self.pulse_rate = 1.0 # time between consecutive heartbeats 
        
    def publish_heartbeat(self, now_time: float, pulse_rate: float):
        """
        Publish a heartbeat to the MQTT topic. Right now, this happens through the vehicle container, since the information needed for this lives almost exclusively there.
        """
        # Assuming you have an MQTT client set up
        # client.publish(self._heartbeat_topic, "Heartbeat message")

        self._vehicle.wara_ps_heartbeat(now_time, pulse_rate)
        return True
    