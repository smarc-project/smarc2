import os
import yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
import robust_BLA   

YAML_PATH = ''

STEP_AMP   = 0.1     # low step amplitude (stay near the excitation RMS)
STEP_TEND  = 5.0     # seconds to simulate the step
STEP_FS    = 200.0   # simulation sample rate for the step [Hz] (fine time grid)
STEP_LP_HZ = 1.0     # low-pass cutoff applied to the reference [Hz]; None = raw step
STEP_T0    = 0.5     # time at which the step happens [s] (flat-zero before it)


def read_parquet_safe(path: str):
    if not os.path.exists(path):
        return None
    try:
        return pd.read_parquet(path)
    except Exception as e:
        print(f'[WARN] could not read {path}: {e}')
        return None


def remove_mean(data: np.ndarray) -> np.ndarray:
    return data - data.mean(axis=0, keepdims=True)


def tf_string(b, a):
    """Pretty rational form G(s) = (num) / (den)."""
    num = ' + '.join(f'{c:.4g} s^{len(b) - 1 - i}' for i, c in enumerate(b))
    den = ' + '.join(f'{c:.4g} s^{len(a) - 1 - i}' for i, c in enumerate(a))
    return f'({num}) / ({den})'


def step_matrix(TF, in_names, out_names, amp=STEP_AMP, t_end=STEP_TEND,
                fs=STEP_FS, lp_cutoff=STEP_LP_HZ, lp_order=2, t0=STEP_T0,
                fname='step_matrix.png'):
    """
    Response to a LOW-PASS-FILTERED step command for every element of the matrix.

    A raw step contains infinite-bandwidth content that is never actually sent to
    the drone (the command is always smoothed first). So we pre-filter the step
    with a Butterworth low-pass at `lp_cutoff` Hz, feed THAT through each TF, and
    on the diagonal plot the filtered command as the reference -- i.e. compare the
    smoothed reference you really send against how the system follows it.

    The step happens at t0 (not at t=0) so you see a flat-zero stretch, the rising
    edge, and the settle. Set lp_cutoff=None to recover the ideal (unfiltered) step.
    """
    n = int(t_end * fs)
    t = np.arange(n) / fs
    raw = np.where(t >= t0, amp, 0.0)                

    if lp_cutoff is not None:
        tau_lp = 1.0 / (2.0 * np.pi * lp_cutoff)
        lp = signal.TransferFunction([1.0], [tau_lp, 1.0])
        _, ref, _ = signal.lsim(lp, raw, t)
    else:
        ref = raw

    n_out, n_in = len(out_names), len(in_names)
    fig, ax = plt.subplots(n_out, n_in, figsize=(4 * n_in, 3 * n_out),
                           sharex=True, squeeze=False)
    for k in range(n_out):
        for j in range(n_in):
            tf = TF[k][j]
            a = ax[k][j]
            if k == j:
                a.plot(t, ref, color='tab:orange', ls='--', lw=1.2,
                       label='filtered reference')
            if tf is None:
                a.text(0.5, 0.5, 'no fit', ha='center', va='center',
                       transform=a.transAxes, color='gray')
            else:
                _, yout, _ = signal.lsim(tf, ref, t)
                dc = amp * (tf.num[-1] / tf.den[-1])      
                is_diag = (k == j)
                a.plot(t, yout, lw=2.0 if is_diag else 1.4,
                       color='tab:red' if is_diag else 'tab:blue',
                       label='response' if is_diag else None)
                a.axhline(dc, ls='--', c='gray', lw=0.8)
                a.axhline(0.0, ls=':', c='k', lw=0.5)
            a.grid(alpha=0.3)
            if k == j:
                a.legend(fontsize=7, loc='lower right')
            if k == 0:
                a.set_title(in_names[j], fontsize=8)
            if j == 0:
                a.set_ylabel(out_names[k], fontsize=8)
            if k == n_out - 1:
                a.set_xlabel('time [s]', fontsize=8)
    fig.suptitle(f'Step response of the identified 3x3 velocity matrix '
                 f'(step amplitude {amp})')
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)
    print(f'\n[INFO] saved step-response matrix -> {fname}')


