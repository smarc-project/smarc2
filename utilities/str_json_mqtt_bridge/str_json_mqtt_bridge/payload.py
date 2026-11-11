"""What goes out on the broker for a given ROS String. Pure; no rclpy.

The contract is that the String carries JSON (json.dumps on the way in,
json.loads on the way out). Two older habits are still accepted: the JSON
wrapped in one extra pair of quotes, and a Python repr (single quotes, None,
True) from a str(dict). Anything else is not JSON and is dropped.
"""

import ast
import json


def to_json_payload(text: str) -> str | None:
    """JSON text for the broker, or None when ``text`` is not JSON-like."""
    try:
        return json.dumps(json.loads(text))
    except ValueError:
        pass
    if text[:1] in ('"', "'"):
        return text[1:-1]                           # JSON wrapped in one pair of quotes; forwarded as before
    try:
        return json.dumps(ast.literal_eval(text))   # Python repr: {'x': None} -> {"x": null}
    except (ValueError, SyntaxError, TypeError):
        return None
