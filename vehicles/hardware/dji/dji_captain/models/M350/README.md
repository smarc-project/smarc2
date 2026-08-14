# Discrete and Continuous Models for M350

These directories contain the discrete and continuous models for the M350 obtained via system identification. The models represent the drone's dynamics and include the DJI embedded motion controller. 

## System Identification Process 

The continuous models represent the continuous transfer functions between the `M350__wrapper__psdk_ros2__flight_control_setpoint_FLUvelocity_yawrate` topic and the `M350__wrapper__psdk_ros2__acceleration_body_fused` topic. 

The models were obtained using the Best Linear Approximation (BLA) method. The inputs were multi-axis orthogonal sinusoids, and yaw rate references were set to 0 throughout the entire data collection process.

## Interval and Conditions of Validity

The models can be considered reliable under the following conditions:
* **Frequency Limit:** Valid for inputs with spectral content below 1 Hz (the highest frequency sinusoid used during data collection).
* **Decoupling:** The total transfer matrix is diagonal, meaning it is possible to control each axis independently.
* **Z-Axis Constraints:** The models accurately reflect the real drone's behavior only for small perturbations along the z-axis. It is highly likely the DJI controller changes its behavior for that phase of flight, as coupling between axes becomes apparent in the data outside of these small perturbations.

## Discrete Models 

The discrete models were obtained by the discretization of the continuous models using the Zero-Order Hold (ZOH) method sampled at 50 Hz.

## YAML File Structure and Model Parameters

The identified models are stored in a YAML format containing the parameters for each diagonal SISO (Single-Input Single-Output) channel. The channels are denoted as `Gxd`, `Gyd`, and `Gzd`, representing the discrete transfer functions for the x, y, and z axes, respectively. 

### Transfer Function Coefficients 

The core dynamics for each axis are represented as discrete-time transfer functions in the $z$-domain. The YAML file defines these functions using two main arrays:
* **`num_b`:** The coefficients of the transfer function's numerator.
* **`den_a`:** The coefficients of the transfer function's denominator.

**Coefficient Ordering (Powers of $z$):**
The lists of coefficients are organized in descending powers of $z$. This means that the first element in the array (`num_b[0]` or `den_a[0]`) always represents the coefficient associated with the highest power of $z$ in that polynomial.

For example, looking at the x-axis channel (`Gxd`):
* `num_b: [0.03685537260331673]` translates to a 0th-order numerator: $N(z) = 0.036855$
* `den_a: [1.0, -0.9662635006011508]` translates to a 1st-order denominator: $D(z) = 1.0z - 0.966263$

This results in the following discrete transfer function for the x-axis:

$$G_{xd}(z) = \frac{0.036855}{z - 0.966263}$$

### Additional Extracted Parameters

Alongside the polynomials, the YAML file logs several other physical properties extracted during the system identification:
* **`fs`:** The sampling frequency of the discrete system (50.0 Hz).
* **`dt`:** The sample time of the discrete system in seconds ($dt = 0.02$ s), which corresponds directly to the 50 Hz sampling frequency.
* **`dc_gain`:** The extrapolated steady-state gain of the system at zero frequency (DC).