import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import os
import pandas as pd
import math
import plotly.graph_objects as go

def analyze_timestamps(df: pd.DataFrame, ub: float, topic_name: str, save_directory: str ='.') -> None:
    bag = df['bag_timestamp_sec'].to_numpy()
    hdr = df['header_timestamp_sec'].to_numpy()

    if len(bag) != len(hdr):
        print(f'Timestamp length mismatch: {abs(len(bag) - len(hdr))} values')
        return

    diff = bag - hdr
    absd = np.abs(diff)
    dt = np.diff(bag)

    nominal = np.median(dt)
    gap_thr = 3 * nominal
    gaps = np.where(dt > gap_thr)[0]
    n_over = int((absd > ub).sum())

    stats_text = (
        f"Samples: {len(diff)}\n"
        f"Mean |offset|: {absd.mean()*1e3:.3f} ms\n"
        f"Std offset: {diff.std()*1e3:.3f} ms\n"
        f"Max |offset|: {absd.max()*1e3:.3f} ms\n"
        f"|offset| > {ub*1e3:.0f} ms: {n_over}\n"
        f"Neg offsets: {(diff < 0).sum()}\n---\n"
        f"Mean dt: {dt.mean()*1e3:.3f} ms\n"
        f"Std dt: {dt.std()*1e3:.3f} ms\n"
        f"Max dt: {dt.max()*1e3:.3f} ms\n"
        f"Gaps > {gap_thr*1e3:.0f} ms: {len(gaps)}"
    )
    print(stats_text)
    if len(gaps):
        print("Largest gaps:")
        for g in gaps[np.argsort(dt[gaps])[::-1][:10]]:
            print(f"  t={bag[g]-bag[0]:7.2f}s   gap={dt[g]*1e3:8.1f} ms")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    positive = diff[diff > 0]
    if positive.size:
        lo = max(positive.min(), 1e-5)
        hi = absd.max()
        log_bins = np.logspace(np.log10(lo), np.log10(hi), 25)

        counts, bins, _ = ax1.hist(diff, bins=log_bins, edgecolor='black', log=True)
        ax1.set_xscale('log')
        ax1.set_xlim(lo, hi)
        for i in range(len(counts)):
            if counts[i] > 0:
                x_center = np.sqrt(bins[i] * bins[i + 1])
                ax1.text(x_center, counts[i], f'{int(counts[i])}',
                         ha='center', va='bottom', fontsize=8, rotation=0)
    ax1.set_xlabel('receive - header offset (s, log)')
    ax1.set_ylabel('count (log)')
    ax1.set_title(f'Offset distribution - {topic_name}')
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    ax1.text(0.95, 0.95, stats_text, transform=ax1.transAxes, fontsize=9,
             va='top', ha='right', bbox=props)

    dt_ub = 5 * nominal
    ax2.hist(dt, bins=40, range=(0, dt_ub), edgecolor='black', log=True)
    ax2.axvline(nominal, color='green', ls='--', label=f'nominal {nominal*1e3:.1f} ms')
    ax2.set_xlim(0, dt_ub)
    ax2.set_xlabel('dt (s)  [clipped; big gaps listed in console]')
    ax2.set_ylabel('count (log)')
    ax2.set_title(f'Sampling interval distribution - {topic_name}')
    ax2.legend()

    fig.suptitle(f'Timing - {topic_name}')
    plt.tight_layout()
    plt.show()

    if input("\nSave this plot? (y/n): ").strip().lower() in ('y', 'yes'):
        os.makedirs(save_directory, exist_ok=True)
        fp = os.path.join(save_directory, f'timing_distribution_{topic_name}.png')
        fig.savefig(fp, dpi=300, bbox_inches='tight')
        print(f"Saved to: {fp}")
    else:
        print("Not saved.")

