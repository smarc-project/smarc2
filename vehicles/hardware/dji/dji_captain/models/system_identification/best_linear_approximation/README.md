# Best Linear Approximation (BLA)

This directory contains the code that turns periodic multisine flight data into a
**linear velocity model of the DJI M350**, together with an honest measurement of how
much of the response is *not* linear.

The system identified here is the closed-loop velocity channel of the drone:

```
input   FLU_axes_0/1/2                       (commanded FLU velocity setpoints)
            |
            v
      [ DJI flight controller + airframe ]
            |
            v
output  FLUvelocity_ground_fused_x/y/z       (measured velocity, FLU frame)
```

The method used is the **robust-method BLA** (Pintelon & Schoukens): the drone is
excited with several *random-phase multisines* (seeds), each repeated for several
*periods*, and the frequency response is estimated line-by-line together with two
separate uncertainty bands — one for measurement noise, one for nonlinear distortion.
The maths is fully derived in [documentation.md](documentation.md); this file
describes the code.

---

## Files

| File | Role |
|---|---|
| [robust_BLA.py](robust_BLA.py) | **Library.** Self-contained, dependency-light (numpy; scipy only optional). Implements the BLA estimator, the rational transfer-function fit, multisine generation, plotting, and a synthetic self-test. Nothing in it knows about ROS, parquet, or the drone. |
| [BLA.py](BLA.py) | **Driver / pipeline.** Loads the experiment data described by `config.yaml`, runs `robust_BLA` on all 9 input→output channel pairs, fits transfer functions, produces validation plots, and exports the model. |
| [config.yaml](config.yaml) | **Experiment description.** Where the parquet periods live and which columns are inputs and outputs. |

The expected input data is what the sibling
[data_extractor](../data_extractor/) and [validate_bag](../validate_bag/) tools
produce: one parquet file **per period**, already resampled to a uniform grid,
rotated into the FLU frame, and with transients cut away.

---

## `robust_BLA.py` — the library

No ROS, no pandas, no I/O beyond an optional figure save. It can be dropped into any
project. Contents, in the order they appear in the file:

### `BLAResult` (dataclass)

The complete result of one SISO identification. Fields:

| Field | Shape | Meaning |
|---|---|---|
| `f` | `(L,)` | frequencies of the excited lines [Hz] |
| `G` | `(L,)` complex | the BLA estimate $\hat G_{\mathrm{BLA}}$ |
| `G_std_noise` | `(L,)` | std of `G` caused by **measurement noise** |
| `G_std_total` | `(L,)` | total std of `G` over seeds (noise **+** distortion) |
| `G_std_nl` | `(L,)` | distortion contribution to the uncertainty **of the mean** |
| `G_std_nl_single` | `(L,)` | distortion level you would see on **one** realisation (`sqrt(M) * G_std_nl`) |
| `excited_lines` | `(L,)` int | DFT bin indices that were excited |
| `fs`, `N`, `M`, `P` | scalars | sample rate, samples/period, seeds, periods per seed |
| `G_per_seed` | `(M, L)` complex | the per-seed FRFs, before averaging |

Two convenience properties turn the bands into readable numbers:

* `dist_to_signal_db` — $20\log_{10}(\sigma_{\mathrm{NL,single}}/|G|)$, i.e. *"the
  nonlinear distortion sits X dB below the linear response at this frequency"*.
* `noise_to_signal_db` — the same for measurement noise.

`G_std_nl` and `G_std_nl_single` differ deliberately: the first shrinks as you add
seeds (it is an error bar on your estimate), the second does not (it is a property of
the system and the excitation). **Judge the nonlinearity with `dist_to_signal_db`, not
with the error bar.**

### `robust_bla(u, y, fs, excited_lines=None, thr_ratio=0.01) -> BLAResult`

The core estimator. Expects data already segmented into steady-state periods:

* `y` — real array `(M, P, N)`
* `u` — `(M, P, N)`, or `(M, N)` if the input is identical every period, or `(N,)` if
  it is identical everywhere. The reduced shapes are broadcast by `_as_MPN`, and the
  input-noise terms then vanish by construction (all periods equal ⇒ zero scatter).

Requires `M >= 2` (needed for the distortion band) and `P >= 2` (needed for the noise
band); it raises otherwise. What it does, in four steps:

