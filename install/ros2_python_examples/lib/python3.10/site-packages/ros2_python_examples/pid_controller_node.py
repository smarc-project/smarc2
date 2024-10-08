#!/usr/bin/python3

import rclpy
import sys


try:
    # ROS
    from .pid_model import PIDModel
    from .sam_view import SAMView
    from .controller_controller import ControllerController
except:
    # Terminal
    from pid_model import  PIDModel
    from sam_view import SAMView
    from controller_controller import ControllerController

def main():
    rclpy.init(args=sys.argv)
    node = rclpy.create_node('pid_controller_node')

    model = PIDModel()
    view = SAMView(node)
    controller = ControllerController(node)

    loop_period = 0.1

    # a function defined like this is a nice way to
    # avoid passing around the above defined "global" objects
    def loop():
        controller.update(model)
        yaw, thrust = model.compute_control_action(loop_period)
        view.set_control_inputs(rpm = thrust,
                                thruster_horizontal_radians=yaw)
        view.update()

    node.create_timer(loop_period, loop)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.get_logger().info("Shutting down~")
    rclpy.shutdown()



if __name__ == '__main__':
    main()

