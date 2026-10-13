from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import yaml
from scipy.linalg import expm


AXES = ("x", "y", "z")


@dataclass(frozen=True)
class AxisModel:
    """First-order discrete model v[k+1] = a*v[k] + b*u[k]."""

    a: float
    b: float
    dc_gain: float

    @property
    def pole(self) -> float:
        return self.a

    @property
    def stable(self) -> bool:
        return abs(self.a) < 1.0


@dataclass(frozen=True)
class DiscreteVelocityModel:
    dt: float
    x: AxisModel
    y: AxisModel
    z: AxisModel
    source: str

    @property
    def fs(self) -> float:
        return 1.0 / self.dt

    @property
    def a_vector(self) -> np.ndarray:
        return np.array([self.x.a, self.y.a, self.z.a], dtype=float)

    @property
    def b_vector(self) -> np.ndarray:
        return np.array([self.x.b, self.y.b, self.z.b], dtype=float)

    @property
    def dc_gain_vector(self) -> np.ndarray:
        return np.array([self.x.dc_gain, self.y.dc_gain, self.z.dc_gain], dtype=float)

    def velocity_matrices(self) -> tuple[np.ndarray, np.ndarray]:
        return np.diag(self.a_vector), np.diag(self.b_vector)

    def xy_position_velocity_matrices(self) -> tuple[np.ndarray, np.ndarray]:
        """State is [e_x, e_y, e_vx, e_vy], input is delta velocity command."""
        ax, ay = self.x.a, self.y.a
        bx, by = self.x.b, self.y.b
        dt = self.dt
        a = np.array(
            [
                [1.0, 0.0, dt, 0.0],
                [0.0, 1.0, 0.0, dt],
                [0.0, 0.0, ax, 0.0],
                [0.0, 0.0, 0.0, ay],
            ],
            dtype=float,
        )
        b = np.array(
            [
                [0.0, 0.0],
                [0.0, 0.0],
                [bx, 0.0],
                [0.0, by],
            ],
            dtype=float,
        )
        return a, b


class ModelFormatError(ValueError):
    pass


def _as_float(value: Any) -> float:
    array = np.asarray(value, dtype=float).reshape(-1)
    if array.size != 1:
        raise ModelFormatError(f"Expected a scalar, received shape {array.shape}")
    return float(array[0])


def _extract_dt(mapping: Mapping[str, Any], fallback_dt: float | None) -> float:
    if "dt" in mapping:
        dt = _as_float(mapping["dt"])
    elif "fs" in mapping:
        fs = _as_float(mapping["fs"])
        if fs <= 0.0:
            raise ModelFormatError("Sampling frequency must be positive")
        dt = 1.0 / fs
    elif fallback_dt is not None:
        dt = float(fallback_dt)
    else:
        raise ModelFormatError("No dt/fs found. Pass sample_time explicitly.")
    if dt <= 0.0:
        raise ModelFormatError("Sample time must be positive")
    return dt


def _channel_candidates(channels: Mapping[str, Any], axis: str) -> list[str]:
    direct = {
        "x": ("Gxd", "Gx", "x", "X"),
        "y": ("Gyd", "Gy", "y", "Y"),
        "z": ("Gzd", "Gz", "z", "Z"),
    }[axis]
    result = [key for key in direct if key in channels]
    axis_index = {"x": "0", "y": "1", "z": "2"}[axis]
    for key in channels:
        lower = key.lower()
        if key in result:
            continue
        if f"axes_{axis_index}" in lower:
            result.append(key)
            continue
        if lower.endswith(f"_{axis}") or f"velocity_ground_fused_{axis}" in lower:
            result.append(key)
    return result


def _get_axis_channel(channels: Mapping[str, Any], axis: str) -> Mapping[str, Any]:
    candidates = _channel_candidates(channels, axis)
    if not candidates:
        raise ModelFormatError(
            f"Could not find a channel for axis '{axis}'. Available channels: {list(channels)}"
        )
    return channels[candidates[0]]


