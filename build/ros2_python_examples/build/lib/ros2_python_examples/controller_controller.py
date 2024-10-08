#!/usr/bin/python3

import rclpy
import sys
import tf2_ros

from rclpy.node import Node
from tf_transformations import euler_from_quaternion

# Dirty dirty workaround to how ROS2 installs things
# while also allowing running this file from the command line
# without ROS-stuff.
# Obviously you can omit one of these if its not needed...
# Only needed for "local" files. 
try:
    from .pid_model import PIDModel # for ROS2
except:
    from pid_model import PIDModel # for non-ros

class ControllerController:
    """
    A simple controller object that subscribes to topics relevant to a model it is expected to modify.
    In this case, this is a PIDModel that only needs x,y position and a yaw, so I will only sub to those.
    Ideally, this should be very similar to the View object.
    """
    def __init__(self,
                 node: Node):
        # The model to update as needed.
        # Avoid doing this update in a callback, since callbacks
        # are ran on different threads and might happen in between
        # an update running inside the model object already.
        # This can lead to things like x=5 for the first half of a method
        # call and x=10 for the second half of the same method call. 
        # Debugging that is painful, update stuff explicitly, on the same thread!
        self._node = node

        # tf stuff is more similar to how it works in CPP now :D
        self._reference_frame = node.declare_parameter("reference_frame", "odom").value
        self._robot_frame = node.declare_parameter("base_link", "sam0_base_link").value
        self._tf_buffer = tf2_ros.buffer.Buffer()
        self._tf_listener = tf2_ros.transform_listener.TransformListener(self._tf_buffer, node)

    def _log(self, s: str):
        self._node.get_logger().info(s)


    def update(self, model: PIDModel):
        try:
            self._last_tf_stamped = self._tf_buffer.lookup_transform(self._robot_frame,
                                                                     self._reference_frame,
                                                                     rclpy.time.Time())
        except Exception as ex:
            self._log(f"Could not find transform from {self._reference_frame} to {self._robot_frame} -> {ex}")
            return False

        translation = self._last_tf_stamped.transform.translation
        posi = [translation.x, translation.y]
        # tf2 does not have transformations in it anymore, so we gotta use this instead
        # http://matthew-brett.github.io/transforms3d/reference/transforms3d.euler.html#transforms3d.euler.quat2euler
        # https://github.com/DLu/tf_transformations
        # ros-humble-tf-transformations -> tf-transformations in package.xml
        # pip3 install transforms3d -> python-transforms3d-pip in package.xml
        # tf_transformations basically uses transforms3d under the hood for everything, but wraps it
        # to look like the old tf functions. this will be very useful for porting.
        xyzw = self._last_tf_stamped.transform.rotation
        rpy = euler_from_quaternion([xyzw.x, xyzw.y, xyzw.z, xyzw.w])
        model.set_pose(posi, rpy[2])


        


if __name__ == "__main__":
    from sam_view import SAMView

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("ControllerControllerTestNode")

    model = PIDModel()
    view = SAMView(node)
    controller = ControllerController(node)

    # just a simple waypoint dead-ahead
    model.set_waypoint([10,0])

    # seconds
    loop_period = 0.1

    def main_loop():
        controller.update(model)
        yaw_u, thrust_u = model.compute_control_action(loop_period)
        node.get_logger().info(f"yaw_u = {yaw_u},   thrust_u = {thrust_u}")
        view.set_control_inputs(thruster_horizontal_radians= yaw_u,
                                rpm = thrust_u)
        view.update()


    # This is a better way to handle the main loop
    # otherwise you might face threading hell :D
    node.create_timer(loop_period, main_loop)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()




