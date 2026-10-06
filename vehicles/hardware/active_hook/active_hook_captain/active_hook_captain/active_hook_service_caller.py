#!/usr/bin/python3
import sys

import rclpy
from rclpy.node import Node

from mavros_msgs.srv import CommandBool, SetMode

from active_hook_msgs.msg import Topics as ActiveHookTopics


def call_service_blocking(node, client, request):
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    if future.result() is None:
        raise RuntimeError("Service call failed (no response).")
    return future.result()


class ServiceCaller:
    def __init__(self, node: Node):
        self._node = node

        self._arming_client = node.create_client(CommandBool, ActiveHookTopics.MAVROS_ARMING_SRV)
        self._set_mode_client = node.create_client(SetMode, ActiveHookTopics.MAVROS_SET_MODE_SRV)

        print("Waiting for mavros arming/set_mode services...")
        self._arming_client.wait_for_service()
        self._set_mode_client.wait_for_service()
        print("Services ready.")

        self.run()

    def run(self):
        menu = (
            "\n--- ActiveHook Service Caller ---\n"
            "1: ARM\n"
            "2: DISARM\n"
            "3: MANUAL mode\n"
            "4: STABILIZE mode\n"
            "5: ALT_HOLD (depth hold) mode\n"
            "0: Exit\n"
            "Enter command: "
        )

        while rclpy.ok():
            try:
                choice = input(menu).strip()

                if choice == "1":
                    self.set_arm(True)
                elif choice == "2":
                    self.set_arm(False)
                elif choice == "3":
                    self.set_mode("MANUAL")
                elif choice == "4":
                    self.set_mode("STABILIZE")
                elif choice == "5":
                    self.set_mode("ALT_HOLD")
                elif choice == "0":
                    print("Exiting...")
                    sys.exit(0)
                else:
                    print(f"Unknown command: '{choice}'")

            except Exception as error:
                print(f"Error: {error}")

    def set_arm(self, arm: bool):
        request = CommandBool.Request()
        request.value = arm
        response = call_service_blocking(self._node, self._arming_client, request)
        action = "ARM" if arm else "DISARM"
        print(f"{action} {'accepted' if response.success else 'rejected'}.")

    def set_mode(self, mode_name: str):
        request = SetMode.Request()
        request.base_mode = 0
        request.custom_mode = mode_name
        response = call_service_blocking(self._node, self._set_mode_client, request)
        print(f"{mode_name} mode {'sent' if response.mode_sent else 'rejected'}.")


def main():
    rclpy.init()
    node = Node("active_hook_service_caller")
    ServiceCaller(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()