1. **`rfft` every period** and keep only the excited lines. The `1/N` normalisation is
   never applied — it cancels in the ratio $\bar Y/\bar U$.
2. **Average over periods** → suppresses measurement noise; the period-to-period
   scatter *is* the noise estimate (variance of the mean, denominator $P(P-1)$).
   The input–output noise covariance is computed too.
3. **One FRF per seed**, $\hat G^{[m]} = \bar Y^{[m]}/\bar U^{[m]}$, and propagate the
   noise variances through the division to first order.
4. **Average over seeds** → the BLA. The seed-to-seed scatter gives the *total*
   variance; subtracting the propagated noise variance leaves the **distortion**
   variance. Both subtractions are clipped at zero (`np.maximum(..., 0.0)`), because a
   finite-sample noise estimate can exceed the total scatter when the system is
   essentially linear.

### `detect_excited_lines(Umag, thr_ratio=0.01)`

Finds the excited multisine bins automatically: any bin whose mean input magnitude
exceeds `thr_ratio` × (largest non-DC magnitude). DC is always dropped. Used only when
`excited_lines` is not supplied. If the recorded command is noisy, or an axis was never
excited, pass the designed lines explicitly instead — the auto-detector will otherwise
pick up noise bins.

### `fit_tf(f, G, na, nb, weights=None, iterations=8)`

Fits a **continuous-time** rational model $G(s) = B(s)/A(s)$, $s = j2\pi f$, to the
complex FRF, by weighted equation-error least squares with **Sanathanan–Koerner
reweighting** (8 iterations by default), which drives the equation-error cost towards
the true output-error cost. Frequencies are normalised by $\omega_{\max}$ for
conditioning and the coefficients are un-normalised afterwards. Denominator is fixed by
$a_0 = 1$.

Pass `weights = 1/G_std_total**2` so that noisy *and* nonlinearly distorted lines are
trusted less — this is the whole point of doing the BLA before the fit.

Returns a dict: `b`, `a` (real, **descending** power, scipy convention), `poles`,
`zeros`, `wn` (natural frequencies in **Hz**), `zeta` (damping ratios), `G_fit` (model
sampled on `f`, for overlay), and `tf` (a `scipy.signal.TransferFunction`, or `None` if
scipy is missing).

Raises a clear error if there are fewer frequency lines than free parameters.

### `fit_tf_auto(f, G, weights=None, na_range=range(1,7), strictly_proper=True, iterations=8, criterion="aic")`

Same fit, but **the model order is not hand-picked**. Sweeps $n_a = 1\ldots6$ with
$n_b = n_a - 1$ (strictly proper), scores each with AIC (or BIC), and returns the
winner. The returned dict is the `fit_tf` dict plus `na`, `nb`, `criterion`, and
`order_scores` (the full `(na, nb, score)` list, useful to check the selection was not
a coin flip). Orders that cannot be fitted are skipped silently.

### `multisine(N, fs, excited_lines, rms=1.0, seed=None)`

Generates one period of a random-phase multisine: unit magnitude on the requested bins,
i.i.d. uniform phases, `irfft`, then scaled to the requested RMS. Use it to **design the
excitation** you will actually fly, and to reproduce a seed exactly.

### `plot_bla(res, tf_fit=None, path=None)`

The signature deliverable figure: magnitude (dB) and unwrapped phase of the BLA, with
the noise band and the single-realisation distortion band overlaid, plus the rational
fit if one is given. Frequencies where the distortion curve climbs towards the FRF are
the frequencies where "linear" is a lie.

### `demo()`

Runs when you execute `robust_BLA.py` directly. Synthetic Hammerstein system
$v = u + 0.15\,u^3$ followed by a 1 Hz second-order resonance ($\zeta = 0.08$), 8 seeds
× 6 periods, with added measurement noise. It prints the recovered resonance, DC gain,
and both dB levels, so you can verify the estimator end-to-end without any flight data.

> Note: `demo()` currently saves its figure to `/mnt/user-data/outputs/bla_demo.png`.
> Change that path before running it locally, or the save will fail.

---

## `BLA.py` — the pipeline

Run from **inside this directory** (it does a plain `import robust_BLA`). It is a
script, not a module — everything happens under `if __name__ == '__main__':`.

### Configurable constants (top of the file)