def _parse_discrete_channel(channel: Mapping[str, Any]) -> AxisModel:
    if "a" in channel and "b" in channel:
        a = _as_float(channel["a"])
        b = _as_float(channel["b"])
    else:
        num = np.asarray(channel.get("num_b", channel.get("num")), dtype=float).reshape(-1)
        den = np.asarray(channel.get("den_a", channel.get("den")), dtype=float).reshape(-1)
        if num.size == 0 or den.size < 2:
            raise ModelFormatError("Discrete channel requires num_b and a first-order den_a")
        den0 = den[0]
        if abs(den0) < 1e-12:
            raise ModelFormatError("Leading denominator coefficient cannot be zero")
        # For D(z)=den[0] z + den[1], v[k+1]=(-den[1]/den[0])v[k]+b*u[k].
        a = -float(den[1] / den0)
        # The identified files use a constant numerator b/(z-a). If a longer
        # numerator is present, the final nonzero coefficient is the direct lag term.
        nonzero = num[np.abs(num) > 1e-15]
        if nonzero.size == 0:
            raise ModelFormatError("Numerator cannot be all zeros")
        b = float(nonzero[-1] / den0)
    dc_gain = float(channel.get("dc_gain", b / (1.0 - a)))
    return AxisModel(a=a, b=b, dc_gain=dc_gain)


def _continuous_first_order_to_discrete(
    channel: Mapping[str, Any], dt: float
) -> AxisModel:
    if "tau_s" in channel and "dc_gain" in channel:
        tau = _as_float(channel["tau_s"])
        gain = _as_float(channel["dc_gain"])
        if tau <= 0.0:
            raise ModelFormatError("tau_s must be positive")
        pole_rate = 1.0 / tau
        numerator = gain * pole_rate
    else:
        num = np.asarray(channel.get("num_b", channel.get("num")), dtype=float).reshape(-1)
        den = np.asarray(channel.get("den_a", channel.get("den")), dtype=float).reshape(-1)
        if num.size == 0 or den.size < 2:
            raise ModelFormatError("Continuous channel requires num_b and first-order den_a")
        den0 = den[0]
        if abs(den0) < 1e-12:
            raise ModelFormatError("Leading denominator coefficient cannot be zero")
        pole_rate = float(den[1] / den0)
        numerator = float(num[-1] / den0)
        gain = float(channel.get("dc_gain", numerator / pole_rate))
    if pole_rate <= 0.0:
        raise ModelFormatError(
            f"Continuous first-order pole rate must be positive, got {pole_rate}"
        )
    a = float(np.exp(-pole_rate * dt))
    b = float((numerator / pole_rate) * (1.0 - a))
    return AxisModel(a=a, b=b, dc_gain=gain)