def static_path(points: np.ndarray, t: np.ndarray) -> None:
    """Whole trajectory at once, coloured by time.
    Args:
        points : Nx3 array of (x,y,z) coordinates
        t : an array of timestamps corresponding to each point
    """
    p = pv.Plotter()
    p.set_background('white')

    line = pv.lines_from_points(points)
    line['time_s'] = t - t[0]
    p.add_mesh(line, scalars='time_s', line_width=4, cmap='viridis',
               scalar_bar_args={'title': 'time (s)'})

    p.add_mesh(pv.PolyData(points[:1]), color='green', point_size=15,
               render_points_as_spheres=True)
    p.add_mesh(pv.PolyData(points[-1:]), color='red', point_size=15,
               render_points_as_spheres=True)

    p.show_grid()
    p.add_axes()
    p.show()

def animate_path(points: np.ndarray, t: np.ndarray, n_frames: int = 500) -> None:
    """
    Animates a 3D trajectory moving over time with a play/pause toggle.

    Args:
        points : An Nx3 array of (x, y, z) coordinates.
        t : An array of timestamps corresponding to each point.
        n_frames : The target number of frames for the animation. Defaults to 500.
    """
    p = pv.Plotter()
    p.set_background('white')
    p.add_mesh(pv.lines_from_points(points), color='lightgrey', line_width=3)

    marker = pv.Sphere(radius=0.5)
    actor = p.add_mesh(marker, color='red')
    actor.position = points[0]
    p.show_grid()
    p.add_axes()

    n = len(points)
    stride = max(1, n // n_frames)
    state = {'i': 0, 'paused': False}

    def draw_label():
        i = state['i']
        status = 'PAUSED' if state['paused'] else 'running'
        p.add_text(f"idx: {i}\nt: {t[i]-t[0]:.2f} s\n[{status}]",
                   name='lbl', position='upper_left', font_size=12)

    draw_label()

    def toggle(flag):
        state['paused'] = flag
        draw_label()
        p.render()

    p.add_checkbox_button_widget(toggle, value=False, position=(10, 10),
                                 size=40, color_on='red', color_off='green')
    p.add_text("Stop / Resume", position=(60, 18), font_size=10, name='btn_lbl')

    def update(step):
        if state['paused']:
            return
        actor.position = points[state['i']]
        draw_label()
        p.render()
        state['i'] = min(state['i'] + stride, n - 1)

    p.add_timer_event(max_steps=10_000_000, duration=20, callback=update)
    p.show()

def _nearest_index(arr: np.ndarray, value: float) -> int:
    """Index of the array element closest to `value`, for snapping a cursor
    x-position onto the nearest actual sample."""
    idx = np.searchsorted(arr, value)
    if idx <= 0:
        return 0
    if idx >= len(arr):
        return len(arr) - 1
    before, after = arr[idx - 1], arr[idx]
    return idx - 1 if abs(value - before) <= abs(after - value) else idx

def _attach_hover_index(fig, axes: np.ndarray, time: np.ndarray, chunk_data: np.ndarray) -> None:
    """Show the sample index (and value) of the nearest point as the cursor
    moves over any subplot in `axes` -- lets you read off segment boundaries
    by eye instead of guessing indices from the tick labels."""
    annotations = []
    for ax in axes:
        ann = ax.annotate('', xy=(0, 0), xytext=(15, 15), textcoords='offset points',
                           bbox=dict(boxstyle='round', fc='lightyellow', ec='gray'),
                           arrowprops=dict(arrowstyle='->'))
        ann.set_visible(False)
        annotations.append(ann)

    ax_to_row = {ax: i for i, ax in enumerate(axes)}

    def on_move(event):
        ax = event.inaxes
        if ax not in ax_to_row or event.xdata is None:
            changed = any(ann.get_visible() for ann in annotations)
            for ann in annotations:
                ann.set_visible(False)
            if changed:
                fig.canvas.draw_idle()
            return

        row = ax_to_row[ax]
        idx = _nearest_index(time, event.xdata)
        ann = annotations[row]
        ann.xy = (time[idx], chunk_data[row][idx])
        ann.set_text(f'idx={idx}\nvalue={chunk_data[row][idx]:.3f}')
        ann.set_visible(True)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', on_move)

def plot_data(time: np.ndarray, data: np.ndarray, title: str, subtitles: list[str], xlabel: str = 'Time',
              tick_step: float = None, hover_index: bool = False) -> None:
    """
    Plots multiple data streams over a common time axis, with a max of 3 subplots per figure.
    If there are more than 3 streams, it automatically generates multiple figures.

    Args:
        time (np.ndarray): 1D array of x-axis values (length N) -- time, sample index, etc.
        data (np.ndarray): 1D or 2D array of data values. A 1D array is treated as a
            single signal of shape (N,). A 2D array is treated as shape (n_data, N).
        title (str): The main title for the overarching dataset.
        subtitles (list[str] | str): Titles for each subplot. A single string is accepted
            and used for the single series case.
        xlabel (str): Label for the shared x-axis, matching whatever `time` actually holds.
        tick_step (float): If set, spacing between x-axis ticks (e.g. 50 for a tick
            every 50 samples). Defaults to matplotlib's automatic tick placement.
        hover_index (bool): If True, hovering over a subplot shows the sample
            index and value of the nearest point (requires an interactive
            matplotlib backend, e.g. not when saving straight to a file).
    """
    time = np.asarray(time)
    if time.ndim != 1:
        raise ValueError(f"time must be 1D, got shape {time.shape}")

    if isinstance(data, (list, tuple)):
        data_arrays = [np.asarray(row, dtype=float).reshape(-1) for row in data]
        if not data_arrays:
            raise ValueError("data must contain at least one series")
        n_samples = len(data_arrays[0])
        if any(len(row) != n_samples for row in data_arrays):
            raise ValueError("all data series must have the same length")
        data = np.vstack(data_arrays)
    else:
        data = np.asarray(data, dtype=float)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        elif data.ndim != 2:
            raise ValueError(f"data must be 1D or 2D, got shape {data.shape}")

    if data.shape[1] != len(time):
        raise ValueError(f"time and data length mismatch: {len(time)} vs {data.shape[1]}")

    n_data = data.shape[0]
    max_subplots = 3

    if isinstance(subtitles, str):
        subtitles = [subtitles]
    else:
        subtitles = list(subtitles)

    if len(subtitles) != n_data:
        if len(subtitles) == 1 and n_data == 1:
            subtitles = [subtitles[0]]
        else:
            print(f"Warning: Data has {n_data} rows, but received {len(subtitles)} subtitles.")
            if len(subtitles) < n_data:
                subtitles = subtitles + [f"Series {i + 1}" for i in range(len(subtitles), n_data)]
            else:
                subtitles = subtitles[:n_data]

    num_figs = math.ceil(n_data / max_subplots)

    for fig_idx in range(num_figs):
        start_idx = fig_idx * max_subplots
        end_idx = min(start_idx + max_subplots, n_data)

        chunk_data = data[start_idx:end_idx]
        chunk_subtitles = subtitles[start_idx:end_idx]
        chunk_size = chunk_data.shape[0]

        fig, axes = plt.subplots(
            nrows=chunk_size,
            ncols=1,
            sharex=True,
            figsize=(8, 2.5 * chunk_size),
            squeeze=False
        )

        axes = axes.flatten()

        for i, (ax, row_data, sub) in enumerate(zip(axes, chunk_data, chunk_subtitles)):
            ax.plot(time, row_data)

            global_index = start_idx + i + 1
            ax.set_ylabel(f'Data {global_index}')
            ax.set_title(sub)
            ax.grid(True, linestyle='--', alpha=0.7)
            if tick_step is not None:
                ax.xaxis.set_major_locator(MultipleLocator(tick_step))
                ax.tick_params(axis='x', labelrotation=90)

        if num_figs > 1:
            fig.suptitle(f"{title} (Part {fig_idx + 1}/{num_figs})", fontsize=14)
        else:
            fig.suptitle(title, fontsize=14)

        axes[-1].set_xlabel(xlabel)

        if hover_index:
            _attach_hover_index(fig, axes, np.asarray(time), chunk_data)

        plt.tight_layout()
        plt.show()

def plot_data_with_gaps(time: np.ndarray, data: list, title: str, subtitles: list[str],
                         gap_thr_mult: float = 3.0) -> None:
    """
    Plots multiple data streams over a common time axis, breaking the line and
    shading the background wherever the gap between consecutive samples is
    larger than `gap_thr_mult` times the nominal (median) sampling interval —
    i.e. wherever the topic went silent. Max of 3 subplots per figure.

    Args:
        time (np.ndarray): 1D array of timestamps (length N), used as-is for the x axis.
        data (list): list of 1D arrays/Series, one per channel (each length N).
        title (str): The main title for the overarching dataset.
        subtitles (list[str]): A list of titles for each individual subplot.
        gap_thr_mult (float): gap is flagged when dt > gap_thr_mult * median(dt).
    """
    time = np.asarray(time)
    data = [np.asarray(row, dtype=float) for row in data]
    n_data = len(data)
    max_subplots = 3

    if len(subtitles) != n_data:
        print(f"Warning: Data has {n_data} rows, but received {len(subtitles)} subtitles.")

    dt = np.diff(time)
    nominal = np.median(dt)
    gap_thr = gap_thr_mult * nominal
    gap_idx = np.where(dt > gap_thr)[0]

    if len(gap_idx):
        print(f"{title}: {len(gap_idx)} gap(s) > {gap_thr*1e3:.1f} ms (nominal dt {nominal*1e3:.1f} ms)")
        for g in gap_idx[np.argsort(dt[gap_idx])[::-1]]:
            print(f"  t={time[g]:.3f}s -> {time[g+1]:.3f}s   gap={dt[g]:.3f}s")
    else:
        print(f"{title}: no gaps > {gap_thr*1e3:.1f} ms (nominal dt {nominal*1e3:.1f} ms)")

    t_mid = (time[gap_idx] + time[gap_idx + 1]) / 2 if len(gap_idx) else np.array([])

    num_figs = math.ceil(n_data / max_subplots)

    for fig_idx in range(num_figs):
        start_idx = fig_idx * max_subplots
        end_idx = min(start_idx + max_subplots, n_data)

        chunk_data = data[start_idx:end_idx]
        chunk_subtitles = subtitles[start_idx:end_idx]
        chunk_size = len(chunk_data)

        fig, axes = plt.subplots(
            nrows=chunk_size,
            ncols=1,
            sharex=True,
            figsize=(10, 2.5 * chunk_size),
            squeeze=False
        )
        axes = axes.flatten()

        for ax, row_data, sub in zip(axes, chunk_data, chunk_subtitles):
            if len(gap_idx):
                t_plot = np.insert(time, gap_idx + 1, t_mid)
                y_plot = np.insert(row_data, gap_idx + 1, np.nan)
            else:
                t_plot, y_plot = time, row_data

            ax.plot(t_plot, y_plot, marker='.', markersize=3)
            for g in gap_idx:
                ax.axvspan(time[g], time[g + 1], color='red', alpha=0.15)

            ax.set_ylabel(sub)
            ax.set_title(sub)
            ax.grid(True, linestyle='--', alpha=0.7)

        if num_figs > 1:
            fig.suptitle(f"{title} (Part {fig_idx + 1}/{num_figs})", fontsize=14)
        else:
            fig.suptitle(title, fontsize=14)

        axes[-1].set_xlabel('bag_timestamp_sec')

        plt.tight_layout()
        plt.show()

def plot_series_comparison(time1: np.ndarray, data1: list, label1: str,
                            time2: np.ndarray, data2: list, label2: str,
                            title: str, subtitles: list[str]) -> None:
    """
    Overlays two data sources with independent time bases, one subplot per
    channel (max 3 per figure) -- e.g. comparing FLU setpoints against odom
    twist. Each source is drawn against its own timestamps, so mismatched
    sample counts or rates between the two sources need no resampling,
    interpolation, or zero-filling: matplotlib plots each line independently
    on a shared x axis.

    Args:
        time1, time2 (np.ndarray): 1D timestamp arrays for each source.
        data1, data2 (list): lists of 1D arrays/Series, one per channel,
            paired channel-for-channel by position with `subtitles`.
        label1, label2 (str): legend labels identifying each source.
        title (str): overarching figure title.
        subtitles (list[str]): per-channel subplot titles.
    """
    time1 = np.asarray(time1)
    time2 = np.asarray(time2)
    data1 = [np.asarray(row, dtype=float) for row in data1]
    data2 = [np.asarray(row, dtype=float) for row in data2]
    n_data = len(subtitles)
    max_subplots = 3

    if len(data1) != n_data or len(data2) != n_data:
        print(f"Warning: '{label1}' has {len(data1)} channels, '{label2}' has "
              f"{len(data2)}, but received {n_data} subtitles.")

    num_figs = math.ceil(n_data / max_subplots)

    for fig_idx in range(num_figs):
        start_idx = fig_idx * max_subplots
        end_idx = min(start_idx + max_subplots, n_data)
        chunk_subtitles = subtitles[start_idx:end_idx]
        chunk_size = len(chunk_subtitles)

        fig, axes = plt.subplots(
            nrows=chunk_size,
            ncols=1,
            sharex=True,
            figsize=(10, 2.5 * chunk_size),
            squeeze=False
        )
        axes = axes.flatten()

        for i, (ax, sub) in enumerate(zip(axes, chunk_subtitles)):
            idx = start_idx + i
            ax.plot(time1, data1[idx], color='tab:blue', marker='.', markersize=3, label=label1)
            ax.plot(time2, data2[idx], color='tab:orange', marker='.', markersize=3,
                    linestyle='--', alpha=0.8, label=label2)
            ax.set_ylabel(sub)
            ax.set_title(sub)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()

        if num_figs > 1:
            fig.suptitle(f"{title} (Part {fig_idx + 1}/{num_figs})", fontsize=14)
        else:
            fig.suptitle(title, fontsize=14)

        axes[-1].set_xlabel('bag_timestamp_sec')

        plt.tight_layout()
        plt.show()

def plot_relative_timestamp(time: np.ndarray, title: str, n_ticks: int = 15) -> None:

    time = np.asarray(time)
    delta_t = np.diff(time)

    indices = np.arange(len(delta_t))
    times_sec = time[1:]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=indices,
        y=delta_t,
        mode='lines+markers',
        name='Delta t',
        marker=dict(size=4),
        xaxis='x'
    ))

    tick_idx = np.linspace(0, len(indices) - 1, num=min(n_ticks, len(indices))).astype(int)
    tick_idx = np.unique(tick_idx)

    fig.add_trace(go.Scatter(
        x=[indices[0], indices[-1]],
        y=[delta_t[0], delta_t[-1]],
        mode='markers',
        xaxis='x2',
        showlegend=False,
        opacity=0,
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(
            title='Message Index',
            side='bottom'
        ),
        xaxis2=dict(
            title='Elapsed Time (Seconds)',
            overlaying='x',   
            matches='x',      
            side='top',
            tickmode='array',
            tickvals=indices[tick_idx],
            ticktext=[f'{t:.1f}' for t in times_sec[tick_idx]]
        ),
        yaxis_title='Time Difference (Seconds)',
        hovermode='x unified'
    )

    fig.show()
    input("Press Enter to continue...")
