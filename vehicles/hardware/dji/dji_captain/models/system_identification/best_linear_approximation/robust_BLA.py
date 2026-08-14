"""

Robust-method Best Linear Approximation (BLA) for periodic random-phase multisine
experiments, plus a frequency-domain rational transfer-function fit.

This implements:

    Y(k) = G_BLA(k) U(k) + Y_S(k) + N_Y(k)

    - average over PERIODS  -> suppress measurement noise N_Y, and estimate it
    - average over SEEDS     -> get G_BLA; the seed-to-seed scatter reveals the
                               nonlinear distortion Y_S
    - subtract the noise part from the total scatter -> the DISTORTION band

Data model
----------
Provide input and output already segmented into steady-state periods (transient
removed), organised as real arrays of shape (M, P, N):

    M = number of seeds / realisations   (different random-phase multisines)
    P = number of periods per seed        (steady state only)
    N = samples per period                (exactly one period; coherent sampling)

If your input is the *commanded* multisine (known, identical every period) you may
pass u of shape (M, N) or (N,) and it will be broadcast; the input-noise terms
then vanish automatically.

Use of AI: Used Generative AI to test and verify the correctness of various functions.

"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np



@dataclass
class BLAResult:
    f: np.ndarray                 # frequency vector at excited lines [Hz]
    G: np.ndarray                 # complex BLA estimate  Ghat_BLA(f)
    G_std_noise: np.ndarray       # std of BLA due to measurement noise (mean uncertainty)
    G_std_total: np.ndarray       # total std of BLA over seeds (noise + distortion)
    G_std_nl: np.ndarray          # distortion contribution to the mean uncertainty
    G_std_nl_single: np.ndarray   # distortion level seen on a *single* realisation
    excited_lines: np.ndarray     # integer DFT bin indices that were excited
    fs: float                     # sampling rate [Hz]
    N: int                        # samples per period
    M: int                        # number of seeds
    P: int                        # periods per seed
    G_per_seed: np.ndarray = field(default=None, repr=False)  # (M, n_lines)

    @property
    def dist_to_signal_db(self) -> np.ndarray:
        """Nonlinear-distortion level relative to the FRF, in dB (per line)."""
        return 20.0 * np.log10(self.G_std_nl_single / np.abs(self.G) + 1e-300)

    @property
    def noise_to_signal_db(self) -> np.ndarray:
        return 20.0 * np.log10(self.G_std_noise / np.abs(self.G) + 1e-300)


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _as_MPN(a: np.ndarray, M: int, P: int, N: int) -> np.ndarray:
    """Broadcast (N,) or (M,N) input up to (M,P,N)."""
    a = np.asarray(a, dtype=float)
    if a.ndim == 3:
        return a
    if a.ndim == 2 and a.shape == (M, N):          # per-seed, same each period
        return np.repeat(a[:, None, :], P, axis=1)
    if a.ndim == 1 and a.shape == (N,):            # identical everywhere
        return np.broadcast_to(a, (M, P, N)).copy()
    raise ValueError(f"input shape {a.shape} not compatible with (M,P,N)=({M},{P},{N})")


def detect_excited_lines(Umag: np.ndarray, thr_ratio: float = 0.01) -> np.ndarray:
    """
    Identify excited DFT bins of a multisine from the mean input magnitude spectrum.
    Excited lines carry design amplitude; non-excited lines sit at the noise floor.
    DC (bin 0) is always excluded.
    """
    ref = Umag[1:].max()
    lines = np.where(Umag > thr_ratio * ref)[0]
    lines = lines[lines != 0]
    return lines


# --------------------------------------------------------------------------- #
#  robust-method BLA
# --------------------------------------------------------------------------- #
def robust_bla(u: np.ndarray,
               y: np.ndarray,
               fs: float,
               excited_lines: np.ndarray | None = None,
               thr_ratio: float = 0.01) -> BLAResult:
    """
    Compute the Best Linear Approximation and its noise / distortion bands.

    Parameters
    ----------
    u, y : arrays, output y must be (M, P, N); input u may be (M,P,N), (M,N) or (N,)
    fs   : sampling rate [Hz]
    excited_lines : optional explicit integer bin indices; auto-detected if None
    thr_ratio     : threshold for auto excited-line detection

    Returns
    -------
    BLAResult
    """
    y = np.asarray(y, dtype=float)
    if y.ndim != 3:
        raise ValueError("y must have shape (M, P, N)")
    M, P, N = y.shape
    if P < 2:
        raise ValueError("need P >= 2 periods to estimate the noise band")
    if M < 2:
        raise ValueError("need M >= 2 seeds to estimate the distortion band")
    u = _as_MPN(u, M, P, N)

    U = np.fft.rfft(u, axis=2)          # (M, P, K)
    Y = np.fft.rfft(y, axis=2)          # (M, P, K)
    f_all = np.fft.rfftfreq(N, d=1.0 / fs)

    if excited_lines is None:
        Umag = np.abs(U).mean(axis=(0, 1))          # (K,)
        excited_lines = detect_excited_lines(Umag, thr_ratio)
    excited_lines = np.asarray(excited_lines, dtype=int)
    if excited_lines.size == 0:
        import warnings
        warnings.warn("robust_bla: no excited lines detected for this channel. "
                      "Pass excited_lines explicitly, or check that this input "
                      "axis was actually excited.")
    f = f_all[excited_lines]

    U = U[:, :, excited_lines]          # (M, P, L)
    Y = Y[:, :, excited_lines]

    Ubar = U.mean(axis=1)               # (M, L)
    Ybar = Y.mean(axis=1)               # (M, L)

    def var_of_mean(X, Xbar):
        return (np.abs(X - Xbar[:, None, :]) ** 2).sum(axis=1) / (P * (P - 1))

    varY = var_of_mean(Y, Ybar)         # (M, L)
    varU = var_of_mean(U, Ubar)         # (M, L)
    covYU = ((Y - Ybar[:, None, :]) *
             np.conj(U - Ubar[:, None, :])).sum(axis=1) / (P * (P - 1))  # (M,L)

    G_seed = Ybar / Ubar                # (M, L)

    varG_seed_noise = (np.abs(G_seed) ** 2) * (
        varY / np.abs(Ybar) ** 2
        + varU / np.abs(Ubar) ** 2
        - 2.0 * np.real(covYU / (Ybar * np.conj(Ubar)))
    )
    varG_seed_noise = np.maximum(varG_seed_noise, 0.0)

    G = G_seed.mean(axis=0)             # (L,)

    varG_total = (np.abs(G_seed - G[None, :]) ** 2).sum(axis=0) / (M * (M - 1))

    varG_noise = varG_seed_noise.sum(axis=0) / (M ** 2)

    varG_nl = np.maximum(varG_total - varG_noise, 0.0)

    return BLAResult(
        f=f,
        G=G,
        G_std_noise=np.sqrt(varG_noise),
        G_std_total=np.sqrt(varG_total),
        G_std_nl=np.sqrt(varG_nl),
        G_std_nl_single=np.sqrt(M) * np.sqrt(varG_nl),
        excited_lines=excited_lines,
        fs=fs, N=N, M=M, P=P,
        G_per_seed=G_seed,
    )


# --------------------------------------------------------------------------- #
#  Rational transfer-function fit  (Sanathanan-Koerner iteration, s-domain)
# --------------------------------------------------------------------------- #
def _polyval_asc(coeff_asc: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Evaluate a polynomial given ascending-power coefficients at points x."""
    return np.polynomial.polynomial.polyval(x, coeff_asc)


