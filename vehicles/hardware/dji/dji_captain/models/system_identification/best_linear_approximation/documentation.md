# The Best Linear Approximation — the maths behind the code

This document derives the theory that [robust_BLA.py](robust_BLA.py) and
[BLA.py](BLA.py) implement. Every formula is tied to the line of code that computes it.
For *how to run* the tools, see [README.md](README.md).

**Contents**

1. [Why a linear model of a nonlinear system](#1-why-a-linear-model-of-a-nonlinear-system)
2. [What PEM assumes, and where it breaks](#2-what-pem-assumes-and-where-it-breaks)
3. [Definition of the BLA](#3-definition-of-the-bla)
4. [Deriving $G_{\mathrm{BLA}} = S_{YU}/S_{UU}$](#4-deriving-g_mathrmbla--s_yus_uu)
5. [The output decomposition](#5-the-output-decomposition)
6. [Properties of the distortion $Y_S$](#6-properties-of-the-distortion-y_s)
7. [The worked example: a static cubic](#7-the-worked-example-a-static-cubic)
8. [Why the input matters](#8-why-the-input-matters)
9. [Random-phase multisines and detection lines](#9-random-phase-multisines-and-detection-lines)
10. [The robust method, estimator by estimator](#10-the-robust-method-estimator-by-estimator)
11. [From FRF to rational transfer function](#11-from-frf-to-rational-transfer-function)
12. [Order selection](#12-order-selection)
13. [Assumptions and limits](#13-assumptions-and-limits)
14. [BLA vs PEM, side by side](#14-bla-vs-pem-side-by-side)

---

## 1. Why a linear model of a nonlinear system

The M350 is nonlinear: rotor aerodynamics saturate, the flight controller has rate and
attitude limits, drag is quadratic, the slung payload swings. And yet a linear model is
what we want, because:

* a **frequency response function** $G(j\omega)$ is directly readable — bandwidth,
  resonances, phase margin;
* every practical outer-loop design (LQR, $H_\infty$, loop shaping, ZV/ZVD input
  shaping) is built on an LTI plant;
* it is cheap, interpretable, and usually good enough near an operating point.

So the useful question is not *"is the system linear?"* (it is not) but:

> **If I am going to use a linear model anyway — which linear model is the best one,
> how good is it, and how do I know when the nonlinearity is hurting me?**

The BLA answers exactly those three, in that order. That is the entire subject, and it
is why the code produces not just a `G` but two uncertainty bands next to it.

---

## 2. What PEM assumes, and where it breaks

The Prediction Error Method fits

$$
y(t) = G(q,\theta)\,u(t) + H(q,\theta)\,e(t),
$$

with $q$ the shift operator, $H$ monic/stable/inversely stable, and $e(t)$ **white** of
variance $\lambda$. It forms the one-step-ahead predictor

$$
\hat y(t\mid t-1,\theta) = H^{-1}(q,\theta)G(q,\theta)\,u(t) + \big(1 - H^{-1}(q,\theta)\big)y(t),
$$

and minimises $V_N(\theta) = \frac1N\sum_t \varepsilon^2(t,\theta)$ with
$\varepsilon = y - \hat y$.

Three assumptions are buried in that machinery:

1. the true system is in the model class (or the residual after the best linear fit is
   well behaved);
2. the residual $e(t)$ is **white**, or can be whitened by $H(q,\theta)$;
3. the residual is **independent of the input** $u$ (open loop).

For a linear plant with additive measurement noise all three hold and PEM is essentially
optimal. **For a nonlinear plant, 2 and 3 are false**, and the failure is not subtle:

> The part of the output your linear model cannot explain is *not* white and *not*
> independent of $u$ — it is a **deterministic nonlinear function of the input**. PEM
> will still converge to *some* linear model, but that model depends on the noise
> structure you assumed and on the model order you chose, and its reported variances are
> wrong, because PEM believes the leftover is white noise when it is structured,
> input-locked distortion.

The BLA framework takes that leftover seriously: it refuses to whiten it and instead
**measures** it.

---

## 3. Definition of the BLA

Let the true (possibly nonlinear) system map $u \mapsto y$. Restrict attention to a
**class of input signals** $\mathbb{U}$ — this qualifier is not optional, see §8. Over
all stable LTI models $G$, define

$$
\boxed{\;G_{\mathrm{BLA}} \;=\; \arg\min_{G \in \mathcal{G}_{\mathrm{LTI}}}\;
\mathbb{E}\Big\{\big|\,y(t) - G(q)\,u(t)\,\big|^2\Big\}\;}
\tag{3.1}
$$

where $\mathbb{E}\{\cdot\}$ is over the random realisations of the input drawn from
$\mathbb{U}$ (and over measurement noise, if present).

Three consequences, all of which show up in the code:

* **It is a projection.** $G_{\mathrm{BLA}}$ is the orthogonal projection of the output
  onto the subspace of LTI-filtered versions of the input, in the mean-square
  ($\mathcal{L}_2$) sense. Minimising a quadratic distance onto a linear subspace
  *always* gives an orthogonal projection — that geometric fact underpins everything
  below.
* **It is best in a well-defined sense**, not "whatever the optimiser returned". Two
  people who agree on the input class and the cost agree on $G_{\mathrm{BLA}}$.
* **It depends on the input class.** For a linear system the FRF is a property of the
  system alone; for a nonlinear one the BLA is a property of the **system + excitation
  pair**. This is why `multisine(...)` takes an `rms` argument and why the README insists
  you report it.

---

## 4. Deriving $G_{\mathrm{BLA}} = S_{YU}/S_{UU}$

### 4.1 Setup

Take $u$ and $y$ zero-mean and jointly wide-sense stationary, and work
frequency-by-frequency. Let $U(j\omega)$, $Y(j\omega)$ be the spectral representations.
At a single frequency an LTI model can do exactly one thing: multiply the input spectrum
by a complex number $G(j\omega)$. So (3.1) decouples across frequency into: at each
$\omega$, pick the complex scalar minimising

$$
V(\omega) = \mathbb{E}\Big\{\big|Y(j\omega) - G(j\omega)U(j\omega)\big|^2\Big\}.
\tag{4.1}
$$

The zero-mean requirement is why [BLA.py](BLA.py) calls `remove_mean` on every period
before anything else.

### 4.2 Expand

With $|z|^2 = zz^\ast$ and dropping the $(j\omega)$:

$$
|Y - GU|^2 = (Y-GU)(Y^\ast - G^\ast U^\ast)
= |Y|^2 - G^\ast YU^\ast - G\,UY^\ast + |G|^2|U|^2 .
$$

Take expectations and name the spectra
$S_{YY} = \mathbb{E}\{|Y|^2\}$, $S_{UU} = \mathbb{E}\{|U|^2\}$,
$S_{YU} = \mathbb{E}\{YU^\ast\}$, $S_{UY} = S_{YU}^\ast$:

$$
V(\omega) = S_{YY} - G^\ast S_{YU} - G\,S_{UY} + |G|^2 S_{UU}.
\tag{4.2}
$$

### 4.3 Minimise over the complex $G$

Use Wirtinger calculus: treat $G$ and $G^\ast$ as independent and set
$\partial V/\partial G^\ast = 0$. (Writing $G = a + jb$ and setting both real partials to
zero gives the same equation, two lines longer.) Term by term:

$$
\frac{\partial S_{YY}}{\partial G^\ast} = 0,\quad
\frac{\partial(-G^\ast S_{YU})}{\partial G^\ast} = -S_{YU},\quad
\frac{\partial(-G S_{UY})}{\partial G^\ast} = 0,\quad
\frac{\partial(GG^\ast S_{UU})}{\partial G^\ast} = G\,S_{UU},
$$

hence

$$
\boxed{\;G_{\mathrm{BLA}}(j\omega) = \frac{S_{YU}(j\omega)}{S_{UU}(j\omega)}\;}
\tag{4.3}
$$

Second-order check: $\partial^2 V/\partial G\,\partial G^\ast = S_{UU} > 0$, so this is
the unique minimum — as it must be, the cost being a convex quadratic in $G$.

### 4.4 What just happened

Formula (4.3) is **identical in form** to the classical H1 spectral estimator you would
use on a *linear* system. That is the punchline:

> The mechanical procedure "cross-spectrum over input auto-spectrum" does not care
> whether the system is linear. Applied to a nonlinear system it *automatically* returns
> the mean-square-optimal linear model. The formula did not change; its **interpretation**
> did. For a linear system it is *the* transfer function; for a nonlinear one it is *the
> best linear shadow* cast under this particular excitation.

### 4.5 The normal equation — and the trap

Rearranging (4.3) gives $S_{YU} = G_{\mathrm{BLA}}S_{UU}$, i.e. with the **residual**
$Y_S \equiv Y - G_{\mathrm{BLA}}U$:

$$
\boxed{\;\mathbb{E}\{Y_S\,U^\ast\} = 0\;}
\tag{4.4}
$$

The residual is **uncorrelated with the input**. Three readings of the same line:

1. *Geometrically*: $G_{\mathrm{BLA}}U$ is the orthogonal projection of $Y$ onto the
   input direction; $Y_S$ is what is left, orthogonal to $U$.
2. *Statistically*: the residual has zero linear correlation with the input.
3. *The trap*: **uncorrelated is not independent.** For a nonlinear system $Y_S$ is a
   fully deterministic function of $u$ — maximally dependent — yet its correlation with
   $u$ is exactly zero. §7 shows this in four symbols.

**PEM's optimality rests on independence; the BLA only ever claims uncorrelatedness. That
gap is the whole story.**

### 4.6 Why the code averages $\hat G$ instead of forming cross-spectra

`robust_bla` does not compute $S_{YU}/S_{UU}$ literally. It computes one FRF per seed,
$\hat G^{[m]} = \bar Y^{[m]}/\bar U^{[m]}$, and averages those
([robust_BLA.py:154](robust_BLA.py#L154), [:165](robust_BLA.py#L165)). For a random-phase
multisine the two are the same object. The input magnitude is *designed*, so
$|U(k)| = A_k$ is deterministic and identical across seeds; only the phase is random.
Then

$$
\frac{S_{YU}}{S_{UU}} = \frac{\mathbb{E}\{YU^\ast\}}{A_k^2}
= \frac{\mathbb{E}\{(G_{\mathrm{BLA}}U + Y_S)U^\ast\}}{A_k^2}
= G_{\mathrm{BLA}} + \frac{\mathbb{E}\{Y_SU^\ast\}}{A_k^2}
= G_{\mathrm{BLA}},
$$

and equally

$$
\mathbb{E}\left\{\frac{Y}{U}\right\}
= G_{\mathrm{BLA}} + \mathbb{E}\left\{\frac{Y_S}{U}\right\} = G_{\mathrm{BLA}},
$$

because $Y_S/U$ has zero mean over phase realisations (§6, property 1). The averaged-FRF
form is preferred here because it also hands you the per-seed scatter, which is exactly
what the distortion band is computed from.

---

## 5. The output decomposition

Excite a system satisfying §13 with a random-phase multisine, measure in steady state,
and DFT. At each excited line $k$:

$$
\boxed{\;Y(k) = \underbrace{G_{\mathrm{BLA}}(j\omega_k)U(k)}_{\text{best linear part}}
\;+\; \underbrace{Y_S(k)}_{\substack{\text{stochastic nonlinear}\\\text{distortion}}}
\;+\; \underbrace{N_Y(k)}_{\substack{\text{measurement}\\\text{noise}}}\;}
\tag{5.1}
$$

This is the equation quoted at the top of [robust_BLA.py](robust_BLA.py). Three terms of
completely different nature, and separating the last two is precisely what PEM cannot do:

| Term | What it is | Across **periods** | Across **phase realisations** |
|---|---|---|---|
| $G_{\mathrm{BLA}}U$ | the linear model output | identical | changes ($U$ changes), $G_{\mathrm{BLA}}$ fixed |
| $Y_S$ | nonlinear distortion | **identical** — deterministic function of a periodic input | **changes randomly**, zero mean |
| $N_Y$ | measurement noise | **changes**, zero mean | changes |

That table *is* the experiment design, and it maps one-to-one onto the data layout
`(M, P, N)`:

* **Averaging over periods $P$ kills $N_Y$ and leaves $Y_S$ untouched.**
* **Varying the phase realisation $M$ turns $Y_S$ into something with computable
  statistics.**

Two knobs, two effects. §10 turns this into the estimator.

---

## 6. Properties of the distortion $Y_S$

Under the standard assumptions (Volterra-class, PISPO system, random-phase multisine
input — §13):

**1. Zero mean over phase realisations.**

$$\mathbb{E}_\phi\{Y_S(k)\} = 0 .$$

*Intuition:* distortion products are sums of terms like $U(k_1)U(k_2)U(k_3)$ with
$k_1 + k_2 + k_3 = k$, each carrying a factor $e^{j(\phi_{k_1}+\phi_{k_2}+\phi_{k_3})}$
whose expectation vanishes. Averaging over phases averages the distortion to zero *at
each line*. **This is why the seed-average in `robust_bla` converges to the true
$G_{\mathrm{BLA}}$ and is not biased by the nonlinearity** — and why the number of seeds
$M$, not the number of periods $P$, is what buys you an unbiased FRF.

**2. Uncorrelated with the input, but not independent** — equation (4.4), and §7.3.

**3. Asymptotically circular complex normal** (as the number of excited lines grows) and
**smooth in frequency**. Line by line, the distortion looks like *coloured Gaussian noise
sitting on top of the FRF*. This is the precise sense in which "nonlinear distortion
masquerades as noise" — and the reason a whiteness test on PEM residuals can pass while
the model is nonsense.

**4. Its variance $\sigma^2_{Y_S}(k)$ is smooth in frequency and grows with input
amplitude faster than the linear term.** The ratio

$$
\frac{\sigma_{Y_S}(k)}{\big|G_{\mathrm{BLA}}(j\omega_k)U(k)\big|}
$$

is the **local nonlinearity meter**. That is exactly what `BLAResult.dist_to_signal_db`
reports ([robust_BLA.py:52-54](robust_BLA.py#L52-L54)): small ⇒ the system is effectively
linear at $\omega_k$ under this excitation; large ⇒ your linear model is fiction there.

> Compare with PEM once more: PEM lumps $Y_S + N_Y$ into one innovation and tries to
> whiten it with $H(q,\theta)$. But $Y_S$ is not stochastic in the period-to-period sense
> at all — it is repeatable, input-locked structure. Whitening it is a category error.

---

## 7. The worked example: a static cubic

Everything above becomes concrete on the simplest nonlinear system. This is also the
system `demo()` uses ([robust_BLA.py:401](robust_BLA.py#L401)), wrapped in a resonance.

### 7.1 The tool: Stein / Bussgang

Let $y = f(u) = u^3$ with $u \sim \mathcal{N}(0, \sigma_u^2)$.

**Stein's lemma.** If $u \sim \mathcal{N}(0,\sigma_u^2)$ and $f$ is differentiable with
$\mathbb{E}|f'(u)| < \infty$, then $\mathbb{E}\{u f(u)\} = \sigma_u^2\,\mathbb{E}\{f'(u)\}$.

*Proof.* The density $p(u) = \frac{1}{\sqrt{2\pi}\sigma_u}e^{-u^2/2\sigma_u^2}$ satisfies
$p'(u) = -\frac{u}{\sigma_u^2}p(u)$, so $u\,p(u) = -\sigma_u^2 p'(u)$. Then

$$
\mathbb{E}\{uf(u)\} = \int u f(u)p(u)\,du = -\sigma_u^2\int f(u)p'(u)\,du
\overset{\text{parts}}{=} \sigma_u^2 \int f'(u)p(u)\,du = \sigma_u^2\mathbb{E}\{f'(u)\},
$$

the boundary term $[-\sigma_u^2 f(u)p(u)]_{-\infty}^{\infty}$ vanishing because the
Gaussian tail kills any polynomially-growing $f$. $\blacksquare$

### 7.2 The BLA gain

Static system ⇒ no dynamics ⇒ $G_{\mathrm{BLA}}$ collapses to a real gain
$\alpha = \mathbb{E}\{yu\}/\mathbb{E}\{u^2\}$. With $f' = 3u^2$:

$$
\alpha = \frac{\sigma_u^2\,\mathbb{E}\{3u^2\}}{\sigma_u^2} = 3\sigma_u^2 .
$$

Brute-force check with $\mathbb{E}\{u^4\} = 3\sigma_u^4$:
$\alpha = 3\sigma_u^4/\sigma_u^2 = 3\sigma_u^2$. ✓

**Read this.** The best linear approximation of $y = u^3$ is $\alpha = 3\sigma_u^2$ — it
is **not a fixed property of the cubic**, it scales with the input variance. Drive harder
and the best linear gain grows. A linear FRF could never do this; the BLA does because it
is a property of the *system + excitation* pair. This is why `STEP_AMP = 0.1` in
[BLA.py](BLA.py) is deliberately kept near the excitation RMS: simulating a big step
through a small-signal BLA is asking the model a question it was never measured to answer.

### 7.3 The distortion: orthogonal yet dependent

$$
y_S = y - \alpha u = u^3 - 3\sigma_u^2 u,
$$

$$
\mathbb{E}\{y_S u\} = \mathbb{E}\{u^4\} - 3\sigma_u^2\mathbb{E}\{u^2\}
= 3\sigma_u^4 - 3\sigma_u^4 = 0 . \;\checkmark
$$

So $y_S$ is *exactly* uncorrelated with $u$ — and it is also a *deterministic function of
$u$*, the most dependent thing imaginable. **Here, in four symbols, is the gap PEM falls
into and the BLA respects.** Hand $\{u, y_S\}$ to a linear correlation test and it reports
"residual uncorrelated with input, model looks fine", while the residual is a pure,
perfectly repeatable nonlinearity.

### 7.4 The Hermite view — why $3\sigma_u^2 u$ specifically

$u^3 - 3\sigma_u^2 u$ is the scaled third probabilists' Hermite polynomial,
$\sigma_u^3 He_3(u/\sigma_u)$ with $He_3(x) = x^3 - 3x$. Hermite polynomials are
orthogonal under the Gaussian measure,
$\mathbb{E}\{He_m(u/\sigma_u)He_n(u/\sigma_u)\} = 0$ for $m \neq n$. Decomposing:

$$
u^3 = \underbrace{3\sigma_u^2\,\sigma_u He_1(u/\sigma_u)}_{\text{linear = BLA}}
\;+\; \underbrace{\sigma_u^3 He_3(u/\sigma_u)}_{\text{distortion} = y_S}.
$$

> **The BLA is literally the projection of the nonlinear map onto the degree-1 Hermite
> component, and $Y_S$ is everything orthogonal to it in the Gaussian inner product.**
> Exact for Gaussian excitation; asymptotic for random-phase multisines (Riemann
> equivalence, §8). This is the deep reason the BLA is unique and why the distortion is
> automatically orthogonal to the input.

§§7.2–7.4 are the entire theory on one page. Everything else is *dynamics* (letting $G$
be a filter instead of a gain), *estimation* (§10), and *bookkeeping* (§9).

---

## 8. Why the input matters

For a linear system the FRF is input-independent — chirp, noise, or steps all recover the
same $G(j\omega)$. **For a nonlinear system this is false, and assuming otherwise is the
classic beginner error.** The BLA depends on the input class through:

* **The power spectrum $S_{UU}(\omega)$** — which bands you excite, with what relative
  power. Distortion products from one band land in others, so the shape of $S_{UU}$
  reshapes $G_{\mathrm{BLA}}$.
* **The RMS / amplitude** — §7.2's $\alpha = 3\sigma_u^2$ in one line. Cranking the level
  changes the best linear gain and, in general, the shape of the FRF.
* **The amplitude distribution** (Gaussian, uniform, binary) — to second order in the
  nonlinearity this matters only weakly, which motivates §8.2.

### 8.1 Random-phase multisines

A random-phase multisine is periodic and built from a chosen harmonic set:

$$
u(t) = \sum_{k \in \mathcal{K}} A_k \cos(2\pi k f_0 t + \phi_k),
\tag{8.1}
$$

with $f_0 = f_s/N$ the frequency resolution, $\mathcal{K}$ the **excited lines**,
$A_k \geq 0$ the **amplitude spectrum** ($\to S_{UU}$), and phases i.i.d. uniform on
$[0,2\pi)$, so that

$$
\mathbb{E}\{e^{j\phi_k}\} = \frac{1}{2\pi}\int_0^{2\pi} e^{j\phi}\,d\phi = 0 .
\tag{8.2}
$$

Property (8.2) is what makes the phase-averaging of §6 work. This is exactly what
`multisine()` builds ([robust_BLA.py:341-357](robust_BLA.py#L341-L357)): unit magnitude on
`excited_lines`, `rng.uniform(0, 2*pi)` phases, `irfft`, rescale to the target RMS.

Multisines are the workhorse because they are:

* **Periodic** ⇒ the steady-state response is periodic ⇒ the DFT lands *exactly* on the
  excited lines with **no leakage**. This is why the pipeline insists that each parquet
  file hold exactly one period: a fractional period reintroduces leakage and inflates both
  bands.
* **Deterministic in amplitude, random only in phase** ⇒ you control $S_{UU}$ and the RMS
  exactly, and can repeat the identical signal for several periods to average noise.
* **Sparse in frequency** ⇒ you can leave lines unexcited on purpose and watch what the
  nonlinearity dumps into them (§9). Gaussian noise cannot do this — it fills every line,
  so distortion and excitation overlap everywhere and become inseparable.

### 8.2 Riemann equivalence

**Definition (informal).** Two signal classes are **Riemann equivalent** if their
amplitude spectra converge to the same power spectral density as $N \to \infty$ — as the
line spacing $f_0 \to 0$ the discrete lines "Riemann-sum" to the same continuous
$S_{UU}(\omega)$.

**Theorem (Pintelon–Schoukens).** For PISPO nonlinear systems, all inputs in the same
Riemann-equivalent class with the same amplitude distribution yield the **same BLA up to
an $O(1/N)$ term**. In particular a random-phase multisine and filtered Gaussian noise
with the same $S_{UU}$ give asymptotically the same $G_{\mathrm{BLA}}$.

The payoff is large: you design a clean, periodic, leakage-free, repeatable multisine, and
you *know* it estimates the same BLA the drone would exhibit under realistic Gaussian-ish
operational excitation. You keep physical relevance and experimental convenience at once.

> **The reporting rule.** A BLA is always reported *together with its excitation*:
> $S_{UU}(\omega)$ and the RMS level. "The BLA of the system" is an incomplete statement;
> "the BLA of the system under this multisine at this RMS" is complete. This has no
> analogue in linear identification and is the most commonly forgotten point.

---

## 9. Random-phase multisines and detection lines

Multisines let you *see where the nonlinearity lives in frequency*, essentially for free.
The mechanism is frequency bookkeeping.

### 9.1 Which nonlinearities land where

A **quadratic** nonlinearity produces output at $\omega_{k_1} \pm \omega_{k_2}$; a
**cubic** at $\omega_{k_1} \pm \omega_{k_2} \pm \omega_{k_3}$; and so on. Track the parity
of the resulting line index:

* **Even-degree** nonlinearities (2nd, 4th, …) combine an even number of lines → land on
  **even** indices (and DC);
* **Odd-degree** nonlinearities (3rd, 5th, …) → land on **odd** indices.

### 9.2 Odd multisines

Excite only odd lines, $\mathcal{K} = \{1,3,5,\dots\}$. Then even non-excited lines carry
*only even* distortion, and odd non-excited lines carry *odd* distortion — each measurable
directly, with nothing else on top.

### 9.3 Detection lines

Take the odd lines and **randomly omit a few**: in each group of consecutive odd lines,
skip one at random. Those skipped lines are **detection lines**. At a detection line there
is no excitation and no linear response (a linear system responds only where excited), so
whatever appears is **odd nonlinear distortion + measurement noise**. Comparing detection-
line level to excited-line level gives an immediate, model-free readout: *"odd nonlinear
distortion is X dB below the linear response across this band."* PEM produces nothing of
the sort.

**Design tension:** omitting lines slightly perturbs $S_{UU}$, and you want enough
detection lines for good statistics but not so many that you distort the excitation.
Random omission within logarithmically or linearly spaced groups is the usual compromise.

### 9.4 Where this sits in the code

The robust method in [robust_BLA.py](robust_BLA.py) does **not** need detection lines — it
gets its distortion statistics from the $M$ seeds instead. Detection lines belong to the
*fast method* (one realisation, distortion read off the unexcited lines and interpolated
onto the excited ones), which is **not implemented here**. If you fly an odd multisine
with detection lines anyway, pass the excited set explicitly through `excited_lines` in
`config.yaml` so the auto-detector does not accidentally include a detection line, and you
retain the option of a single-experiment cross-check.

---

## 10. The robust method, estimator by estimator

This section is [robust_BLA.robust_bla](robust_BLA.py#L91) line by line.

### 10.1 Experiment structure

* $M$ = number of **independent random-phase realisations** (seeds), typically 5–20;
  different $\phi_k$ draws, *same* amplitude spectrum $A_k$. In `config.yaml`, one entry
  under `paths` = one seed.
* $P$ = number of **periods** per seed, typically 2–8, all in steady state (transient
  periods discarded beforehand). The trailing file index = the period.

Index a measured output DFT by $Y^{[m,p]}(k)$, with input $U^{[m]}(k)$ — identical across
periods of a seed, since it is the same periodic signal. Hence `_as_MPN` accepts $(N,)$ or
$(M,N)$ inputs and broadcasts them: if you pass the *commanded* multisine, the input-noise
terms vanish automatically because the scatter across $p$ is exactly zero.

### 10.2 Step 1 — average over periods, kill the noise

Within seed $m$, the linear part and $Y_S^{[m]}(k)$ are identical every period, while
$N_Y^{[m,p]}(k)$ is fresh each period with zero mean. So averaging over $p$ attacks only
the noise:

$$
\hat Y^{[m]}(k) = \frac1P \sum_{p=1}^{P} Y^{[m,p]}(k).
\tag{10.1}
$$

Its noise variance is reduced by $P$, and the period-to-period scatter *estimates the
noise level itself* — the sample variance **of the mean**:

$$
\hat\sigma^2_{Y,n}{}^{[m]}(k) = \frac{1}{P(P-1)}\sum_{p=1}^{P}\big|Y^{[m,p]}(k) - \hat Y^{[m]}(k)\big|^2 .
\tag{10.2}
$$

*Why $P(P-1)$ and not $P$?* Because $\frac{1}{P-1}\sum_p|\cdot|^2$ is the unbiased estimate
of the **per-period** variance, and dividing by a further $P$ converts it to the variance
of the **average** — the standard error of a sample mean. This is `var_of_mean`
([robust_BLA.py:145-146](robust_BLA.py#L145-L146)), applied to both $Y$ and $U$; the
input–output noise covariance

$$
\hat\sigma^2_{YU,n}{}^{[m]}(k) = \frac{1}{P(P-1)}\sum_p \big(Y^{[m,p]} - \hat Y^{[m]}\big)\big(U^{[m,p]} - \hat U^{[m]}\big)^\ast
$$

is computed alongside ([robust_BLA.py:150-151](robust_BLA.py#L150-L151)) — it matters here
because the drone's *measured* command is itself a noisy signal, correlated with the
output noise through the logging chain.

> The DFT is `np.fft.rfft` with **no** $1/N$ normalisation. That is fine: the factor
> cancels in the ratio $\hat Y/\hat U$ and in every variance ratio below.

### 10.3 Step 2 — one FRF per seed

$$
\hat G^{[m]}(k) = \frac{\hat Y^{[m]}(k)}{\hat U^{[m]}(k)}.
\tag{10.3}
$$

Each $\hat G^{[m]}$ estimates $G_{\mathrm{BLA}}(j\omega_k) + Y_S^{[m]}(k)/U^{[m]}(k)$ —
the true BLA *plus* the distortion contribution of this particular phase realisation. That
extra term differs for each $m$ and has zero mean over $m$ (§6, property 1).

Propagating (10.2) through the division, to first order:

$$
\frac{\hat\sigma^2_{\hat G,n}}{|\hat G|^2}
\approx \frac{\hat\sigma^2_{Y,n}}{|\hat Y|^2}
+ \frac{\hat\sigma^2_{U,n}}{|\hat U|^2}
- 2\,\mathrm{Re}\!\left(\frac{\hat\sigma^2_{YU,n}}{\hat Y\,\hat U^\ast}\right),
\tag{10.4}
$$

which is [robust_BLA.py:157-161](robust_BLA.py#L157-L161) verbatim. The result is clipped
at zero, because a first-order propagation with finite-sample variances can go slightly
negative. If the input is noise-free (commanded multisine passed in), the second and third
terms vanish on their own.

### 10.4 Step 3 — average over seeds → the BLA

$$
\boxed{\;\hat G_{\mathrm{BLA}}(k) = \frac1M \sum_{m=1}^{M}\hat G^{[m]}(k)\;}
\tag{10.5}
$$

Because the distortion has zero mean over realisations, this converges to the true
$G_{\mathrm{BLA}}(j\omega_k)$ as $M \to \infty$, with bias only $O(1/N)$ from the multisine
approximation. **This is the curve plotted as the FRF and handed to the rational fit.**

### 10.5 Step 4 — split noise from distortion

Total sample variance of the estimate across seeds (again a variance of the mean):

$$
\hat\sigma^2_{\hat G_{\mathrm{BLA}}}(k) = \frac{1}{M(M-1)}\sum_{m=1}^{M}\big|\hat G^{[m]}(k) - \hat G_{\mathrm{BLA}}(k)\big|^2 .
\tag{10.6}
$$

This spread comes from **two** sources: measurement noise, and the realisation-varying
nonlinear distortion. We already have an independent handle on the noise part. Since
$\hat G_{\mathrm{BLA}}$ is a $1/M$-weighted sum of independent per-seed estimates, the
noise contribution to its variance is

$$
\hat\sigma^2_{\hat G_{\mathrm{BLA}},n}(k) = \frac{1}{M^2}\sum_{m=1}^{M}\hat\sigma^2_{\hat G^{[m]},n}(k),
\tag{10.7}
$$

which is [robust_BLA.py:171](robust_BLA.py#L171). Now **subtract**:

$$
\boxed{\;\hat\sigma^2_{\hat G_{\mathrm{BLA}},\mathrm{NL}}(k)
= \hat\sigma^2_{\hat G_{\mathrm{BLA}}}(k) - \hat\sigma^2_{\hat G_{\mathrm{BLA}},n}(k)\;}
\tag{10.8}
$$

clipped at zero ([robust_BLA.py:174](robust_BLA.py#L174)) — for an essentially linear
channel the two terms are equal up to sampling error and the difference can come out
negative.

The two results mean different things:

* $\hat\sigma^2_{\hat G_{\mathrm{BLA}},n}$ — how much of the FRF uncertainty is
  **measurement noise**. Falls as $1/(MP)$; beat it down with more data.
* $\hat\sigma^2_{\hat G_{\mathrm{BLA}},\mathrm{NL}}$ — how much is **nonlinear
  distortion**. As an error *on the mean* it falls as $1/M$, but its *underlying level* is
  a property of the system + excitation and **does not vanish with more averaging**. It
  tells you the system is nonlinear, full stop.

### 10.6 Why `G_std_nl_single = sqrt(M) * G_std_nl`

This distinction is important enough that the code carries both numbers. The distortion
seen on the *average of $M$ seeds* has variance $\sigma^2_{\mathrm{NL}}/M$ where
$\sigma^2_{\mathrm{NL}}$ is the level on a *single* realisation. Equation (10.8) estimates
the former, so

$$
\hat\sigma_{\mathrm{NL,single}}(k) = \sqrt{M}\;\hat\sigma_{\hat G_{\mathrm{BLA}},\mathrm{NL}}(k),
$$

which is [robust_BLA.py:182](robust_BLA.py#L182). **Use `G_std_nl_single` (and hence
`dist_to_signal_db`) to judge the nonlinearity**, because it does not shrink when you fly
more seeds; use `G_std_nl` when you want an error bar on the FRF you just estimated. A
plot that used the shrinking one would suggest, falsely, that flying longer makes the
drone more linear.

### 10.7 What to look at

`plot_bla` draws the BLA magnitude, the noise band, and the single-realisation distortion
band together. In one glance you see *the best linear model, how repeatable it is against
noise, and how badly the nonlinearity contaminates it, frequency by frequency.* No PEM
output gives you this decomposition. Where the distortion band rises towards the FRF,
"linear" is a lie at that frequency — restrict the amplitude or the band, or graduate to a
nonlinear structure.

---

## 11. From FRF to rational transfer function

$\hat G_{\mathrm{BLA}}(k)$ is a table of complex numbers. Control design wants
$G(s) = B(s)/A(s)$. This is [fit_tf](robust_BLA.py#L197).

### 11.1 The weighted frequency-domain cost

The target is

$$
\hat\theta = \arg\min_\theta \sum_k
\frac{\big|\hat G_{\mathrm{BLA}}(k) - G(j\omega_k,\theta)\big|^2}{\hat\sigma^2_G(k)},
\qquad
\hat\sigma^2_G(k) = \hat\sigma^2_{\hat G_{\mathrm{BLA}},n}(k) + \hat\sigma^2_{\hat G_{\mathrm{BLA}},\mathrm{NL}}(k),
\tag{11.1}
$$

which is **frequency-domain PEM / maximum likelihood**. In the code the weight is
`w = 1.0 / (res.G_std_total**2 + 1e-18)` ([BLA.py:277](BLA.py#L277)) — and `G_std_total`
*is* $\sqrt{\hat\sigma^2_n + \hat\sigma^2_{\mathrm{NL}}}$, since (10.6) is the total
scatter by construction.

**So BLA and PEM are not rivals at this stage.** The BLA is the honest front-end that
tells PEM the correct weighting. Because the weight includes the nonlinear distortion, the
parametric fit **automatically down-weights the frequencies where the nonlinearity makes
the linear model untrustworthy**, and the resulting parameter covariance is *correct* —
unlike naive time-domain PEM, which trusted the distortion as if it were signal.

> Punchline: **you do not throw PEM away, you upgrade its inputs.** The BLA replaces PEM's
> false "the leftover is white noise" assumption with a *measured* distortion model, then
> hands PEM a properly weighted, properly uncertain FRF to fit.

### 11.2 Equation error and the parameterisation

(11.1) is nonlinear in $\theta$ because $\theta$ sits in the denominator. The classical
trick is to multiply through by $A$: define the **equation error**

$$
\epsilon_{\mathrm{eq}}(k) = B(s_k) - \hat G(k)\,A(s_k), \qquad s_k = j\omega_k,
\tag{11.2}
$$

which is *linear* in the coefficients and solvable by ordinary least squares. Writing
$A(s) = \sum_{i=0}^{n_a} a_i s^i$ and $B(s) = \sum_{i=0}^{n_b} b_i s^i$, and fixing the
scale by $a_0 = 1$ (otherwise $\theta = 0$ wins trivially), the residual becomes

$$
\epsilon_{\mathrm{eq}}(k) = \sum_{i=0}^{n_b} b_i s_k^i \;-\; \hat G(k)\sum_{i=1}^{n_a} a_i s_k^i \;-\; \hat G(k).
$$

That is exactly the regressor matrix built at
[robust_BLA.py:237-240](robust_BLA.py#L237-L240):

$$
\Phi = \big[\, \hat s^0 \;\cdots\; \hat s^{n_b} \;\big|\; -\hat G\hat s^1 \;\cdots\; -\hat G\hat s^{n_a} \,\big],
\qquad \text{rhs} = \hat G,
$$

so that $\Phi\theta - \hat G = \epsilon_{\mathrm{eq}}$.

### 11.3 Sanathanan–Koerner reweighting

Equation error is not what we want: minimising $|B - \hat G A|^2$ biases the fit towards
frequencies where $|A|$ is large. The relation to the true output error is

$$
\hat G - \frac{B}{A} = \frac{\hat G A - B}{A} = \frac{-\epsilon_{\mathrm{eq}}}{A},
$$

so dividing the equation error by $|A|$ recovers the output error. $A$ is unknown, so
iterate: at iteration $i$, weight each row by $1/|A^{(i-1)}(s_k)|$ using the denominator
from the previous solve, starting from $A^{(0)} = 1$. This is the **Sanathanan–Koerner
iteration** ([robust_BLA.py:242-249](robust_BLA.py#L242-L249)), run 8 times by default; on
convergence the equation-error solution coincides with the output-error one.

The BLA weight enters the same row scaling. Note that `fit_tf` takes
$\sqrt{w}$ ([robust_BLA.py:230](robust_BLA.py#L230)) before multiplying the rows, because
least squares squares them — so the effective cost is $\sum_k w_k |\cdot|^2$ with $w_k$ as
given in (11.1). The combined row weight is therefore

$$
\text{row}_k \;\propto\; \frac{\sqrt{w_k}}{\big|A^{(i-1)}(s_k)\big|}.
$$

### 11.4 Frequency normalisation

Raw $s^i = (j\omega)^i$ spans many decades and wrecks the conditioning of $\Phi$. The code
solves in a normalised variable

$$
\hat s = \frac{j\omega}{c}, \qquad c = \omega_{\max},
$$

so all powers stay $O(1)$. Since $\hat s^i = s^i/c^i$, the coefficient of $s^i$ is
recovered by dividing the fitted coefficient of $\hat s^i$ by $c^i$
([robust_BLA.py:255-256](robust_BLA.py#L255-L256)). Coefficients are then reversed to the
**descending** order scipy expects.

### 11.5 What comes out

* `poles = np.roots(a)`, `zeros = np.roots(b)`;
* $\omega_n = |p|/2\pi$ in **Hz** and $\zeta = -\mathrm{Re}(p)/|p|$ per pole
  ([robust_BLA.py:264-265](robust_BLA.py#L264-L265)) — the standard second-order
  identities, since for $s^2 + 2\zeta\omega_n s + \omega_n^2$ the poles satisfy
  $|p| = \omega_n$ and $\mathrm{Re}(p) = -\zeta\omega_n$. A positive $\zeta$ means a stable
  pole; a negative one is a red flag that the fit went unstable.
* `G_fit` = the model evaluated on the same lines, for overlay;
* `tf` = `scipy.signal.TransferFunction(b, a)`, which the pipeline simulates with `lsim`.

Two derived quantities used downstream in [BLA.py](BLA.py):

$$
\text{DC gain} = G(0) = \frac{b_{-1}}{a_{-1}}, \qquad
\tau = \frac{a_0}{a_1} \;\;\text{(first order only: } G(s) = \tfrac{b_0}{a_1 s + a_0}\text{)} .
$$

In descending storage those are `b[-1]/a[-1]` and `a[0]/a[1]`. **The DC gain is an
extrapolation**: nothing was measured below the lowest excited line, so if you care about
steady-state gain, excite low enough that $f_{\min}$ is genuinely below the bandwidth of
interest.

---

## 12. Order selection

Hand-picking $n_a$ is guesswork, and raising the order stops helping the moment the model
starts fitting the noise and the nonlinear distortion rather than the FRF.
[fit_tf_auto](robust_BLA.py#L282) sweeps $n_a \in \{1,\dots,6\}$ with $n_b = n_a - 1$
(strictly proper — the physical velocity response has no direct feedthrough) and scores
each by an information criterion:

$$
\mathrm{RSS} = \sum_k w_k\big|\hat G(k) - G(j\omega_k,\hat\theta)\big|^2, \qquad
k_{\text{par}} = n_a + n_b + 1, \qquad n = |\mathcal{K}|,
$$

$$
\mathrm{AIC} = n\log\!\frac{\mathrm{RSS}}{n} + 2k_{\text{par}},
\qquad
\mathrm{BIC} = n\log\!\frac{\mathrm{RSS}}{n} + k_{\text{par}}\log n .
$$

The first term rewards fit, the second penalises complexity; BIC penalises harder and is
the safer choice when you have few excited lines. Orders needing more parameters than you
have data points are skipped ([robust_BLA.py:313](robust_BLA.py#L313)), and the full
`order_scores` list is returned so you can check whether the winner won clearly or by a
hair.

The weight $w_k$ inside the RSS is the same BLA-derived weight as in (11.1), so the order
selection is also distortion-aware: a resonance that is visible only in badly distorted
lines does not get to buy itself two extra poles.

---

## 13. Assumptions and limits

BLA theory is clean *because* it restricts the system class. Know the boundaries.

### 13.1 PISPO — "Period In, Same Period Out"

A nonlinear system is **PISPO** if, driven by a periodic input, its steady-state output is
periodic **with the same period**. This is the core structural assumption: it guarantees
the output DFT lands on the same frequency grid as the input, which everything in §§5–10
relies on.

PISPO holds for a large useful class — static nonlinearities, Wiener / Hammerstein /
Wiener–Hammerstein systems, saturations, dead-zones, smooth nonlinear dynamics, and many
hysteretic systems. It is **violated** by anything that creates new periods or
non-periodic steady states:

* **subharmonic generation** (output at $f_0/2$),
* **chaotic** dynamics,
* **quasi-periodic / limit-cycle** behaviour at incommensurate frequencies,
* **bifurcations** within the excitation range.

On a multirotor the realistic risks are rotor-speed limit cycles and payload pendulum
modes locking onto a subharmonic. A quick check: with the drone's own period-averaged
spectrum in hand, look for energy at non-integer multiples of $f_0$.

### 13.2 Volterra class / fading memory

The existence of $G_{\mathrm{BLA}}$ and the CLT-style properties of $Y_S$ (§6) assume the
system admits a convergent **Volterra series** — equivalently, that it has *fading memory*
(the far past matters exponentially less). This excludes infinite-memory or non-fading
effects. Most physical plants near an operating point are fine.

### 13.3 Excitation and stationarity

* Input is a **random-phase multisine** (or a Riemann-equivalent random signal), with the
  phase condition (8.2).
* The system must be at **steady state** when you measure — discard transient periods.
  Leftover transients corrupt the FRF like an extra coloured "noise", and the robust
  method will misattribute them: a transient is *not* identical every period, so it leaks
  into the **noise** band, not the distortion band.
* **Open loop** for the basic theory. **This is where the M350 application departs from
  the textbook**: the DJI flight controller sits inside the loop, so the input is
  correlated with the disturbance. What is identified is the closed-loop velocity
  response — the right object for outer-loop design, but the guarantees on the distortion
  band are weaker than the theory promises. Closed-loop BLA exists and needs the usual
  instrumental-variable / errors-in-variables care.

### 13.4 What the BLA does *not* give you

* **It is not a nonlinear model.** It is the best *linear shadow*. If the distortion band
  is large everywhere, the message is "stop using a linear model here" — move to a
  nonlinear structure (Volterra, block-oriented Wiener/Hammerstein, NARX, nonlinear
  state-space). The BLA is often the *first stage* of exactly such an identification: it
  gives you the linear dynamics to hang the nonlinearity on.
* **It is excitation-specific** (§8): valid for the input class you used, not universally.

---

## 14. BLA vs PEM, side by side

| Aspect | **PEM** | **BLA** |
|---|---|---|
| **Object estimated** | parametric $G(q,\theta)$ + noise model $H(q,\theta)$ | non-parametric $G_{\mathrm{BLA}}(j\omega)$ first; parametric fit optional afterwards (§11) |
| **Model of the leftover** | white innovations $e(t)$, whitened by $H$, assumed **independent** of $u$ | two explicit terms, noise $N_Y$ **and** distortion $Y_S$; only claims **uncorrelated** with $u$ (§4.5, §7.3) |
| **On nonlinear systems** | converges to *a* linear model depending on the chosen $H$, the order, and how the distortion happens to correlate; **variance estimates biased** | converges to the well-defined MSE-optimal $G_{\mathrm{BLA}}$; distortion is measured, not mismodelled |
| **Quantifies nonlinearity?** | no native mechanism — at best a failed whiteness test, with no localisation | **yes** — level *and frequency location*, with bands (§9, §10.5) |
| **Input dependence** | implicitly assumes LTI, hence input-independent | **explicit**: a system+excitation property; you must report $S_{UU}$ and RMS (§8) |
| **Uncertainty bounds** | trustworthy *iff* the residual is truly white and independent — false for nonlinear systems | noise band and distortion band separated; both meaningful (§10.5) |
| **Excitation** | any persistently exciting input | random-phase multisines: leakage-free, repeatable, sparse — this is what enables the whole distortion analysis |
| **Right tool when** | truly linear plant + additive coloured measurement noise | nonlinear (or unknown-linearity) plant where you still want a linear model **and** an honesty check on it |

### 14.1 Why the BLA is "better" here, stated precisely

It is *not* that the BLA finds a more accurate linear model by magic — under matched
conditions $\hat G_{\mathrm{BLA}}$ and a well-tuned frequency-domain PEM fit can land in
the same place (§11 explains why: you *feed* the BLA to PEM). The superiority is
**epistemic and diagnostic**:

1. **Correct treatment of the leftover.** PEM's optimality theory assumes the residual is
   white and input-independent. For a nonlinear system the residual is $Y_S$: repeatable,
   coloured, input-locked. PEM's uncertainty results are therefore wrong in a way PEM
   cannot detect from inside its own assumptions.
2. **Quantification and localisation.** The BLA hands you the distortion level as a number,
   per frequency, with bands. You learn *"my linear model is trustworthy below 1 Hz and
   garbage near the payload sway mode"* — directly actionable when deciding where ZV/ZVD
   input shaping suffices and where you need something better.
3. **A well-defined target.** "The BLA under this excitation" is unambiguous. "The linear
   model PEM returns" depends on $H$, the order, and the initialisation whenever the truth
   is nonlinear.
4. **Input honesty.** The BLA forces you to acknowledge the excitation dependence that
   PEM's LTI framing hides — the fact that bites when a controller tuned at one amplitude
   misbehaves at another.

> Blunt version: **PEM answers "what linear model best predicts these data, assuming the
> leftover is white noise?" The BLA answers "what is the best linear model, how much of
> what's left is genuine noise versus nonlinearity, and where does the nonlinearity
> hurt?"** For a nonlinear plant, the second question is the one you actually needed
> answered.

---

## 15. Summary — the sixty-second version

* The **BLA** is the mean-square-optimal LTI model of a nonlinear system **for a given
  input class**: $G_{\mathrm{BLA}} = S_{YU}/S_{UU}$ — the same formula as linear spectral
  ID, with a new meaning (§4).
* It is a **projection**: the residual $Y_S$ is **uncorrelated with the input but not
  independent of it** — the exact gap PEM ignores (§4.5, §7.3).
* The output splits as $Y = G_{\mathrm{BLA}}U + Y_S + N_Y$. **Averaging over periods
  removes noise; varying the phase realisation characterises the distortion** (§5) —
  which is exactly the `(M, P, N)` data layout.
* **Nonlinear distortion masquerades as coloured, input-locked noise.** The BLA measures
  it; PEM mis-whitens it (§6, §14).
* The BLA **depends on input amplitude and spectrum** — always report the excitation (§8).
  The cubic example, $\alpha = 3\sigma_u^2$, shows this in one line (§7).
* **Odd multisines with detection lines** locate odd/even distortion for free (§9), though
  the robust method implemented here uses seeds instead.
* The **robust method** ($M$ realisations × $P$ periods) cleanly separates the noise band
  from the distortion band (§10).
* Assumptions: **PISPO + Volterra/fading memory + steady-state periodic excitation**, and
  nominally open loop — the M350 identification is closed-loop (§13).
* The BLA does not replace PEM; it **feeds PEM the right weights** for the final parametric
  fit, giving correct, distortion-aware uncertainties (§11).

---

## References

* R. Pintelon & J. Schoukens, *System Identification: A Frequency Domain Approach*, 2nd
  ed. — the definitive reference; chapters on the BLA, nonlinear distortions, and
  multisine design.
* J. Schoukens, R. Pintelon, Y. Rolain, *Mastering System Identification in 100 Exercises*
  — hands-on multisine/BLA problems.
* J. Schoukens & L. Ljung, "Nonlinear System Identification: A User-Oriented Roadmap",
  *IEEE Control Systems Magazine*, 2019 — situates the BLA among nonlinear ID methods and
  links it back to PEM.
* C. K. Sanathanan & J. Koerner, "Transfer function synthesis as a ratio of two complex
  polynomials", *IEEE TAC*, 1963 — the reweighting used in §11.3.
* Search terms for the estimator details: *robust method BLA*, *fast method BLA detection
  lines*, *random-phase multisine*, *Riemann equivalence class*, *stochastic nonlinear
  distortion*.


## Use of generative AI
Generative AI was used to write this file by synthesizing sections from the papers and books listed above, and the final report was manually reviewed. This document is intended as an introductory overview of the method, all information should be verified against the cited literature.