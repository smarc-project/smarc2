#!/usr/bin/python3

import rclpy, sys
from rclpy.node import Node

from geometry_msgs.msg import Pose2D
from smarc_mission_msgs.srv import DubinsPlan
from smarc_mission_msgs.msg import Topics as MissionTopics

from .dubins import Waypoint, sample_complete_plan

class DubinsPlannerService:
    def __init__(self,
                 node: Node):
        self._node = node
        self._dubins_service = self._node.create_service(DubinsPlan,
                                                          MissionTopics.DUBINS_SERVICE,
                                                          DubinsPlannerService.dubins_cb)
        
        self._node.get_logger().info(f"Dubins planner service available on:{MissionTopics.DUBINS_SERVICE}")
        
    def dubins_cb(request:DubinsPlan.Request, response:DubinsPlan.Response):
        # the request has a field .waypoints that contains a buch of pose2D objects
        # we convert that to the waypoint object of the dubins planner
        # and pass that on
        dubins_input = [Waypoint(p.x, p.y, p.theta) for p in request.waypoints]
        dubins_out, original_indices = sample_complete_plan(dubins_input, request.turning_radius, request.step)

        # convert back to pose2D for transfer
        response.waypoints = []
        response.original_wp_indices = [int(i) for i in original_indices]
        for wp in dubins_out:
            p = Pose2D()
            p.x = float(wp[0])
            p.y = float(wp[1])
            p.theta = float(wp[2])
            response.waypoints.append(p)

        return response



def main():
    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("dubins_planner_service")
    
    s = DubinsPlannerService(node)
    
    rclpy.spin(node)


def test_service():
    import matplotlib.pyplot as plt
    import numpy as np

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("dubins_planner_service_tester")

    client = node.create_client(DubinsPlan, MissionTopics.DUBINS_SERVICE)
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info("Can't reach the service?!")

    req = DubinsPlan.Request()

    req.step = 0.1
    req.turning_radius = 5.0
    points = [
        (0,0,0),
        (10,0,0),
        (20,0,90)
    ]

    
    

    def plot_path(ax, points, marker='bo'):
        # Plot each point and draw an arrow according to the angle
        for x, y, angle in points:
            ax.plot(x, y, marker)  # 'bo' creates a blue circle marker
            # Calculate the arrow's dx and dy using the angle
            dx = np.cos(np.radians(angle))
            dy = np.sin(np.radians(angle))
            ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc='k', ec='k')

    # Create the plot
    fig, ax = plt.subplots()
    plot_path(ax, points)
        
    req.waypoints = []
    for p in points:
        p2d = Pose2D()
        p2d.x = float(p[0])
        p2d.y = float(p[1])
        p2d.theta = float(p[2])
        req.waypoints.append(p2d)

    future = client.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    res = future.result()
    points = [(p.x, p.y, p.theta) for p in res.waypoints]
    plot_path(ax, points, marker='rx')

    # Show the plot
    plt.show()


if __name__ == "__main__":
    main()