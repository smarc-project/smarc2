import math
from typing import Iterable

import numpy as np
from geometry_msgs.msg import Point, Quaternion, TransformStamped, Vector3


def vector3_to_numpy(value: Vector3) -> np.ndarray:
    return np.array([value.x, value.y, value.z], dtype=float)


def point_to_numpy(value: Point) -> np.ndarray:
    return np.array([value.x, value.y, value.z], dtype=float)


def numpy_to_vector3(value: Iterable[float]) -> Vector3:
    array = np.asarray(value, dtype=float).reshape(3)
    return Vector3(x=float(array[0]), y=float(array[1]), z=float(array[2]))


def numpy_to_point(value: Iterable[float]) -> Point:
    array = np.asarray(value, dtype=float).reshape(3)
    return Point(x=float(array[0]), y=float(array[1]), z=float(array[2]))


def quaternion_to_rotation_matrix(quaternion: Quaternion) -> np.ndarray:
    x, y, z, w = quaternion.x, quaternion.y, quaternion.z, quaternion.w
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm < 1e-12:
        return np.eye(3)
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    return np.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ],
        dtype=float,
    )


def yaw_to_quaternion(yaw: float) -> Quaternion:
    half = 0.5 * yaw
    return Quaternion(x=0.0, y=0.0, z=math.sin(half), w=math.cos(half))


def transform_point(point: np.ndarray, transform: TransformStamped) -> np.ndarray:
    rotation = quaternion_to_rotation_matrix(transform.transform.rotation)
    translation = np.array(
        [
            transform.transform.translation.x,
            transform.transform.translation.y,
            transform.transform.translation.z,
        ],
        dtype=float,
    )
    return rotation @ np.asarray(point, dtype=float).reshape(3) + translation


def transform_vector(vector: np.ndarray, transform: TransformStamped) -> np.ndarray:
    rotation = quaternion_to_rotation_matrix(transform.transform.rotation)
    return rotation @ np.asarray(vector, dtype=float).reshape(3)


def clamp(value: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.minimum(np.maximum(value, lower), upper)


def first_order_lowpass(previous: np.ndarray, target: np.ndarray, cutoff_hz: float, dt: float) -> np.ndarray:
    if cutoff_hz <= 0.0:
        return np.asarray(target, dtype=float).copy()
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff_hz * dt)
    return np.asarray(previous, dtype=float) + alpha * (
        np.asarray(target, dtype=float) - np.asarray(previous, dtype=float)
    )


def slew_limit(previous: np.ndarray, target: np.ndarray, max_rate: np.ndarray, dt: float) -> tuple[np.ndarray, bool]:
    previous = np.asarray(previous, dtype=float)
    target = np.asarray(target, dtype=float)
    max_step = np.asarray(max_rate, dtype=float) * dt
    delta = target - previous
    limited_delta = np.clip(delta, -max_step, max_step)
    limited = not np.allclose(delta, limited_delta, rtol=0.0, atol=1e-12)
    return previous + limited_delta, limited
