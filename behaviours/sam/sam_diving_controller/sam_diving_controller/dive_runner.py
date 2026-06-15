# my_pkg/dive_runner.py
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor


class HasUpdate(Protocol):
    def update(self) -> None: ...


@dataclass(frozen=True)
class Rates:
    dive_pub: float
    dive_controller: float
    dive_sub: float
    convenience: float


@dataclass(frozen=True)
class Components:
    dive_pub: object
    dive_controller: HasUpdate
    dive_sub: HasUpdate
    convenience_pub: Optional[HasUpdate] = None
    dive_pub_update: Optional[Callable[[], None]] = None


def declare_and_get_rates(node: Node) -> Rates:
    node.declare_parameter("dive_pub_rate", 0.1)
    node.declare_parameter("dive_controller_rate", 0.2)
    node.declare_parameter("dive_sub_rate", 0.1)
    node.declare_parameter("convenience_rate", 0.1)

    gp = node.get_parameter

    return Rates(
        dive_pub=float(gp("dive_pub_rate").value),
        dive_controller=float(gp("dive_controller_rate").value),
        dive_sub=float(gp("dive_sub_rate").value),
        convenience=float(gp("convenience_rate").value),
    )


def run_mode( *, node_name: str, build: Callable[[Node, Rates], Components],
             log_banner: str = "Created MVC",) -> None:
    rclpy.init(args=sys.argv)
    node = rclpy.create_node(node_name)

    rates = declare_and_get_rates(node)
    comps = build(node, rates)

    # Timers (shared)
    pub_cb = comps.dive_pub_update
    if pub_cb is None:
        # default assumes dive_pub has .update()
        pub_cb = getattr(comps.dive_pub, "update")

    node.create_timer(rates.dive_pub, pub_cb)
    node.create_timer(rates.dive_controller, comps.dive_controller.update)
    node.create_timer(rates.dive_sub, comps.dive_sub.update)

    if comps.convenience_pub is not None:
        node.create_timer(rates.convenience, comps.convenience_pub.update)

    node.get_logger().info("Setpoints in Topic")
    node.get_logger().info(log_banner)

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info("Shutting down")
        node.destroy_node()
        rclpy.shutdown()