def _load_yaml(
    path: Path, model_kind: str, sample_time: float | None
) -> DiscreteVelocityModel:
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, Mapping):
        raise ModelFormatError("YAML root must be a mapping")

    # Some repositories wrap the actual model under discrete_models/continuous_models.
    root = data
    detected_kind = model_kind
    if "discrete_models" in data:
        root = data["discrete_models"]
        if model_kind == "auto":
            detected_kind = "discrete"
    elif "continuous_models" in data:
        root = data["continuous_models"]
        if model_kind == "auto":
            detected_kind = "continuous"

    if not isinstance(root, Mapping) or "channels" not in root:
        raise ModelFormatError("YAML must contain a channels mapping")
    channels = root["channels"]
    if not isinstance(channels, Mapping):
        raise ModelFormatError("channels must be a mapping")

    if detected_kind == "auto":
        any_channel = next(iter(channels.values()))
        if isinstance(any_channel, Mapping) and (
            "dt" in any_channel or "Gxd" in channels or "Gyd" in channels
        ):
            detected_kind = "discrete"
        elif isinstance(any_channel, Mapping) and "tau_s" in any_channel:
            detected_kind = "continuous"
        else:
            raise ModelFormatError(
                "Could not determine whether YAML is continuous or discrete. "
                "Set model_kind explicitly."
            )

    root_dt = None
    if detected_kind == "continuous" and sample_time is not None:
        # Explicit controller sample time takes precedence over the acquisition fs
        # stored with a continuous-time identification result.
        root_dt = float(sample_time)
    else:
        try:
            root_dt = _extract_dt(root, sample_time)
        except ModelFormatError:
            # Discrete channels may carry dt individually.
            root_dt = None

    axis_models: dict[str, AxisModel] = {}
    axis_dts: list[float] = []
    for axis in AXES:
        channel = _get_axis_channel(channels, axis)
        if detected_kind == "discrete":
            axis_models[axis] = _parse_discrete_channel(channel)
            axis_dts.append(_extract_dt(channel, root_dt))
        elif detected_kind == "continuous":
            dt = root_dt if root_dt is not None else _extract_dt(channel, sample_time)
            axis_models[axis] = _continuous_first_order_to_discrete(channel, dt)
            axis_dts.append(dt)
        else:
            raise ModelFormatError(f"Unsupported model_kind: {detected_kind}")

    dt = axis_dts[0]
    if not np.allclose(axis_dts, dt, rtol=0.0, atol=1e-12):
        raise ModelFormatError(f"Axis sample times do not match: {axis_dts}")
    return DiscreteVelocityModel(
        dt=dt,
        x=axis_models["x"],
        y=axis_models["y"],
        z=axis_models["z"],
        source=f"{detected_kind} YAML: {path}",
    )


