#!/usr/bin/python3

import sys
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, IntegerRange
from example_interfaces.srv import SetBool

from .IThrustView import IThrustView
from .advanced_science.IRPMModel import IRPMModel

class ThrustyController:
    def __init__(self,
                 node: Node,
                 view: IThrustView,
                 model: IRPMModel):
        """ 
        A basic controller class to tie together the model and view objects we created.
        Controllers are usually quite specific to what you need done, so they rarely use the
        interface->concrete setup we used for the model and view. 

        Notice how it doesn't take the specific "SAMThrustView" or "SuperAdvancedScienceModel" as its
        view and model objects, but instead takes in the interfaces we defined. This allows
        you to easily swap around the specific view and model objects later.
        You could even modify this class to take _multiple_ of such objects, if that makes sense for
        your use case. For example if you had 3 different views, one that speaks to the robot, one
        that plots some stuff and one that writes things to a file, you could take all three and use them.

        This controller is the thing that interfaces with a "user" of the model. In this case thats usually ROS, 
        through parameters, services, subs, actions.
        These are all ROS things that can give INPUT to a model, to define how it should behave. 
        Some of those inputs could be things like "Stop working" or "Work faster" etc.
        """
        self._node = node
        self._view = view
        self._model = model

        min, max, step, default = 0, 1000, 100, 500

        # If we define a parameter descriptor like this, then ros2 will
        # actually check and accept/deny any changes to this parameter
        # this works even when you set it from a launch file
        rpm_range = IntegerRange(from_value=min, to_value=max, step=step)
        rpm_limit_descriptor = ParameterDescriptor(
            name = "rpm_limit",
            description = "The upper and lower limits given to the Advanced Science model",
            integer_range = [rpm_range])
        # even without a descriptor, this is how you define a param
        self._rpm_limit_param = node.declare_parameter(
            name = 'rpm_limit',
            value = default,
            descriptor = rpm_limit_descriptor)
        
        # the .value field is static. it doesnt change and has the
        # default value set above. Useful for setting defaults in general.
        self._model.set_range(self._rpm_limit_param.value)

        # service defs are the same as they were in ros1.
        self._log_rpm_info_service = self._node.create_service(SetBool, "log_rpm_info", self._log_rpm_info_service_cb)
        self._log_rpm_info = True

    def _log_rpm_info_service_cb(self, request, response):
        self._log_rpm_info = request.data
        response.success = True
        response.message = f"Toggled logging the RPM changes to {request.data}!"
        return response

    def update(self):
        # the usual things done in a controller loop is like so
        # READ -> from user==ROS (done above with the param)
        # UPDATE -> the model. with any inputs there might be. very dependent on everything really.
        # SHOW -> something, if there is anything to show from the MODEL, using any VIEWs.

        # READ
        # this is how we get the _current_ value of a param. 
        # you can do this anywhere anytime really.
        r = self._node.get_parameter('rpm_limit').get_parameter_value().integer_value

        # UPDATE
        self._model.set_range(r)
        if(self._log_rpm_info):
            self._node.get_logger().info(f"RPM Limit: {r}")
        rpm = self._model.computeRPM()

        # SHOW
        if(self._log_rpm_info):
            self._node.get_logger().info(f"Setting RPM to {rpm}")
        self._view.set_rpm(rpm)
        self._view.update()

    def run(self):
        loop_period = 1
        self._node.create_timer(loop_period, self.update)
        try:
            rclpy.spin(self._node)
        except KeyboardInterrupt:
            pass

# see setup.py. This function is defined in there to expose to ros2.
def main():
    # when creating the _object_ rather than the _class_, we use the concrete classes
    from .advanced_science.SuperAdvancedScienceModel import SuperAdvancedScienceModel
    from .SAMThrustView import SAMThrustView

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("AdvancedScienceNode")

    view = SAMThrustView(node)
    model = SuperAdvancedScienceModel(range=500)

    controller = ThrustyController(node, view, model)

    controller.run()


if __name__ == "__main__":
    main()