def fit_tf(f: np.ndarray,
           G: np.ndarray,
           na: int,
           nb: int,
           weights: np.ndarray | None = None,
           iterations: int = 8):
    """
    Fit a continuous-time rational model  G(s) = B(s)/A(s),  s = j*2*pi*f,
    to the (complex) FRF G at frequencies f [Hz], by weighted equation-error LS
    with Sanathanan-Koerner reweighting.

    na, nb : denominator / numerator orders.
    weights: per-line weights. Defaults to 1.

    Returns dict with:
        b, a       : real numerator/denominator coeffs, DESCENDING power (scipy order)
        poles,zeros: np.roots of a, b
        wn, zeta   : natural frequencies [Hz] and damping of the poles
        G_fit      : model evaluated on f (for overlay)
        tf         : scipy.signal.TransferFunction if scipy is available else None
    """
    f = np.asarray(f, float)
    G = np.asarray(G, complex)

    n_unknown = (nb + 1) + na
    if f.size < max(n_unknown, 2):
        raise ValueError(
            f"fit_tf: need >= {max(n_unknown, 2)} frequency lines to fit "
            f"na={na}, nb={nb}, but got {f.size}. This channel likely had no "
            "or too few excited lines (unexcited axis, or detection failed).")

    w = np.ones_like(f) if weights is None else np.asarray(weights, float)
    w = np.sqrt(np.maximum(w, 0.0))

    omega = 2.0 * np.pi * f
    c = omega.max()                       
    shat = 1j * (omega / c)               

    # regressor columns: [ shat^0..shat^nb ,  -G*shat^1 .. -G*shat^na ]
    num_powers = np.vstack([shat ** k for k in range(nb + 1)]).T          # (L, nb+1)
    den_powers = np.vstack([-G * shat ** k for k in range(1, na + 1)]).T  # (L, na)
    Phi = np.hstack([num_powers, den_powers])                             # (L, nb+1+na)
    rhs = G.copy()

    a_full = np.concatenate([[1.0], np.zeros(na)])   
    for _ in range(iterations):
        Aeval = _polyval_asc(a_full, shat)
        wk = (w / np.abs(Aeval))[:, None]            
        theta, *_ = np.linalg.lstsq(Phi * wk, rhs * wk[:, 0], rcond=None)
        bhat = theta[:nb + 1]
        ahat = np.concatenate([[1.0], theta[nb + 1:]])
        a_full = ahat  

    bhat = np.real(bhat)
    ahat = np.real(a_full)

    b_real_asc = np.array([bhat[k] / c ** k for k in range(nb + 1)])
    a_real_asc = np.array([ahat[k] / c ** k for k in range(na + 1)])

    b = b_real_asc[::-1].copy()
    a = a_real_asc[::-1].copy()

    poles = np.roots(a)
    zeros = np.roots(b)
    wn = np.abs(poles) / (2 * np.pi)                     
    zeta = -np.real(poles) / np.maximum(np.abs(poles), 1e-300)

    s = 1j * omega
    G_fit = np.polyval(b, s) / np.polyval(a, s)

    tf = None
    try:
        from scipy.signal import TransferFunction
        tf = TransferFunction(b, a)
    except Exception:
        pass

    return dict(b=b, a=a, poles=poles, zeros=zeros, wn=wn, zeta=zeta,
                G_fit=G_fit, tf=tf)


