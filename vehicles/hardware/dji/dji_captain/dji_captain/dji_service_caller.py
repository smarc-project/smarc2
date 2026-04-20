#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
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
            commands += "  3: Take off\n"
            commands += "  4: Land\n"
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
                elif user_input == "3":
                    res = call_service_blocking(self._node, self._takeoff_srv, Trigger.Request())
                    print(f"Take off response: {res.success}")
                elif user_input == "4":
                    res = call_service_blocking(self._node, self._land_srv, Trigger.Request())
                    print(f"Land response: {res.success}")
                elif user_input == "0":
                    print("Exiting...")
                    sys.exit(0)
                else:
                    print("Invalid command.")
                    continue

            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        
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
