import json
from typing import Type
from rclpy.node import Node
from std_msgs.msg import String
from smarc_msgs.msg import Topics
from wasp_bt.vehicles.sensor import Sensor, SensorNames
from wasp_bt.vehicles.vehicle import IVehicleState


class WaraPSVehicle():

    def __init__(self, 
                 node:Node, 
                 vehicle_state:Type[IVehicleState], wara_ps_dict:Type[dict]):
                        
        # private variables
        self._node = node
        self._vehicle_state = vehicle_state

        self._logger = node.get_logger()

        # Publishers for Level 1 WARA-PS topics
        self._wara_ps_heartbeat_pub = node.create_publisher(String, Topics.WARA_PS_HEARTBEAT_TOPIC, 10)
        self._wara_ps_position_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_POSITION_TOPIC, 10)
        self._wara_ps_heading_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_HEADING_TOPIC, 10)
        self._wara_ps_course_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_COURSE_TOPIC, 10)
        self._wara_ps_speed_pub = node.create_publisher(String, Topics.
        WARA_PS_SENSOR_SPEED_TOPIC, 10)
        self._wara_ps_roll_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_ROLL_TOPIC, 10)
        self._wara_ps_pitch_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_PITCH_TOPIC, 10)
        self._wara_ps_depth_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_DEPTH_TOPIC, 10)

        self._wara_ps_sensor_info_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_INFO_TOPIC, 10)



        self._wara_ps_dict = wara_ps_dict

        self._heartbeat_data = {
            "agent-type": self._wara_ps_dict["agent-type"],
            "agent-uuid": self._wara_ps_dict["agent-uuid"],
            "levels": self._wara_ps_dict["levels"],
            "name": self._wara_ps_dict["name"],
            "rate": self._wara_ps_dict["pulse_rate"],
            "stamp": "",
            # "stamp": self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9,
            "type": "HeartBeat"
        }

        self._sensor_info_data = {
            "name": self._wara_ps_dict["name"],
            "rate": self._wara_ps_dict["pulse_rate"],
            # TODO: this is VERY bad, ideally we should listen to topics under a "sensor" namespace and just replicate the structure
            "sensor-data-provided": [
                "position",
                "heading",
                "course",
                "speed",
                "roll",
                "pitch",    
                "depth",
                "executing_tasks"
            ],

        "stamp": "",
        "type": "SensorInfo"
        }

    @property
    def wara_ps_dict(self):
        """
        Returns the WaraPS dictionary that is used to handle the MQTT interactor.
        """
        return self._wara_ps_dict

    def wara_ps_heartbeat(self, now_time):
        
        # update the heartbeat data
        self._heartbeat_data["stamp"] = now_time
        
        # publish the heartbeat data
        msg = String()
        msg.data = json.dumps(self._heartbeat_data)
        self._wara_ps_heartbeat_pub.publish(msg)
        # self._node.get_logger().info('Published Heartbeat message')
        
        return True
    

    def wara_ps_lvl1(self, now_time):
        
        # 1. publish sensor info data

        self._sensor_info_data["stamp"] = now_time

        msg = String()
        msg.data = json.dumps(self._sensor_info_data)
        self._wara_ps_sensor_info_pub.publish(msg)

                                    
        try:
            position_msg = {
                "latitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lat'],
                "longitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lon'],
                # "altitude": -self._vehicle_state[SensorNames.DEPTH][0] if self._vehicle_state[SensorNames.DEPTH][0] is not None else 0,
                "altitude": self._vehicle_state[SensorNames.ALTITUDE][0],
                "type": "GeoPoint"
            }
            msg = String()
            msg.data = json.dumps(position_msg)
            self._wara_ps_position_pub.publish(msg)
            # self._node.get_logger().info('Published Position message')
        except Exception:
            self._node.get_logger().error("Failed to publish position data. Check if the vehicle state has valid position data.")
            


        #TODO: this stuff is strings, but wara-ps expects floats. Our json bridge only handles strings. Github Issue exists for this.

        # 3. publish course data
        try:
            course_msg = String()
            course_msg.data = f"{self._vehicle_state[SensorNames.COURSE_DEG][0]}"
            self._wara_ps_course_pub.publish(course_msg)
            # self._node.get_logger().info('Published Course message')
        except Exception:
            pass

        # 3.5 publish heading data
        try:
            heading_msg = String()
            heading_msg.data = f"{self._vehicle_state[SensorNames.GLOBAL_HEADING_DEG][0]}"
            # float
            self._wara_ps_heading_pub.publish(heading_msg)
            # self._node.get_logger().info('Published Heading message')
        except Exception:
            pass
        
        # 4. publish speed data
        try:
            speed_msg = String()
            speed_msg.data = f"{self._vehicle_state[SensorNames.SPEED][0]}"
            # speed_msg.data = "0.0
            # float
            self._wara_ps_speed_pub.publish(speed_msg)
            # self._node.get_logger().info('Published Speed message')
        except:
            pass

        # computation to get roll and pitch from orientation quaternion

        # # 5. publish roll data
        # roll_msg = String()
        # roll_msg.data = f"{self._vehicle_state[SensorNames.ORIENTATION_EULER]['roll']}"
        # # float
        # self._wara_ps_roll_pub.publish(roll_msg)
        # # self._node.get_logger().info('Published Roll message')

        # # 6. publish pitch data
        # pitch_msg = String()
        # pitch_msg.data = f"{self._vehicle_state[SensorNames.ORIENTATION_EULER]['pitch']}"
        # # float
        # self._wara_ps_pitch_pub.publish(pitch_msg)
        # # self._node.get_logger().info('Published Pitch message')

        # 7. publish depth data
        depth_msg = String()
        try:
            depth_msg.data = f"{self._vehicle_state[SensorNames.DEPTH][0]}"
        except:
            depth_msg.data = "-1"
        # float
        self._wara_ps_depth_pub.publish(depth_msg)
        # self._node.get_logger().info('Published Depth message')            

        return True
    
    