def fit_tf_auto(f: np.ndarray,
                G: np.ndarray,
                weights: np.ndarray | None = None,
                na_range=range(1, 7),
                strictly_proper: bool = True,
                iterations: int = 8,
                criterion: str = "aic"):
    """
    Fit a rational transfer function WITHOUT hand-picking the order.

    Sweeps denominator orders na in na_range (numerator nb = na-1 if
    strictly_proper else na), fits each with fit_tf, and selects the order that
    minimises an information criterion balancing fit quality against complexity:

        weighted residual sum of squares  RSS = sum_i w_i |G_i - Ghat_i|^2
        k  = number of free parameters (= na + nb + 1)
        n  = number of (complex) data points = f.size
        AIC = n*log(RSS/n) + 2k
        BIC = n*log(RSS/n) + k*log(n)      (criterion="bic", penalises more)

    Raising the order stops helping once the model starts fitting the noise and
    nonlinear distortion rather than the FRF.
    Returns the winning fit dict, augmented with:
        na, nb, order_scores (list of (na, nb, score)), criterion
    """
    f = np.asarray(f, float)
    n = f.size
    best = None
    scores = []
    for na in na_range:
        nb = na - 1 if strictly_proper else na
        if n < (na + nb + 1) + 1:          
            continue
        try:
            fit = fit_tf(f, G, na=na, nb=nb, weights=weights, iterations=iterations)
        except Exception:
            continue
        w = np.ones(n) if weights is None else np.asarray(weights, float)
        rss = float(np.sum(w * np.abs(G - fit["G_fit"]) ** 2))
        rss = max(rss, 1e-300)
        k = na + nb + 1
        if criterion == "bic":
            score = n * np.log(rss / n) + k * np.log(n)
        else:
            score = n * np.log(rss / n) + 2 * k
        scores.append((na, nb, score))
        if best is None or score < best["_score"]:
            fit["_score"] = score
            fit["na"], fit["nb"] = na, nb
            best = fit
    if best is None:
        raise ValueError("fit_tf_auto: no order could be fitted with the given data.")
    best["order_scores"] = scores
    best["criterion"] = criterion
    best.pop("_score", None)
    return best



