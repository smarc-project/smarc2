import numpy as np
from scipy.spatial.transform import Rotation, Slerp
import scipy,signal 
import scipy.interpolate
import pandas as pd


def numpy2parquet(dict: dict[str, np.ndarray], clock: str, prefix:str, attribute_list: list[str]) -> pd.DataFrame:
    df = pd.DataFrame({'bag_timestamp_sec': clock})
    for attribute in attribute_list:
        df[prefix + '_' + attribute] = dict[attribute]
    return df

def segment_by_time(df: pd.DataFrame, t_start: int, t_end: int, clock: str) -> pd.DataFrame:
    """Return the rows whose timestamp falls in [t_start, t_end] on `clock`."""
    mask = (df[clock] >= t_start) & (df[clock] <= t_end)
    return df.loc[mask].reset_index(drop=True)

def report_segment(df: pd.DataFrame, name:str, clock: str) -> None:
    """Print a quick sanity line: sample count, duration, largest dt."""
    n = len(df)
    if n < 2:
        print(f'  {name:28s}: {n} samples  (!! too few)')
        return
    t = df[clock].to_numpy()
    dt = np.diff(t)
    dur = t[-1] - t[0]
    rate = (n - 1) / dur if dur > 0 else float('nan')
    print(f'  {name:28s}: {n:6d} samples  {dur:6.1f}s  ~{rate:5.1f} Hz  '
          f'max dt {dt.max()*1e3:7.1f} ms')

