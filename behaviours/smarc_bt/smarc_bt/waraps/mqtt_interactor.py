from typing import Type
# from smarc_msgs.msg import Topics
from smarc_bt.waraps.waraps_vehicle import WaraPSVehicle

class HasMQTTInteractor:
    """
    This class is used to mark a class as having an MQTT interactor. This is used to make sure that the class has the methods that are needed for the MQTT interactor to work.
    """
    def __init__(self):
        self._mqtt_interactor = None

    @property
    def mqtt_interactor(self):
        return self._mqtt_interactor

    @mqtt_interactor.setter
    def mqtt_interactor(self, value):
        self._mqtt_interactor = value

class MQTTInteractor:
    def __init__(self, vehicle: Type[WaraPSVehicle]):
        """
        A class to handle the parts of the BT that need to interact with MQTT. This will later double up as the Mission Command and Updator.

        It is the job of this interactor to listen and publish to the relevant ROS topics connected to the MQTT bridge, and handle WARA-PS actions.
        """
        self._vehicle = vehicle
        # self._heartbeat_topic = Topics.WARA_PS_HEARTBEAT_TOPIC
        # self.pulse_rate = 1.0 # time between consecutive heartbeats
        self.pulse_rate = self._vehicle.wara_ps_dict()["pulse_rate"] 
        
    def publish_heartbeat(self, prev_time: float, now_time: float):
        """
        Publish a heartbeat to the MQTT topic. Right now, this happens through the vehicle container, since the information needed for this lives almost exclusively there.
        """
        # Assuming you have an MQTT client set up
        # client.publish(self._heartbeat_topic, "Heartbeat message")

        return self._vehicle.wara_ps_heartbeat(prev_time, now_time)
    
    def wara_ps_lvl1(self, prev_time, now_time):
        """
        Publish sensor information to the MQTT topic. Right now, this happens through the vehicle container, since the information needed for this lives almost exclusively there.
        """
        # Assuming you have an MQTT client set up
        # client.publish(self._sensor_topic, "Sensor message")

        return self._vehicle.wara_ps_lvl1(prev_time, now_time)