def _discretize_state_space(ac: np.ndarray, bc: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    n = ac.shape[0]
    m = bc.shape[1]
    augmented = np.zeros((n + m, n + m), dtype=float)
    augmented[:n, :n] = ac
    augmented[:n, n:] = bc
    transition = expm(augmented * dt)
    return transition[:n, :n], transition[:n, n:]


def _axis_models_from_ab(a_matrix: np.ndarray, b_matrix: np.ndarray) -> dict[str, AxisModel]:
    a_matrix = np.asarray(a_matrix, dtype=float)
    b_matrix = np.asarray(b_matrix, dtype=float)
    if a_matrix.shape[0] < 3 or a_matrix.shape[1] < 3:
        raise ModelFormatError(f"A must contain at least a 3x3 velocity block, got {a_matrix.shape}")
    if b_matrix.shape[0] < 3 or b_matrix.shape[1] < 3:
        raise ModelFormatError(f"B must contain at least a 3x3 velocity block, got {b_matrix.shape}")
    result: dict[str, AxisModel] = {}
    for index, axis in enumerate(AXES):
        a = float(a_matrix[index, index])
        b = float(b_matrix[index, index])
        result[axis] = AxisModel(a=a, b=b, dc_gain=b / (1.0 - a))
    return result


def _first_existing(npz: Mapping[str, Any], keys: tuple[str, ...]) -> Any | None:
    for key in keys:
        if key in npz:
            return npz[key]
    return None


def _axis_rows(value: Any, name: str) -> np.ndarray:
    """Normalize stacked three-axis coefficients to shape (3, n)."""
    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        raise ModelFormatError(f"{name} must contain one row per axis")
    if array.ndim == 1:
        if array.size == 3:
            return array.reshape(3, 1)
        if array.size % 3 == 0:
            return array.reshape(3, -1)
        raise ModelFormatError(
            f"{name} cannot be split into three axes; shape={array.shape}"
        )
    if array.shape[0] == 3:
        return array.reshape(3, -1)
    if array.shape[1] == 3:
        return np.swapaxes(array, 0, 1).reshape(3, -1)
    raise ModelFormatError(f"{name} must have an axis dimension of 3; shape={array.shape}")


def _transfer_channels_from_npz(npz: Mapping[str, Any]) -> dict[str, dict[str, Any]] | None:
    """Extract first-order transfer channels from common NPZ layouts."""
    num_value = _first_existing(npz, ("num_b", "num", "numerators"))
    den_value = _first_existing(npz, ("den_a", "den", "denominators"))
    if num_value is not None and den_value is not None:
        num_rows = _axis_rows(num_value, "num_b")
        den_rows = _axis_rows(den_value, "den_a")
        gains = _first_existing(npz, ("dc_gain", "dc_gains", "gain"))
        taus = _first_existing(npz, ("tau_s", "tau", "time_constants"))
        gain_rows = None if gains is None else np.asarray(gains, dtype=float).reshape(-1)
        tau_rows = None if taus is None else np.asarray(taus, dtype=float).reshape(-1)
        channels: dict[str, dict[str, Any]] = {}
        for index, axis in enumerate(AXES):
            channel: dict[str, Any] = {
                "num_b": num_rows[index],
                "den_a": den_rows[index],
            }
            if gain_rows is not None:
                if gain_rows.size < 3:
                    raise ModelFormatError("dc_gain must contain three axis values")
                channel["dc_gain"] = float(gain_rows[index])
            if tau_rows is not None:
                if tau_rows.size < 3:
                    raise ModelFormatError("tau_s must contain three axis values")
                channel["tau_s"] = float(tau_rows[index])
            channels[axis] = channel
        return channels

    # Exact BLA export used by dji_captain/sway_controller, for example:
    # b__FLU_axes_0__to__FLUvelocity_ground_fused_x
    # a__FLU_axes_0__to__FLUvelocity_ground_fused_x
    bla_channels: dict[str, dict[str, Any]] = {}
    for index, axis in enumerate(AXES):
        input_token = f"flu_axes_{index}"
        output_token = f"fluvelocity_ground_fused_{axis}"
        numerator_key = next(
            (
                key
                for key in npz
                if key.lower().startswith("b__")
                and input_token in key.lower()
                and output_token in key.lower()
            ),
            None,
        )
        denominator_key = next(
            (
                key
                for key in npz
                if key.lower().startswith("a__")
                and input_token in key.lower()
                and output_token in key.lower()
            ),
            None,
        )
        if numerator_key is None or denominator_key is None:
            bla_channels = {}
            break
        bla_channels[axis] = {
            "num_b": np.asarray(npz[numerator_key], dtype=float).reshape(-1),
            "den_a": np.asarray(npz[denominator_key], dtype=float).reshape(-1),
        }
    if len(bla_channels) == 3:
        return bla_channels

    # Accept flattened keys and the shipped identified b__Gxd/a__Gxd archive.
    explicit: dict[str, dict[str, Any]] = {}
    for axis in AXES:
        prefixes = (axis, f"G{axis}", f"G{axis}d", f"{axis}d")
        num_candidates = tuple(
            candidate
            for prefix in prefixes
            for candidate in (
                f"{prefix}_num_b",
                f"{prefix}_num",
                f"num_b_{prefix}",
                f"num_{prefix}",
                f"b__{prefix}",
            )
        )
        den_candidates = tuple(
            candidate
            for prefix in prefixes
            for candidate in (
                f"{prefix}_den_a",
                f"{prefix}_den",
                f"den_a_{prefix}",
                f"den_{prefix}",
                f"a__{prefix}",
            )
        )
        num_axis = _first_existing(npz, num_candidates)
        den_axis = _first_existing(npz, den_candidates)
        if num_axis is None or den_axis is None:
            return None
        channel = {
            "num_b": np.asarray(num_axis, dtype=float).reshape(-1),
            "den_a": np.asarray(den_axis, dtype=float).reshape(-1),
        }
        for key in (f"dc_gain_{axis}", f"{axis}_dc_gain", f"G{axis}d_dc_gain"):
            if key in npz:
                channel["dc_gain"] = _as_float(npz[key])
                break
        for key in (f"tau_s_{axis}", f"{axis}_tau_s", f"G{axis}_tau_s"):
            if key in npz:
                channel["tau_s"] = _as_float(npz[key])
                break
        explicit[axis] = channel
    return explicit if len(explicit) == 3 else None


def _infer_transfer_kind(channels: Mapping[str, Mapping[str, Any]]) -> str:
    """Infer the user's first-order convention: [1,+rate] continuous, [1,-pole] discrete."""
    normalized_second: list[float] = []
    for axis in AXES:
        den = np.asarray(channels[axis]["den_a"], dtype=float).reshape(-1)
        if den.size < 2 or abs(den[0]) < 1e-12:
            raise ModelFormatError("First-order transfer denominator is invalid")
        normalized_second.append(float(den[1] / den[0]))
    if all(value > 0.0 for value in normalized_second):
        return "continuous"
    if all(value < 0.0 for value in normalized_second):
        return "discrete"
    raise ModelFormatError(
        "Transfer-function NPZ is ambiguous. Set model_kind explicitly. "
        f"Normalized denominator coefficients: {normalized_second}"
    )


def _load_npz(
    path: Path, model_kind: str, sample_time: float | None
) -> DiscreteVelocityModel:
    with np.load(path, allow_pickle=False) as npz_file:
        npz = {key: npz_file[key] for key in npz_file.files}

    keys = tuple(npz)
    dt_value = _first_existing(npz, ("dt", "sample_time", "Ts"))
    fs_value = _first_existing(npz, ("fs", "sample_rate"))
    if model_kind == "continuous" and sample_time is not None:
        dt = float(sample_time)
    elif dt_value is not None:
        dt = _as_float(dt_value)
    elif fs_value is not None:
        dt = 1.0 / _as_float(fs_value)
    elif sample_time is not None:
        dt = float(sample_time)
    else:
        raise ModelFormatError(
            f"NPZ has no dt/fs and no sample_time was provided. Keys: {keys}"
        )

    detected_kind = model_kind
    ad = _first_existing(npz, ("Ad", "A_d", "A_discrete"))
    bd = _first_existing(npz, ("Bd", "B_d", "B_discrete"))
    ac = _first_existing(npz, ("Ac", "A_c", "A_continuous"))
    bc = _first_existing(npz, ("Bc", "B_c", "B_continuous"))
    generic_a = _first_existing(npz, ("A",))
    generic_b = _first_existing(npz, ("B",))
    transfer_channels = _transfer_channels_from_npz(npz)
    tau_vector = _first_existing(npz, ("tau_s", "tau", "time_constants"))
    dc_gain_vector = _first_existing(npz, ("dc_gain", "dc_gains", "gain"))

    if detected_kind == "auto":
        if ad is not None and bd is not None:
            detected_kind = "discrete"
        elif ac is not None and bc is not None:
            detected_kind = "continuous"
        elif generic_a is not None and generic_b is not None:
            # Generic A/B are assumed discrete unless explicitly overridden.
            detected_kind = "discrete"
        elif all(key in npz for key in ("a", "b")):
            detected_kind = "discrete"
        elif all(key in npz for key in ("ax", "ay", "az", "bx", "by", "bz")):
            detected_kind = "discrete"
        elif transfer_channels is not None:
            detected_kind = _infer_transfer_kind(transfer_channels)
        elif tau_vector is not None and dc_gain_vector is not None:
            detected_kind = "continuous"
        else:
            raise ModelFormatError(
                "Unsupported NPZ schema; expected state-space or three-axis transfer coefficients. "
                f"Keys: {keys}"
            )

    if detected_kind == "continuous" and sample_time is not None:
        dt = float(sample_time)

    if detected_kind == "continuous":
        if ac is None or bc is None:
            ac, bc = generic_a, generic_b
        if ac is not None and bc is not None:
            ad_matrix, bd_matrix = _discretize_state_space(
                np.asarray(ac, dtype=float), np.asarray(bc, dtype=float), dt
            )
            axis_models = _axis_models_from_ab(ad_matrix, bd_matrix)
        elif transfer_channels is not None:
            axis_models = {
                axis: _continuous_first_order_to_discrete(transfer_channels[axis], dt)
                for axis in AXES
            }
        elif tau_vector is not None and dc_gain_vector is not None:
            taus = np.asarray(tau_vector, dtype=float).reshape(-1)
            gains = np.asarray(dc_gain_vector, dtype=float).reshape(-1)
            if taus.size < 3 or gains.size < 3:
                raise ModelFormatError("tau_s and dc_gain must each contain three values")
            axis_models = {
                axis: _continuous_first_order_to_discrete(
                    {"tau_s": taus[index], "dc_gain": gains[index]}, dt
                )
                for index, axis in enumerate(AXES)
            }
        else:
            raise ModelFormatError(
                f"Continuous NPZ needs Ac/Bc, A/B, transfer arrays, or tau_s/dc_gain. Keys: {keys}"
            )
    else:
        if ad is None or bd is None:
            ad, bd = generic_a, generic_b
        if ad is not None and bd is not None:
            axis_models = _axis_models_from_ab(ad, bd)
        elif "a" in npz and "b" in npz:
            avec = np.asarray(npz["a"], dtype=float).reshape(-1)
            bvec = np.asarray(npz["b"], dtype=float).reshape(-1)
            if avec.size < 3 or bvec.size < 3:
                raise ModelFormatError("NPZ a/b vectors must have at least three entries")
            gains = (
                np.asarray(npz["dc_gain"], dtype=float).reshape(-1)
                if "dc_gain" in npz
                else bvec[:3] / (1.0 - avec[:3])
            )
            axis_models = {
                axis: AxisModel(float(avec[i]), float(bvec[i]), float(gains[i]))
                for i, axis in enumerate(AXES)
            }
        elif all(key in npz for key in ("ax", "ay", "az", "bx", "by", "bz")):
            axis_models = {}
            for axis in AXES:
                a = _as_float(npz[f"a{axis}"])
                b = _as_float(npz[f"b{axis}"])
                gain_key = f"dc_gain_{axis}"
                gain = _as_float(npz[gain_key]) if gain_key in npz else b / (1.0 - a)
                axis_models[axis] = AxisModel(a=a, b=b, dc_gain=gain)
        elif transfer_channels is not None:
            axis_models = {
                axis: _parse_discrete_channel(transfer_channels[axis])
                for axis in AXES
            }
        else:
            raise ModelFormatError(f"Unsupported discrete NPZ schema. Keys: {keys}")

    return DiscreteVelocityModel(
        dt=dt,
        x=axis_models["x"],
        y=axis_models["y"],
        z=axis_models["z"],
        source=f"{detected_kind} NPZ: {path}",
    )


def load_velocity_model(
    path: str | Path,
    model_kind: str = "auto",
    sample_time: float | None = None,
) -> DiscreteVelocityModel:
    """Load continuous/discrete YAML or NPZ and return a 3-axis discrete model.

    model_kind can be auto, discrete, or continuous. Continuous models are
    discretized with zero-order hold at sample_time (or the dt/fs stored in file).
    """

    model_path = Path(path).expanduser().resolve()
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    normalized_kind = model_kind.strip().lower()
    if normalized_kind not in {"auto", "discrete", "continuous"}:
        raise ValueError("model_kind must be auto, discrete, or continuous")
    if model_path.suffix.lower() in {".yaml", ".yml"}:
        model = _load_yaml(model_path, normalized_kind, sample_time)
    elif model_path.suffix.lower() == ".npz":
        model = _load_npz(model_path, normalized_kind, sample_time)
    else:
        raise ModelFormatError(f"Unsupported model extension: {model_path.suffix}")

    for axis_name, axis in zip(AXES, (model.x, model.y, model.z)):
        if not axis.stable:
            raise ModelFormatError(
                f"Axis {axis_name} has an unstable discrete pole a={axis.a:.6g}"
            )
        if abs(axis.b) < 1e-12:
            raise ModelFormatError(f"Axis {axis_name} has zero input gain")
    return model