def decimate_topic(grid: np.ndarray, 
    t_p: np.ndarray, 
    segmented_df: pd.DataFrame, 
    name_list: list[str], 
    grid_freq: float
) -> tuple[dict[str, np.ndarray], dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    """
    Resamples and filters time-series data onto a uniform time grid to prevent aliasing.

    Args:
        grid (np.ndarray): The target uniform time array to evaluate the final data on.
        t_p (np.ndarray): The original, potentially non-uniform timestamp array.
        segmented_df (pd.DataFrame): The DataFrame containing the data streams.
        name_list (list[str]): A list of column names in segmented_df to process.
        grid_freq (float): The target sampling frequency (Hz) of the final grid.

    Returns:
        tuple: A tuple containing two dictionaries:
            - topic_on_grid (dict): Maps each topic name to its decimated data array.
            - psd (dict): Maps each topic name to a tuple of Power Spectral Density 
                          arrays (f_raw, P_raw, f_filt, P_filt).
    """
    topic_on_grid = {}
    psd = {}

    fs_native = (len(t_p) - 1) / (t_p[-1] - t_p[0])
    t_uni = np.arange(t_p[0], t_p[-1], 1.0 / fs_native)

    b, a = scipy.signal.butter(4, 0.7 * (grid_freq / 2), fs=fs_native, btype='low')

    for name in name_list:
        data_topic = segmented_df[name].to_numpy()
        
        data_uni = np.interp(t_uni, t_p, data_topic)
        
        data_filt = scipy.signal.filtfilt(b, a, data_uni)
        
        f = scipy.interpolate.interp1d(
            t_uni, data_filt, kind='linear',
            bounds_error=False,
            fill_value=(data_filt[0], data_filt[-1])
        )
        topic_on_grid[name] = f(grid)
        
        f_raw,  P_raw  = scipy.signal.welch(data_uni,  fs=fs_native, nperseg=4096)
        f_filt, P_filt = scipy.signal.welch(data_filt, fs=fs_native, nperseg=4096)
        psd[name] = (f_raw, P_raw, f_filt, P_filt)

    return topic_on_grid, psd

def decimate_zoh(grid, t_p, df_seg, name_list):
    zoh_df = {}
    data_src = {c: df_seg[c].to_numpy() for c in name_list}
    for c in name_list:
            f = scipy.interpolate.interp1d(t_p, data_src[c], kind='previous',
                                           bounds_error=False,
                                           fill_value=(data_src[c][0], data_src[c][-1]))
            zoh_df[c] = f(grid)
    return zoh_df

def flu_to_world(t_flu: np.ndarray, flu_xyz: np.ndarray,
                  t_att: np.ndarray, quat_xyzw: np.ndarray, yaw_only: bool = True) -> np.ndarray:
    """
    Rotates body-frame FLU (forward-left-up) vectors into the world (ENU)
    frame using the vehicle attitude.

    Args:
        t_flu (np.ndarray): FLU command timestamps, shape (N,).
        flu_xyz (np.ndarray): body-frame (forward, left, up) vectors, shape (N, 3).
        t_att (np.ndarray): attitude timestamps, shape (M,).
        quat_xyzw (np.ndarray): attitude quaternions [x, y, z, w], shape (M, 4).
        yaw_only (bool): if True (default), rotate by yaw alone and leave the
            vertical (up) component untouched, matching PSDK's FLU velocity
            convention where the vertical rate is gravity-aligned rather than
            tilted with roll/pitch. If False, apply the full 3D attitude.

    Returns:
        np.ndarray: world-frame (ENU) vectors, shape (N, 3).
    """
    t_flu = np.asarray(t_flu, dtype=float)
    flu_xyz = np.asarray(flu_xyz, dtype=float)
    t_att = np.asarray(t_att, dtype=float)
    quat_xyzw = np.asarray(quat_xyzw, dtype=float)

    order = np.argsort(t_att)
    t_att = t_att[order]
    quat_xyzw = quat_xyzw[order]

    keep = np.concatenate(([True], np.diff(t_att) > 0))
    t_att = t_att[keep]
    quat_xyzw = quat_xyzw[keep]

    n_below = int(np.sum(t_flu < t_att[0]))
    n_above = int(np.sum(t_flu > t_att[-1]))
    if n_below or n_above:
        print(f"flu_to_world: {n_below} FLU sample(s) before attitude start and "
              f"{n_above} after attitude end; clamped to nearest attitude sample.")
    t_query = np.clip(t_flu, t_att[0], t_att[-1])

    slerp = Slerp(t_att, Rotation.from_quat(quat_xyzw))
    rot_at_flu = slerp(t_query)

    if yaw_only:
        yaw = rot_at_flu.as_euler('ZYX')[:, 0]
        rot_at_flu = Rotation.from_euler('z', yaw)

    return rot_at_flu.apply(flu_xyz)

def world_to_flu(t_world: np.ndarray, world_xyz: np.ndarray,
                  t_att: np.ndarray, quat_xyzw: np.ndarray, yaw_only: bool = True) -> np.ndarray:
    """
    Rotates world-frame (ENU) vectors into the body-frame FLU (forward-left-up)
    convention using the vehicle attitude.

    Args:
        t_world (np.ndarray): world-frame sample timestamps, shape (N,).
        world_xyz (np.ndarray): world-frame (east, north, up) vectors, shape (N, 3).
        t_att (np.ndarray): attitude timestamps, shape (M,).
        quat_xyzw (np.ndarray): attitude quaternions [x, y, z, w], shape (M, 4).
        yaw_only (bool): if True (default), rotate by yaw alone and leave the
            vertical (up) component untouched, matching PSDK's FLU velocity
            convention where the vertical rate is gravity-aligned rather than
            tilted with roll/pitch. If False, apply the inverse of the full 3D
            attitude.

    Returns:
        np.ndarray: body-frame FLU vectors, shape (N, 3).
    """
    t_world = np.asarray(t_world, dtype=float)
    world_xyz = np.asarray(world_xyz, dtype=float)
    t_att = np.asarray(t_att, dtype=float)
    quat_xyzw = np.asarray(quat_xyzw, dtype=float)

    order = np.argsort(t_att)
    t_att = t_att[order]
    quat_xyzw = quat_xyzw[order]

    keep = np.concatenate(([True], np.diff(t_att) > 0))
    t_att = t_att[keep]
    quat_xyzw = quat_xyzw[keep]

    n_below = int(np.sum(t_world < t_att[0]))
    n_above = int(np.sum(t_world > t_att[-1]))
    if n_below or n_above:
        print(f"world_to_flu: {n_below} sample(s) before attitude start and "
              f"{n_above} after attitude end; clamped to nearest attitude sample.")
    t_query = np.clip(t_world, t_att[0], t_att[-1])

    slerp = Slerp(t_att, Rotation.from_quat(quat_xyzw))
    rot_at_world = slerp(t_query)

    if yaw_only:
        yaw = rot_at_world.as_euler('ZYX')[:, 0]
        rot_at_world = Rotation.from_euler('z', yaw)

    return rot_at_world.inv().apply(world_xyz)

def zero_fill_gaps(
    t: np.ndarray, 
    data_list: list[np.ndarray], 
    t_ref: np.ndarray, 
    gap_factor: float = 3.0
) -> tuple[np.ndarray, list[np.ndarray]]:
    """
    
    Args:
        t (np.ndarray): The original timestamp array.
        data_list (list[np.ndarray]): A list of data arrays corresponding to `t`.
        t_ref (np.ndarray): A reference timestamp array determining the full required time span.
        gap_factor (float, optional): Multiplier for the nominal dt to define a gap. Defaults to 3.0.
        
    Returns:
        tuple[np.ndarray, list[np.ndarray]]: A tuple containing the newly extended time array 
                                             and the zero-padded data list, sorted by time.
    """
    t = np.asarray(t, dtype=float)
    t_ref = np.asarray(t_ref, dtype=float)
    dt = np.diff(t)
    
    nominal = np.median(dt) if len(dt) > 0 else 0.0
    gap_thr = gap_factor * nominal if nominal > 0 else 0.0
    eps = nominal * 0.1 if nominal > 0 else 1e-6

    insert_times = []
    
    for i in np.where(dt > gap_thr)[0]:
        insert_times.append(t[i] + eps)
        insert_times.append(t[i + 1] - eps)

    t_start, t_end = t_ref[0], t_ref[-1]
    
    if t_start < t[0]:
        insert_times.append(t_start)
        insert_times.append(t[0] - eps)
        
    if t_end > t[-1]:
        insert_times.append(t[-1] + eps)
        insert_times.append(t_end)

    insert_times = np.array(sorted(set(insert_times)))
    
    new_t = np.concatenate([t, insert_times])
    order = np.argsort(new_t)
    new_t = new_t[order]

    new_data_list = []
    
    for vals in data_list:
        zeros = np.zeros(len(insert_times))
        new_data_list.append(np.concatenate([vals, zeros])[order])

    return new_t, new_data_list

def relative_clock(df: pd.DataFrame, clock: str) -> pd.DataFrame:
    time = df[clock]
    
    differential_time = time - time.iloc[0]
    df['relative_clock'] = differential_time
        
    return df