| Constant | Meaning |
|---|---|
| `YAML_PATH` | path to `config.yaml` — **must be filled in**, it ships empty |
| `STEP_AMP` | amplitude of the synthetic step, 0.1 (keep it near the excitation RMS: the BLA is only valid at the level it was measured at) |
| `STEP_TEND`, `STEP_FS`, `STEP_T0` | step simulation length, fine sample rate, and the instant the step happens |
| `STEP_LP_HZ` | low-pass cutoff applied to the step before feeding it to the model (`None` = raw step) |

The low-pass on the step is deliberate: a raw step has infinite bandwidth that is never
actually commanded to the drone, and it would excite the model far outside the band
where the BLA was identified. `STEP_LP_HZ` makes the plot show *the smoothed reference
you really send vs. how the model follows it*.

### Flow

1. **Load `config.yaml`**, fix `fs = 40` Hz (hardcoded, must match the resampling rate
   used by `validate_bag`), read the input/output column names and the optional
   `excited_lines`.
2. **Load the data.** One entry in `paths` = one **seed**; the trailing integer in the
   filename = the **period** inside that seed. Files are read as
   `f'{base}{count}{end}'` with `count = 0, 1, 2, …` until one is missing. Each period
   is mean-removed (`remove_mean`) — the BLA is a small-signal model around the
   operating point, so DC must go.
3. **Assemble** into `(M, P, N, n_channels)`, trimming to the smallest common `P` and
   `N` across seeds. Asserts `M >= 2 and P >= 2`, and warns if `M < 5` (the distortion
   band is a poor estimate with few seeds).
4. **Loop over all 9 channel pairs.** For each, run `robust_bla`, then — if at least
   `min_lines = 4` excited lines survived — fit an order-selected transfer function
   weighted by $1/\sigma^2_{\text{total}}$, and print the chosen order, the rational
   form, the resonances, and the median noise/distortion levels in dB. One
   `bla_<in>__to__<out>.png` is saved per pair. Channels with too few lines get the BLA
   plot only and no fit.
5. **Fill two grids**: `TF[k][j]` — the full 3×3 MIMO model; `TF_DIAG[k][k]` — the
   diagonal-only model (off-diagonal entries kept as `0`, which the simulator skips).
6. **Validate**, three ways (below).
7. **Export** the diagonal model with `save_model`.

### Helper functions

* **`read_parquet_safe(path)`** — returns `None` instead of raising when a file is
  missing; this is what terminates the period-counting loop.
* **`remove_mean(data)`** — subtracts the per-column mean.
* **`tf_string(b, a)`** — pretty-prints $G(s)$ as `(num) / (den)` for the console.
* **`step_matrix(TF, ...)`** — 3×3 grid of step responses. The diagonal also shows the
  filtered reference and the DC gain line ($\text{amp} \times b_{-1}/a_{-1}$); empty
  cells are labelled *"no fit"*. Saved to `step_matrix.png`.
* **`validate_response(TF, U_seed, Y_seed, fs, ..., TF_diag=None)`** — the honest test:
  simulates the identified model on **real logged commands** and overlays reference,
  measured output, full-MIMO model, and diagonal-only model, one subplot per output
  axis. Comparing the last two tells you directly whether the cross-couplings are worth
  keeping.
* **`save_model(TF_diag, ...)`** — writes the diagonal model twice: `<name>.npz`
  (arrays `b__<in>__to__<out>` / `a__<in>__to__<out>`, load with `np.load`) for code,
  and `<name>.yaml` (coefficients, DC gain, and time constant $\tau = a_0/a_1$ for
  first-order channels, plus metadata) for humans. Non-`TransferFunction` entries are
  skipped.

### Paths that must be filled before running

`BLA.py` ships with several placeholder strings. Set all of them:

| Line | Placeholder | What to put there |
|---|---|---|
| [BLA.py:11](BLA.py#L11) | `YAML_PATH = ''` | path to `config.yaml` |
| [BLA.py:301](BLA.py#L301) | `validate_response(..., "", TF_DIAG)` | output filename for the multisine validation plot |
| [BLA.py:304](BLA.py#L304) | `step_bag_path = ""` | parquet file of an **independent** step/manoeuvre log — validation on data the model never saw |
| [BLA.py:309](BLA.py#L309) | `validate_response(..., "", TF_DIAG)` | output filename for that second plot |
| [BLA.py:313-314](BLA.py#L313-L314) | `path_dir=""`, `name=""` | where to write the exported model, and its name |

---

## `config.yaml`

```yaml
paths:                        # one entry per SEED (independent phase realisation)
  exp1: '/.../bag4/processed/bag4_processed_40hz_'   # filename prefix; the period
  exp2: '/.../bag5/processed/bag4_processed_40hz_'   # index and `end` are appended
  exp3: '/.../bag6/processed/bag4_processed_40hz_'
end: '.parquet'
flu_attributes:   ["FLU_axes_0", "FLU_axes_1", "FLU_axes_2"]          # inputs  u
vl_gf_attributes: ["FLUvelocity_ground_fused_x", ..._y, ..._z]        # outputs y
motor_attributs:  ["prop_bl", "prop_br", "prop_fl", "prop_fr"]        # unused here
```

So `exp1` expects `..._40hz_0.parquet`, `..._40hz_1.parquet`, … one per period.

An optional key is read but not present in the shipped file:

```yaml
excited_lines: [3, 7, 11, ...]   # designed DFT bins; if absent they are auto-detected
```

`motor_attributs` is read by other tools in this folder tree, not by `BLA.py`.

> The current config has only **3 seeds**, which triggers the `M < 5` warning: the FRF
> itself is fine, but treat the distortion numbers as provisional.

---

## How to use

**1 — Design the excitation.** Pick the frequency band and RMS level that match how the
drone is really flown, then build the multisine:

```python
import numpy as np, robust_BLA
fs, N = 40.0, 800                       # f0 = fs/N = 0.05 Hz, period = 20 s
lines = np.arange(2, 60, 3)             # 0.1 .. 3 Hz, sparse
u = robust_BLA.multisine(N, fs, lines, rms=0.3, seed=1)
```

Fly **M ≥ 5 different seeds**, each for **P ≥ 3 periods** *after* the transient has
died out, all with the same amplitude spectrum and the same RMS.

**2 — Extract and segment.** Use [data_extractor](../data_extractor/) to get parquet,
then [validate_bag](../validate_bag/) to rotate into FLU, resample to 40 Hz, and cut the
log into exactly one period per file, numbered from 0.

**3 — Configure.** Point `config.yaml` at the seeds, fill in the placeholder paths in
`BLA.py`, and add `excited_lines` if you know them.

**4 — Run.**

```bash
cd .../best_linear_approximation
python3 BLA.py
```

Outputs: one `bla_<in>__to__<out>.png` per channel, `step_matrix.png`, the two
validation figures, the exported `.npz` + `.yaml` model, and a console report per
channel.

**5 — Read the result.** For each channel, look at the plot before the coefficients:

* Distortion band well below the FRF across your band → the linear model is trustworthy
  there; use it.
* Distortion band approaching the FRF → the linear model is fiction at those
  frequencies. Lower the excitation amplitude, narrow the band, or move to a nonlinear
  structure.
* Noise band dominating → you need more periods/seeds, not a different model.

**Always report the excitation (spectrum and RMS) alongside the model.** A BLA measured
at one amplitude is not valid at another — see §8 of [documentation.md](documentation.md).

To sanity-check the toolchain without flight data:

```bash
python3 robust_BLA.py     # runs demo(); fix the output path first
```

---

## Caveats

* **The identification is closed-loop.** The DJI flight controller sits between the
  command and the airframe, so what is identified is the *closed-loop* velocity
  response, not the bare vehicle. That is the right object for outer-loop control
  design, but the textbook BLA theory assumes open loop; the distortion band inherits
  whatever the inner loop is doing.
* **`fs = 40` is hardcoded** in `BLA.py` and must match the rate `validate_bag` produced.
* **Coherent sampling matters.** Each parquet file must contain *exactly* one period.
  A fractional period leaks energy across the DFT bins and inflates both bands.
* **The model is small-signal**, mean-removed, and its DC gain is extrapolated below the
  lowest excited line — it is not measured there.
* **The `.npz`/`.yaml` export only saves the diagonal channels.** If the validation plot
  shows that the off-diagonal terms matter, `save_model` needs extending.

## Use of generative AI
Generative AI was used to rewrite and polish the text above.