def validate_response(TF, U_seed, Y_seed, fs, in_names, out_names,
                      fname='response_vs_reference.png', TF_diag=None):
    """
    Overlay REFERENCE with the RESPONSE per output axis.

    Curves per axis:
        - reference    : command on the matching input axis (dashed orange)
        - measured     : logged velocity output (blue)              [if Y_seed given]
        - model (full) : full MIMO response of TF (dashed black)
        - model (diag) : diagonal-only response of TF_diag (dash-dot green) [if given]

    TF and TF_diag are (n_out x n_in) grids; entries that are not scipy
    TransferFunction objects (e.g. 0 or None) are skipped -- so a TF_diag holding
    0 in the off-diagonal slots works directly.
    """
    U_seed = np.asarray(U_seed, float)
    Nt = U_seed.shape[0]
    t = np.arange(Nt) / fs
    n_out, n_in = len(out_names), len(in_names)

    def sim_grid(grid):
        Y = np.zeros((Nt, n_out))
        for k in range(n_out):
            for j in range(n_in):
                tf = grid[k][j]
                if not isinstance(tf, signal.TransferFunction):   
                    continue
                _, yk, _ = signal.lsim(tf, U_seed[:, j], t)
                Y[:, k] += yk
        return Y

    Ysim  = sim_grid(TF)
    Ydiag = sim_grid(TF_diag) if TF_diag is not None else None

    fig, ax = plt.subplots(n_out, 1, figsize=(11, 2.6 * n_out),
                           sharex=True, squeeze=False)
    ax = ax[:, 0]
    for k in range(n_out):
        ax[k].plot(t, U_seed[:, k], color='tab:orange', lw=1.0, ls='--',
                   label=f'reference (cmd {in_names[k]})')
        if Y_seed is not None:
            ax[k].plot(t, Y_seed[:, k], color='tab:blue', lw=1.5,
                       label=f'measured {out_names[k]}')
        ax[k].plot(t, Ysim[:, k], color='k', lw=1.3, ls='--',
                   label='model (full MIMO)')
        if Ydiag is not None:
            ax[k].plot(t, Ydiag[:, k], color='tab:green', lw=1.3, ls='-.',
                       label='model (diagonal only)')
        ax[k].set_ylabel(out_names[k], fontsize=8)
        ax[k].grid(alpha=0.3)
        ax[k].legend(fontsize=7, loc='upper right')
    ax[-1].set_xlabel('time [s]')
    fig.suptitle(fname)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)
    print(f'[INFO] saved reference-vs-response -> {fname}')


def save_model(TF_diag, in_names, out_names, path_dir, name, fs=None, notes=""):
    """
    Save the diagonal velocity model as portable coefficients.

    Writes  <path_dir>/<name>.npz   (arrays b__/a__ per channel, load with np.load)
    and     <path_dir>/<name>.yaml  (human-readable coeffs + DC gain + tau + meta).

    Only diagonal entries that are real TransferFunctions are saved.
    """
    os.makedirs(path_dir, exist_ok=True)
    npz_path  = os.path.join(path_dir, name + ".npz")
    yaml_path = os.path.join(path_dir, name + ".yaml")

    arrays = {}
    meta = {"inputs": list(in_names), "outputs": list(out_names),
            "fs": float(fs) if fs is not None else None,
            "structure": "diagonal SISO channels: vel_out = G(s) * cmd_in",
            "notes": notes, "channels": {}}

    for k, out_name in enumerate(out_names):
        tf = TF_diag[k][k]
        if not isinstance(tf, signal.TransferFunction):
            continue
        b = np.atleast_1d(np.asarray(tf.num, dtype=float))
        a = np.atleast_1d(np.asarray(tf.den, dtype=float))
        key = f"{in_names[k]}__to__{out_name}"
        arrays[f"b__{key}"] = b
        arrays[f"a__{key}"] = a
        dc  = b[-1] / a[-1]
        tau = (a[0] / a[1]) if len(a) == 2 else None   
        meta["channels"][key] = {"num_b": b.tolist(), "den_a": a.tolist(),
                                 "dc_gain": float(dc),
                                 "tau_s": float(tau) if tau is not None else None}

    np.savez(npz_path, **arrays)
    with open(yaml_path, "w") as fh:
        yaml.safe_dump(meta, fh, sort_keys=False, default_flow_style=False)
    print(f"[INFO] saved model -> {npz_path}")
    print(f"[INFO] saved model -> {yaml_path}")



