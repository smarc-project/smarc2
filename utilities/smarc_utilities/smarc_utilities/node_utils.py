from typing import TypeVar

from rcl_interfaces.msg import ParameterDescriptor
from rclpy.node import Node

T = TypeVar("T")

def typed_param_declare(node: Node, name: str, default_value: T, param_desc: str) -> T:
    """Wrapped parameter declare to enable type completion for LSP.

    Additional None protection added.
    """
    param_value = node.declare_parameter(
        name, default_value, ParameterDescriptor(description=param_desc)
    ).value
    if param_value is None:
        err_str = "This function wraps param calls to prevent None types."
        err_str = "A None parameter was discoverd violation the assumption.\n"
        err_str += (
            "Use node.declare_parameter and directly handle None types if you must\n"
        )
        err_str += (
            "Rewriting this function to allow None types would defeat it's purpose."
        )
        raise ValueError(err_str)
    return param_value