def multisine(N: int, fs: float, excited_lines, rms: float = 1.0,
              seed: int | None = None) -> np.ndarray:
    """
    One period of a random-phase multisine.

    N            : samples per period
    fs           : sampling rate [Hz]  (period T = N/fs, resolution f0 = fs/N)
    excited_lines: integer DFT bins to excite (multiples of f0)
    rms          : target RMS of the time signal
    """
    rng = np.random.default_rng(seed)
    U = np.zeros(N // 2 + 1, dtype=complex)
    lines = np.asarray(excited_lines, int)
    U[lines] = np.exp(1j * rng.uniform(0, 2 * np.pi, size=lines.size))
    x = np.fft.irfft(U, n=N)
    x *= rms / np.std(x)
    return x



def plot_bla(res: BLAResult, tf_fit: dict | None = None, path: str | None = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    magG = 20 * np.log10(np.abs(res.G))

    floor = 1e-12   
    ax[0].plot(res.f, magG, ".-", label="BLA  |G_BLA|", zorder=3)
    ax[0].plot(res.f, 20 * np.log10(res.G_std_noise + floor),
               label="noise band (std)", lw=1.2)
    ax[0].plot(res.f, 20 * np.log10(res.G_std_nl_single + floor),
               label="nonlinear distortion (std, 1 realisation)", lw=1.2)
    if tf_fit is not None:
        ax[0].plot(res.f, 20 * np.log10(np.abs(tf_fit["G_fit"])),
                   "k--", label="rational fit", zorder=4)
    ax[0].set_ylabel("magnitude [dB]")
    ax[0].legend(fontsize=8)
    ax[0].grid(True, alpha=0.3)
    ax[0].set_title("Robust-method BLA:  FRF with noise & distortion bands")

    ax[1].plot(res.f, np.unwrap(np.angle(res.G)) * 180 / np.pi, ".-", label="BLA phase")
    if tf_fit is not None:
        ax[1].plot(res.f, np.unwrap(np.angle(tf_fit["G_fit"])) * 180 / np.pi,
                   "k--", label="rational fit")
    ax[1].set_ylabel("phase [deg]")
    ax[1].set_xlabel("frequency [Hz]")
    ax[1].legend(fontsize=8)
    ax[1].grid(True, alpha=0.3)

    fig.tight_layout()
    if path:
        fig.savefig(path, dpi=130)
    return fig



if __name__ == "__main__":
    pass