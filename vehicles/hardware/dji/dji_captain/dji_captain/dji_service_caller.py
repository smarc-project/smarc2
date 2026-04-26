#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
from sensor_msgs.msg import Joy
from dji_msgs.msg import PsdkTopics as PSDKTopics


class ServiceCaller():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("robot_name", "M350")
        self.ROBOT_NAME : str = self._node.get_parameter("robot_name").get_parameter_value().string_value        
        
        # services to take and give-up control + take-off and land
        # call service: obtain/release_ctrl_authority
        self._take_control_srv = node.create_client(Trigger, PSDKTopics.TAKE_CONTROL_SRV)
        self._release_control_srv = node.create_client(Trigger, PSDKTopics.RELEASE_CONTROL_SRV)
        self._takeoff_srv = node.create_client(Trigger, PSDKTopics.TAKEOFF_SRV)
        self._land_srv = node.create_client(Trigger, PSDKTopics.LAND_SRV)

        self.FLU_vel_joy_pub = node.create_publisher(Joy, PSDKTopics.FLU_VEL_YAWRATE_JOY_CMD, qos_profile=10)

        got_srvs = False
        while rclpy.ok() and not got_srvs:
            got_take_control = self._take_control_srv.wait_for_service(timeout_sec=5.0)
            got_release_control = self._release_control_srv.wait_for_service(timeout_sec=5.0)
            got_takeoff = self._takeoff_srv.wait_for_service(timeout_sec=5.0)
            got_land = self._land_srv.wait_for_service(timeout_sec=5.0)
            got_srvs = got_take_control and got_release_control and got_takeoff and got_land
            if not got_srvs:
                self._node.get_logger().error("Not all services are available... Captain will do nothing but wait for these...")
                self._node.get_logger().error("Unavailable services: " +
                    ("" if got_take_control else "Take control ") +
                    ("" if got_release_control else "Release control ") +
                    ("" if got_takeoff else "Take off ") +
                    ("" if got_land else "Land "))
                time.sleep(2)
            

        while rclpy.ok():
            commands = "Commands:\n"
            commands += "  1: Take control\n"
            commands += "  2: Release control\n"
            commands += "  4: Take off\n"
            commands += "  6: Land\n"
            commands += "  9: Joytest\n"
            commands += "  0: EXIT\n"
            commands += "Enter command: "

            try:
                user_input = input(commands)
                if user_input == "1":
                    res = call_service_blocking(self._node, self._take_control_srv, Trigger.Request())
                    print(f"Take control response: {res.success}")
                elif user_input == "2":
                    res = call_service_blocking(self._node, self._release_control_srv, Trigger.Request())
                    print(f"Release control response: {res.success}")
                elif user_input == "4":
                    res = call_service_blocking(self._node, self._takeoff_srv, Trigger.Request())
                    print(f"Take off response: {res.success}")
                elif user_input == "6":
                    res = call_service_blocking(self._node, self._land_srv, Trigger.Request())
                    print(f"Land response: {res.success}")
                elif user_input == "0":
                    print("Exiting...")
                    sys.exit(0)
                elif user_input == "9":
                    print("Starting joy test...")
                    joy_cmds = "JOY MODE Commands (FLU Velocity YawRate):\n"
                    joy_cmds += "Example to move forward for 1s at 0.1m/s: move,f,1s,0.1\n"
                    joy_cmds += "Example to yaw for 2s at 20 deg/s: yaw,2s,20\n"
                    user_input = input(joy_cmds + "Enter JOY command: ")
                    if user_input.startswith("move"):
                        vx, vy, vz = 0.0, 0.0, 0.0
                        direction_str, duration_str, speed_str = user_input.split(",")[1:]
                        if direction_str == "f":
                            vx, vy, vz = float(speed_str), 0.0, 0.0
                        elif direction_str == "b":
                            vx, vy, vz = -float(speed_str), 0.0, 0.0
                        elif direction_str == "l":
                            vx, vy, vz = 0.0, float(speed_str), 0.0
                        elif direction_str == "r":
                            vx, vy, vz = 0.0, -float(speed_str), 0.0
                        elif direction_str == "u":
                            vx, vy, vz = 0.0, 0.0, float(speed_str)
                        elif direction_str == "d":
                            vx, vy, vz = 0.0, 0.0, -float(speed_str)
                        else:
                            print("Invalid direction. Use f/b/l/r/u/d for forward/backward/left/right/up/down.")
                            continue
                        duration = float(duration_str.replace("s", ""))
                        self.send_joy(vx, vy, vz, 0.0, duration)
                    elif user_input.startswith("yaw"):
                        _, duration_str, speed_str = user_input.split(",")
                        yaw_rate_deg = float(speed_str)
                        duration = float(duration_str.replace("s", ""))
                        self.send_joy(0.0, 0.0, 0.0, yaw_rate_deg, duration)
                    else:
                        print("Invalid JOY command, must start with 'move' or 'yaw'.")
                        continue
                else:
                    print("Invalid command.")
                    continue

            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)


    def send_joy(self, vx: float, vy: float, vz: float, yawrate: float, duration: float):
        joy_msg = Joy()
        joy_msg.axes = [vx, vy, vz, yawrate]

        def pub():
            joy_msg.header.stamp = self._node.get_clock().now().to_msg()
            self.FLU_vel_joy_pub.publish(joy_msg)

        timer = self._node.create_timer(0.1, pub) 

        end_time = time.time() + duration
        while time.time() < end_time:
            rclpy.spin_once(self._node, timeout_sec=0.1)
            dt = end_time - time.time()
            if dt <= 0:
                break
            self._node.get_logger().info(f"Publishing JOY command with vx: {vx}, vy: {vy}, vz: {vz}, yawrate: {yawrate} for {dt:.2f} more seconds...")


        timer.cancel()

        
def call_service_blocking(node, client, request) -> Trigger.Response:
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    if future.result() is None:
        raise RuntimeError('Service call failed')
    return future.result()            
    

def main():
    rclpy.init(args=sys.argv)
    node = Node("dji_service_caller_node")
    ServiceCaller(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
