from collections.abc import Sequence

from geometry_msgs.msg import Point, Quaternion, TransformStamped, Vector3
import numpy as np
from transforms3d.quaternions import quat2mat

def vector3_to_numpy(value: Point | Vector3) -> np.ndarray:
    return np.array([value.x, value.y, value.z], dtype=float)

def numpy_to_vector3(value: np.ndarray) -> Vector3:
    return Vector3(x=float(value[0]), y=float(value[1]), z=float(value[2]))

def rotation(quaternion: Quaternion) -> np.ndarray:
    q = np.array([quaternion.w, quaternion.x, quaternion.y, quaternion.z])
    if not np.isfinite(q).all() or np.linalg.norm(q) < 1e-12:
        raise ValueError('invalid orientation quaternion')
    return quat2mat(q)

def transform_point(point: np.ndarray, transform: TransformStamped) -> np.ndarray:
    return (rotation(transform.transform.rotation) @ point + vector3_to_numpy(transform.transform.translation))

def rotate_covariance(covariance: Sequence[float] | np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Rotate the linear and angular blocks of a six-dimensional covariance."""
    transform = np.zeros((6, 6))
    transform[:3, :3] = transform[3:, 3:] = matrix
    return transform @ np.asarray(covariance).reshape(6, 6) @ transform.T