if __name__ == '__main__':
    with open(YAML_PATH, 'r') as file:
        config = yaml.safe_load(file)

    end              = config['end']
    fs               = 40                            
    flu_attributes   = config['flu_attributes']      
    vl_gf_attributes = config['vl_gf_attributes']    
    excited_lines    = config.get('excited_lines', None)
    if excited_lines is not None:
        excited_lines = np.asarray(excited_lines, dtype=int)

    # ---- load: one experiment = one seed; count = period within that seed ----
    seeds_in, seeds_out = [], []
    for experiment in config['paths']:
        base = config['paths'][experiment]
        periods_in, periods_out = [], []
        count = 0
        while True:
            df = read_parquet_safe(f'{base}{count}{end}')
            if df is None:
                break
            u_seg = np.column_stack([df[a].to_numpy() for a in flu_attributes])
            y_seg = np.column_stack([df[a].to_numpy() for a in vl_gf_attributes])
            periods_in.append(remove_mean(u_seg))
            periods_out.append(remove_mean(y_seg))
            count += 1
        if periods_in:
            print(f'[INFO] {experiment}: {count} periods')
            seeds_in.append(periods_in)
            seeds_out.append(periods_out)
        else:
            print(f'[INFO] {experiment}: no files found, skipping')

    # ---- assemble into (M, P, N, n_channels), trimming to a common P and N ----
    M = len(seeds_in)
    P = min(len(s) for s in seeds_in)
    N = min(seg.shape[0] for s in seeds_in for seg in s)
    assert M >= 2 and P >= 2, "need >=2 seeds and >=2 periods for the bands"
    print(f'[INFO] M={M} seeds, P={P} periods, N={N} samples/period')
    if M < 5:
        print(f'[WARN] only {M} seeds: the distortion band is a very noisy '
              f'estimate. Treat distortion numbers as provisional; aim for >= 5.')

    def stack(seeds):
        return np.stack([np.stack([seg[:N] for seg in s[:P]]) for s in seeds])

    U_all = stack(seeds_in)     # (M, P, N, n_in)
    Y_all = stack(seeds_out)    # (M, P, N, n_out)

    # 3x3 grid of identified transfer functions: TF[output k][input j]
    TF = [[None] * len(flu_attributes) for _ in range(len(vl_gf_attributes))]
    TF_DIAG = [[0] * len(flu_attributes) for _ in range(len(vl_gf_attributes))]

    # ---- run the BLA per input/output channel pair (SISO) ----
    min_lines = 4   
    for j, in_name in enumerate(flu_attributes):
        for k, out_name in enumerate(vl_gf_attributes):
            u = U_all[..., j]
            y = Y_all[..., k]
            tag = f'{in_name}__to__{out_name}'

            res = robust_BLA.robust_bla(u, y, fs=fs, excited_lines=excited_lines)

            if res.f.size < min_lines:
                print(f'[{tag}] only {res.f.size} excited lines -> BLA only, '
                      f'no TF fit')
                robust_BLA.plot_bla(res, None, path=f'bla_{tag}.png')
                continue

            w = 1.0 / (res.G_std_total ** 2 + 1e-18)
            fit = robust_BLA.fit_tf_auto(res.f, res.G, weights=w, criterion="aic")
            b, a = fit['b'], fit['a']
            TF[k][j] = fit['tf']       
            if k == j:
                TF_DIAG[k][j] = fit['tf']

            print(f'\n[{tag}]')
            print(f'  chosen order       : na={fit["na"]}, nb={fit["nb"]}  '
                  f'(selected by {fit["criterion"].upper()}, not guessed)')
            print(f'  G(s)               = {tf_string(b, a)}')
            print(f'  resonances         : ' + ', '.join(
                f'{wn:.3f} Hz (zeta={z:.3f})'
                for wn, z in zip(fit['wn'], fit['zeta'])))
            print(f'  noise / signal     : {np.median(res.noise_to_signal_db):5.1f} dB')
            print(f'  distortion / signal: {np.median(res.dist_to_signal_db):5.1f} dB')

            robust_BLA.plot_bla(res, fit, path=f'bla_{tag}.png')

    step_matrix(TF, flu_attributes, vl_gf_attributes)

    U_seed0 = np.concatenate(seeds_in[0], axis=0)
    Y_seed0 = np.concatenate(seeds_out[0], axis=0)
    validate_response(TF, U_seed0, Y_seed0, fs,
                      flu_attributes, vl_gf_attributes, "", TF_DIAG)
    

    step_bag_path = ""
    df_step_bag = pd.read_parquet(step_bag_path)
    u_seg = np.column_stack([df_step_bag[a].to_numpy() for a in flu_attributes])
    y_seg = np.column_stack([df_step_bag[a].to_numpy() for a in vl_gf_attributes])

    validate_response(TF, u_seg, y_seg, fs, flu_attributes, vl_gf_attributes, "", TF_DIAG)


    save_model(TF_DIAG, flu_attributes, vl_gf_attributes,
               path_dir="",
               name="",
               fs=fs,
               notes="diagonal closed-loop velocity model (BLA + AIC order fit); "
                     "small-signal regime, DC gain extrapolated below excited band")

    