def main(args=None):
    import rclpy
    from rclpy.node import Node
    import uuid
    from wasp_bt.vehicles.ros_vehicle import ROSVehicle
    from wasp_bt.vehicles.smarc_vehicle import GenericSMaRCVehicle
    from wasp_bt.vehicles.vehicle import UnderwaterVehicleState


    rclpy.init(args=args)

    node = Node("waraps_vehicle_node")

    def ros_seconds_float() -> float:
        nonlocal node
        secs, nsecs = node.get_clock().now().seconds_nanoseconds()
        return float(secs) + float(nsecs) * 1e-9

    smarc_vehicle = GenericSMaRCVehicle(node, UnderwaterVehicleState)
    # smarc_vehicle = ROSVehicle(node, UnderwaterVehicleState)

    # Declare and get parameters with defaults
    node.declare_parameter("agent_type", "air")
    node.declare_parameter("levels", ["sensor", "direct_execution"])
    node.declare_parameter("pulse_rate", 1.0) # Hz
    node.declare_parameter("domain", "simulation")

    agent_type = node.get_parameter("agent_type").value
    levels = node.get_parameter("levels").value
    pulse_rate = node.get_parameter("pulse_rate").value
    robot_name = node.get_parameter("robot_name").value if node.has_parameter("robot_name") else "sam0"

    agent_waraps_dict = {
        "agent-type": agent_type,
        "agent-uuid": str(uuid.uuid4()),
        "levels": levels,
        "name": robot_name,
        "pulse_rate": pulse_rate,
    }

    wara_ps_vehicle = WaraPSVehicle(node, smarc_vehicle.vehicle_state, agent_waraps_dict)

    def wara_ps_level_1_comms():
        nonlocal wara_ps_vehicle
        # get the current time
        now_time = ros_seconds_float()
        # heartbeat
        wara_ps_vehicle.wara_ps_heartbeat(now_time)
        # sensor info
        wara_ps_vehicle.wara_ps_lvl1(now_time)

    # Create a timer to call the wara_ps_level_1_comms function every 1 second
    timer_period = 1.0/agent_waraps_dict["pulse_rate"]  # seconds
    timer = node.create_timer(timer_period, wara_ps_level_1_comms)
    node.get_logger().info("WaraPS Vehicle Node started. Publishing WaraPS Level 1 data...")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("WaraPS Vehicle Node stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()