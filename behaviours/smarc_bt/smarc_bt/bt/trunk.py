#!/usr/bin/python3

import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.blackboard import Blackboard

from ..vehicles.vehicle import IVehicleStateContainer
from .i_has_vehicle_container import HasVehicleContainer
from .bb_keys import BBKeys

from .conditions import *




class SMaRCBT(HasVehicleContainer):
    def __init__(self,
                 vehicle_container:IVehicleStateContainer):
        """
        vehicle_container: An object that has a field "vehicle_state" which
            returns a vehicles.vehicle.IVehicleState type of object.
            SAMAuv, ROSVehicle, etc. should all fit this
        """
        self._vehicle_container = vehicle_container
        self._bt = None

    @property
    def vehicle_container(self) -> IVehicleStateContainer:
        return self._vehicle_container


    def setup(self) -> bool:
        root = Sequence("S_Root",
                        memory=False,
                        children=[
            C_VehicleSensorsWorking(self)
        ])

        self._bt = pt.trees.BehaviourTree(root)
        return self._bt.setup()


    def tick(self):
        self._bt.tick()



def test_bt_setup():
    from ..vehicles.vehicle import MockVehicleStateContainer


    v = MockVehicleStateContainer()

    bt = SMaRCBT(v)
    bt.setup()

    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))

    v.vehicle_state.update_sensor("position", [2,3,4], 0)
    v.vehicle_state.update_sensor("orientation_euler", [1,2,3], 0)
    v.vehicle_state.update_sensor("global_position", [1,2], 0)
    v.vehicle_state.update_sensor("global_heading_deg", [1], 0)
    v.vehicle_state.update_sensor("battery", [1,2], 0)

    print('='*10)
    bt.tick()
    print(bt.vehicle_container.vehicle_state)
    print(pt.display.ascii_tree(bt._bt.root, show_status=True))






def test_ros_vehicle_in_bb():
    # putting things that work with threads and such in
    # the blackboard might be a bad idea sometimes...
    from ..vehicles.sam_auv import SAMAuv
    import rclpy, sys

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_whatever")
    v = SAMAuv(node)

    bt = SMaRCBT(v)

    def update():
        nonlocal v
        bb = Blackboard()
        print(bb.get(BBKeys.VEHICLE_STATE))

    node.create_timer(0.5, update)
    rclpy.spin(node)
