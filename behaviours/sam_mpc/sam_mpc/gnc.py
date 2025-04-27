#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNC functions. 

Reference: T. I. Fossen (2021). Handbook of Marine Craft Hydrodynamics and
Motion Control. 2nd. Edition, Wiley. 
URL: www.fossen.biz/wiley

Author:     Thor I. Fossen
Modified by:   Omid Mirzaeedodangeh
"""

import numpy as np
import math
from sympy import symbols, lambdify
from scipy.interpolate import PchipInterpolator, CubicSpline, interp1d
from scipy.spatial.transform import Rotation as R

#------------------------------------------------------------------------------

def ssa(angle):
    """
    angle = ssa(angle) returns the smallest-signed angle in [ -pi, pi )
    """
    angle = (angle + math.pi) % (2 * math.pi) - math.pi
        
    return angle 

#------------------------------------------------------------------------------

def sat(x, x_min, x_max):
    """
    x = sat(x,x_min,x_max) saturates a signal x such that x_min <= x <= x_max
    """
    if x > x_max:
        x = x_max 
    elif x < x_min:
        x = x_min
        
    return x    

#------------------------------------------------------------------------------

def Smtrx(a):
    """
    S = Smtrx(a) computes the 3x3 vector skew-symmetric matrix S(a) = -S(a)'.
    The cross product satisfies: a x b = S(a)b. 
    """
 
    S = np.array([ 
        [ 0, -a[2], a[1] ],
        [ a[2],   0,     -a[0] ],
        [-a[1],   a[0],   0 ]  ])

    return S


#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
def skew_symmetric(vector):
    """
    Generates a skew-symmetric matrix for a given vector.

    Args:
        vector (numpy array): A 3-element vector.

    Returns:
        numpy array: A 3x3 skew-symmetric matrix.
    """
    return np.array([
        [0, -vector[2], vector[1]],
        [vector[2], 0, -vector[0]],
        [-vector[1], vector[0], 0]
    ])

#------------------------------------------------------------------------------



#------------------------------------------------------------------------------

def dcm_derivatives(C, omega_b_bn, omega_dot_b_bn):
    """
    Calculates the derivatives of the Direction Cosine Matrix (DCM) and its inverse.

    Args:
        C (numpy array): 3x3 Direction Cosine Matrix (DCM) representing the
                         rotation from navigation to body frame.
        omega_b_bn (numpy array): Angular velocity vector in the **body frame**
                                  relative to the navigation frame (rad/s).
        omega_dot_b_bn (numpy array): Angular acceleration vector in the **body frame**
                                      relative to the navigation frame (rad/s²).

    Returns:
        dict: A dictionary containing:
            - "C_dot": Derivative of the DCM (rotation rate matrix in the body frame).
            - "C_dot_inv": Derivative of the inverse DCM.
            - "C_ddot_inv": Second derivative of the inverse DCM.
    """
    # Calculate skew-symmetric matrices for angular velocity and acceleration
    S_omega_b_bn = skew_symmetric(omega_b_bn)  # S(omega_b_bn)
    S_omega_dot_b_bn = skew_symmetric(omega_dot_b_bn)  # S(omega_dot_b_bn)
    S2_omega_b_bn = S_omega_b_bn @ S_omega_b_bn  # S^2(omega_b_bn)

    # Derivative of the DCM
    # \dot{C} = S^2(\omega_{b_bn})C - S(\dot{\omega}_{b_bn})C
    C_dot = S2_omega_b_bn @ C - S_omega_dot_b_bn @ C

    # Inverse of the DCM (C^{-1} = C^T for orthogonal rotation matrices)
    C_inv = C.T

    # Derivative of the inverse DCM
    # \dot{C}^{-1} = C^{-1} S(\omega_{b_bn})
    C_dot_inv = C_inv @ S_omega_b_bn

    # Second derivative of the inverse DCM
    # \ddot{C}^{-1} = C^{-1} [ S^2(\omega_{b_bn}) + S(\dot{\omega}_{b_bn}) ]
    C_ddot_inv = C_inv @ (S2_omega_b_bn + S_omega_dot_b_bn)

    return {
        "C_dot": C_dot,
        "C_dot_inv": C_dot_inv,
        "C_ddot_inv": C_ddot_inv
    }

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
def dcm_derivative_single_axis(theta, theta_dot, axis):
    """
    Calculates the time derivative of the DCM around a single principal axis.

    Args:
        theta (float): Rotation angle (rad) for the selected axis.
        theta_dot (float): Angular rate (rad/s) for the selected axis.
        axis (int): The axis of interest (1, 2, or 3).

    Returns:
        numpy array: 3x3 matrix representing the time derivative of the DCM for the selected axis.
    """
    if axis == 1:
        # Time derivative of DCM around the first principal axis
        C_dot = np.array([
            [0, 0, 0],
            [0, -np.sin(theta) * theta_dot, np.cos(theta) * theta_dot],
            [0, -np.cos(theta) * theta_dot, -np.sin(theta) * theta_dot]
        ])
    elif axis == 2:
        # Time derivative of DCM around the second principal axis
        C_dot = np.array([
            [-np.sin(theta) * theta_dot, 0, -np.cos(theta) * theta_dot],
            [0, 0, 0],
            [np.cos(theta) * theta_dot, 0, -np.sin(theta) * theta_dot]
        ])
    elif axis == 3:
        # Time derivative of DCM around the third principal axis
        C_dot = np.array([
            [-np.sin(theta) * theta_dot, np.cos(theta) * theta_dot, 0],
            [np.cos(theta) * theta_dot, -np.sin(theta) * theta_dot, 0],
            [0, 0, 0]
        ])
    else:
        raise ValueError("Invalid axis. Must be 1, 2, or 3.")

    return C_dot
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
def dot_skew_squared(r, r_dot):
    """
    Calculates the time derivative of the square of the skew-symmetric matrix of vector r.

    Parameters:
    - r: np.array, shape (3,), the input vector.
    - r_dot: np.array, shape (3,), the time derivative of the input vector r.

    Returns:
    - np.array, shape (3, 3): The derivative of the square of the skew-symmetric matrix of r.
    """
    # Compute the outer product r_dot * r^T
    term1 = np.outer(r_dot, r)

    # Compute the outer product r * r_dot^T
    term2 = np.outer(r, r_dot)

    # Compute the scalar (r_dot . r) and multiply by the 3x3 identity matrix
    term3 = 2 * np.dot(r, r_dot) * np.eye(3)

    # Compute the final result
    result = term1 + term2 - term3

    return result
#------------------------------------------------------------------------------

def Hmtrx(r):
    """
    H = Hmtrx(r) computes the 6x6 system transformation matrix
    H = [eye(3)     S'
         zeros(3,3) eye(3) ]       Property: inv(H(r)) = H(-r)

    If r = r_bg is the vector from the CO to the CG, the model matrices in CO and
    CG are related by: M_CO = H(r_bg)' * M_CG * H(r_bg). Generalized position and
    force satisfy: eta_CO = H(r_bg)' * eta_CG and tau_CO = H(r_bg)' * tau_CG 
    """

    H = np.identity(6,float)
    H[0:3, 3:6] = Smtrx(r).T

    return H

#------------------------------------------------------------------------------

def Rzyx(phi,theta,psi):
    """
    R = Rzyx(phi,theta,psi) computes the Euler angle rotation matrix R in SO(3)
    using the zyx convention
    """
    
    cphi = math.cos(phi)
    sphi = math.sin(phi)
    cth  = math.cos(theta)
    sth  = math.sin(theta)
    cpsi = math.cos(psi)
    spsi = math.sin(psi)
    
    R = np.array([
        [ cpsi*cth, -spsi*cphi+cpsi*sth*sphi, spsi*sphi+cpsi*cphi*sth ],
        [ spsi*cth,  cpsi*cphi+sphi*sth*spsi, -cpsi*sphi+sth*spsi*cphi ],
        [ -sth,      cth*sphi,                 cth*cphi ] ])

    return R

#------------------------------------------------------------------------------


# ------------------------------------------------------------------------------

def quaternion_to_dcm(q):
    """
    Converts a quaternion [q0, q1, q2, q3], with scalar part q0, to a Direction
    Cosine Matrix (DCM).

    Parameters:
        q (list or numpy array): Quaternion [q0, q1, q2, q3]

    Returns:
        numpy array: 3x3 Direction Cosine Matrix (DCM)
    """
    rot = R.from_quat(q, scalar_first=True)
    dcm = rot.as_matrix()

    return dcm
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
def quaternion_to_angles(q):
    """
    Converts a quaternion [q0, q1, q2, q3] to Euler angles (phi, theta, psi) using the 3-2-1 sequence.
    The quaternion is assumed to be in the form [q0, q1, q2, q3], where q1, q2, q3 are
    the vector components and q0 is the real part.

    Parameters:
        q (list or numpy array): Quaternion [q0, q1, q2, q3]

    Returns:
        tuple: Euler angles (psi, theta, phi) in radians, that is phi=roll, theta=pitch, psi=yaw)
    """

    rot = R.from_quat(q, scalar_first=True)
    rot_euler = rot.as_euler('xyz')
    phi, theta, psi = rot_euler

    return psi, theta, phi
# ------------------------------------------------------------------------------

def Tzyx(phi,theta):
    """
    T = Tzyx(phi,theta) computes the Euler angle attitude
    transformation matrix T using the zyx convention
    """
    
    cphi = math.cos(phi)
    sphi = math.sin(phi)
    cth  = math.cos(theta)
    sth  = math.sin(theta)    

    try: 
        T = np.array([
            [ 1,  sphi*sth/cth,  cphi*sth/cth ],
            [ 0,  cphi,          -sphi],
            [ 0,  sphi/cth,      cphi/cth] ])
        
    except ZeroDivisionError:  
        print ("Tzyx is singular for theta = +-90 degrees." )
        
    return T
#------------------------------------------------------------------------------

def attitudeEuler(eta,nu,sampleTime):
    """
    eta = attitudeEuler(eta,nu,sampleTime) computes the generalized 
    position/Euler angles eta[k+1]
    """
   
    p_dot   = np.matmul( Rzyx(eta[3], eta[4], eta[5]), nu[0:3] )
    v_dot   = np.matmul( Tzyx(eta[3], eta[4]), nu[3:6] )

    # Forward Euler integration
    eta[0:3] = eta[0:3] + sampleTime * p_dot
    eta[3:6] = eta[3:6] + sampleTime * v_dot

    return eta


#------------------------------------------------------------------------------

def m2c(M, nu):
    """
    C = m2c(M,nu) computes the Coriolis and centripetal matrix C from the
    mass matrix M and generalized velocity vector nu (Fossen 2021, Ch. 3)
    """

    M = 0.5 * (M + M.T)     # systematization of the inertia matrix

    if (len(nu) == 6):      #  6-DOF model
    
        M11 = M[0:3,0:3]
        M12 = M[0:3,3:6] 
        M21 = M12.T
        M22 = M[3:6,3:6] 
    
        nu1 = nu[0:3]
        nu2 = nu[3:6]
        dt_dnu1 = np.matmul(M11,nu1) + np.matmul(M12,nu2)
        dt_dnu2 = np.matmul(M21,nu1) + np.matmul(M22,nu2)

        #C  = [  zeros(3,3)      -Smtrx(dt_dnu1)
        #      -Smtrx(dt_dnu1)  -Smtrx(dt_dnu2) ]
        C = np.zeros( (6,6) )    
        C[0:3,3:6] = -Smtrx(dt_dnu1)
        C[3:6,0:3] = -Smtrx(dt_dnu1)
        C[3:6,3:6] = -Smtrx(dt_dnu2)
            
    else:   # 3-DOF model (surge, sway and yaw)
        #C = [ 0             0            -M(2,2)*nu(2)-M(2,3)*nu(3)
        #      0             0             M(1,1)*nu(1)
        #      M(2,2)*nu(2)+M(2,3)*nu(3)  -M(1,1)*nu(1)          0  ]    
        C = np.zeros( (3,3) ) 
        C[0,2] = -M[1,1] * nu[1] - M[1,2] * nu[2]
        C[1,2] =  M[0,0] * nu[0] 
        C[2,0] = -C[0,2]       
        C[2,1] = -C[1,2]
        
    return C
#------------------------------------------------------------------------------

def Hoerner(B,T):
    """
    CY_2D = Hoerner(B,T)
    Hoerner computes the 2D Hoerner cross-flow form coeff. as a function of beam 
    B and draft T.The data is digitized and interpolation is used to compute 
    other data point than those in the table
    """
    
    # DATA = [B/2T  C_D]
    DATA1 = np.array([
        0.0109,0.1766,0.3530,0.4519,0.4728,0.4929,0.4933,0.5585,0.6464,0.8336,
        0.9880,1.3081,1.6392,1.8600,2.3129,2.6000,3.0088,3.4508, 3.7379,4.0031 
        ])
    DATA2 = np.array([
        1.9661,1.9657,1.8976,1.7872,1.5837,1.2786,1.2108,1.0836,0.9986,0.8796,
        0.8284,0.7599,0.6914,0.6571,0.6307,0.5962,0.5868,0.5859,0.5599,0.5593 
        ])

    CY_2D = np.interp( B / (2 * T), DATA1, DATA2 )
        
    return CY_2D

#------------------------------------------------------------------------------

def crossFlowDrag(L,B,T,nu_r):
    """
    tau_crossflow = crossFlowDrag(L,B,T,nu_r) computes the cross-flow drag 
    integrals for a marine craft using strip theory. 

    M d/dt nu_r + C(nu_r)*nu_r + D*nu_r + g(eta) = tau + tau_crossflow
    """

    rho = 1026               # density of water
    n = 20                   # number of strips

    dx = L/20             
    Cd_2D = Hoerner(B,T)    # 2D drag coefficient based on Hoerner's curve

    Yh = 0
    Nh = 0
    xL = -L/2
    
    for i in range(0,n+1):
        v_r = nu_r[1]             # relative sway velocity
        r = nu_r[5]               # yaw rate
        Ucf = abs(v_r + xL * r) * (v_r + xL * r)
        Yh = Yh - 0.5 * rho * T * Cd_2D * Ucf * dx         # sway force
        Nh = Nh - 0.5 * rho * T * Cd_2D * xL * Ucf * dx    # yaw moment
        xL += dx
        
    tau_crossflow = np.array([0, Yh, 0, 0, 0, Nh],float)

    return tau_crossflow

#------------------------------------------------------------------------------

def forceLiftDrag(b,S,CD_0,alpha,U_r):
    """
    tau_liftdrag = forceLiftDrag(b,S,CD_0,alpha,Ur) computes the hydrodynamic
    lift and drag forces of a submerged "wing profile" for varying angle of
    attack (Beard and McLain 2012). Application:
    
      M d/dt nu_r + C(nu_r)*nu_r + D*nu_r + g(eta) = tau + tau_liftdrag
    
    Inputs:
        b:     wing span (m)
        S:     wing area (m^2)
        CD_0:  parasitic drag (alpha = 0), typically 0.1-0.2 for a streamlined body
        alpha: angle of attack, scalar or vector (rad)
        U_r:   relative speed (m/s)

    Returns:
        tau_liftdrag:  6x1 generalized force vector
    """

    # constants
    rho = 1026

    def coeffLiftDrag(b,S,CD_0,alpha,sigma):
        
        """
        [CL,CD] = coeffLiftDrag(b,S,CD_0,alpha,sigma) computes the hydrodynamic 
        lift CL(alpha) and drag CD(alpha) coefficients as a function of alpha
        (angle of attack) of a submerged "wing profile" (Beard and McLain 2012)

        CD(alpha) = CD_p + (CL_0 + CL_alpha * alpha)^2 / (pi * e * AR)
        CL(alpha) = CL_0 + CL_alpha * alpha
  
        where CD_p is the parasitic drag (profile drag of wing, friction and
        pressure drag of control surfaces, hull, etc.), CL_0 is the zero angle 
        of attack lift coefficient, AR = b^2/S is the aspect ratio and e is the  
        Oswald efficiency number. For lift it is assumed that
  
        CL_0 = 0
        CL_alpha = pi * AR / ( 1 + sqrt(1 + (AR/2)^2) );
  
        implying that for alpha = 0, CD(0) = CD_0 = CD_p and CL(0) = 0. For
        high angles of attack the linear lift model can be blended with a
        nonlinear model to describe stall
  
        CL(alpha) = (1-sigma) * CL_alpha * alpha + ...
            sigma * 2 * sign(alpha) * sin(alpha)^2 * cos(alpha) 

        where 0 <= sigma <= 1 is a blending parameter. 
        
        Inputs:
            b:       wing span (m)
            S:       wing area (m^2)
            CD_0:    parasitic drag (alpha = 0), typically 0.1-0.2 for a 
                     streamlined body
            alpha:   angle of attack, scalar or vector (rad)
            sigma:   blending parameter between 0 and 1, use sigma = 0 f
                     or linear lift 
            display: use 1 to plot CD and CL (optionally)
        
        Returns:
            CL: lift coefficient as a function of alpha   
            CD: drag coefficient as a function of alpha   

        Example:
            Cylinder-shaped AUV with length L = 1.8, diameter D = 0.2 and 
            CD_0 = 0.3
            
            alpha = 0.1 * pi/180
            [CL,CD] = coeffLiftDrag(0.2, 1.8*0.2, 0.3, alpha, 0.2)
        """
         
        e = 0.7             # Oswald efficiency number
        AR = b**2 / S       # wing aspect ratio

        # linear lift
        CL_alpha = math.pi * AR / ( 1 + math.sqrt(1 + (AR/2)**2) )
        CL = CL_alpha * alpha

        # parasitic and induced drag
        CD = CD_0 + CL**2 / (math.pi * e * AR)
        
        # nonlinear lift (blending function)
        CL = (1-sigma) * CL + sigma * 2 * np.sign(alpha) \
            * math.sin(alpha)**2 * math.cos(alpha)

        return CL, CD

    
    [CL, CD] = coeffLiftDrag(b,S,CD_0,alpha,0) 
    
    F_drag = 1/2 * rho * U_r**2 * S * CD    # drag force
    F_lift = 1/2 * rho * U_r**2 * S * CL    # lift force

    # transform from FLOW axes to BODY axes using angle of attack
    tau_liftdrag = np.array([
        math.cos(alpha) * (-F_drag[0]) - math.sin(alpha) * (-F_lift[0]),
        0,
        math.sin(alpha) * (-F_drag[2]) + math.cos(alpha) * (-F_lift[2]),
        0,
        0,
        0 ])
    #tau_liftdrag = np.array([
    #    math.cos(alpha) * (-F_drag) - math.sin(alpha) * (-F_lift),
    #    0,
    #    math.sin(alpha) * (-F_drag) + math.cos(alpha) * (-F_lift),
    #    0,
    #    0,
    #    0 ])

    return tau_liftdrag
    
#------------------------------------------------------------------------------
def MRB_function(mp, m, r_bp_b, r_bg_b, Ib_b):
        # Use the pre-existing Smtrx function to compute the skew-symmetric matrices
        S_r_bp_b = Smtrx(r_bp_b)
        S_r_bg_b = Smtrx(r_bg_b)

        # Construct each block of the matrix with correct signs
        M11 = mp * np.eye(3)
        M12 = mp * np.eye(3)
        M13 = -mp * S_r_bp_b  # Negative sign as per the given matrix
        M21 = mp * np.eye(3)
        M22 = (m + mp) * np.eye(3)
        M23 = -mp * S_r_bp_b - m * S_r_bg_b  # Negative signs as per the given matrix
        M31 = mp * S_r_bp_b
        M32 = mp * S_r_bp_b + m * S_r_bg_b
        M33 = Ib_b - mp * np.dot(S_r_bp_b, S_r_bp_b)

        # Combine into the full matrix MRB
        MRB = np.block([[M11, M12, M13],
                        [M21, M22, M23],
                        [M31, M32, M33]])
        return MRB


# ------------------------------------------------------------------------------
def gvect(W,B,theta,phi,r_bg,r_bb):
    """
    g = gvect(W,B,theta,phi,r_bg,r_bb) computes the 6x1 vector of restoring 
    forces about an arbitrarily point CO for a submerged body. 
    
    Inputs:
        W, B: weight and buoyancy (kg)
        phi,theta: roll and pitch angles (rad)
        r_bg = [x_g y_g z_g]: location of the CG with respect to the CO (m)
        r_bb = [x_b y_b z_b]: location of the CB with respect to th CO (m)
        
    Returns:
        g: 6x1 vector of restoring forces about CO
    """

    sth  = math.sin(theta)
    cth  = math.cos(theta)
    sphi = math.sin(phi)
    cphi = math.cos(phi)

    #print(f"r_bg: {r_bg}")
    #print(f"r_bb: {r_bb}")
    #print(f"r_diff: {r_bg - r_bb}")
    #print(f"sth: {sth:.3f}, cth: {cth:.3f}, sphi: {sphi}, cphi: {cphi}")

    g = np.array([
        (W-B) * sth,
        -(W-B) * cth * sphi,
        -(W-B) * cth * cphi,
        -(r_bg[1]*W-r_bb[1]*B) * cth * cphi + (r_bg[2]*W-r_bb[2]*B) * cth * sphi,
        (r_bg[2]*W-r_bb[2]*B) * sth         + (r_bg[0]*W-r_bb[0]*B) * cth * cphi,
        -(r_bg[0]*W-r_bb[0]*B) * cth * sphi - (r_bg[1]*W-r_bb[1]*B) * sth      
        ])
    
    return g


def calculate_dcm(order, angles):
    """
    Calculates the Direction Cosine Matrix (DCM) for a given rotation order and angles.

    Parameters:
        order (list or tuple): A sequence of integers specifying the order of rotation (e.g., 1 for X, 2 for Y, 3 for Z).
        angles (list or tuple): A vector of rotation angles in radians.

    Returns:
        numpy.ndarray: A 3x3 DCM matrix.
    """

    def rotation_matrix(axis, angle):
        """
        Creates a rotation matrix for a given axis and angle.

        Parameters:
            axis (int): An identifier for the axis of rotation (arbitrary numbers are mapped to X, Y, Z).
            angle (float): Rotation angle in radians.

        Returns:
            numpy.ndarray: 3x3 rotation matrix for the axis.
        """
        c = np.cos(angle)
        s = np.sin(angle)

        # Map arbitrary numbers to X, Y, Z
        if axis in [1, 'X']:  # X-axis
            return np.array([
                [1, 0, 0],
                [0, c, s],
                [0, -s, c]
            ])
        elif axis in [2, 'Y']:  # Y-axis
            return np.array([
                [c, 0, -s],
                [0, 1, 0],
                [s, 0, c]
            ])
        elif axis in [3, 'Z']:  # Z-axis
            return np.array([
                [c, s, 0],
                [-s, c, 0],
                [0, 0, 1]
            ])
        else:
            raise ValueError("Invalid axis identifier. Use 1 (X), 2 (Y), or 3 (Z).")

    # Validate inputs
    if len(order) != len(angles):
        raise ValueError("Order and angles must have the same number of elements.")

    # Compute the DCM
    dcm = np.eye(3)  # Start with the identity matrix
    for axis, angle in zip(order, angles):
        dcm = np.dot(rotation_matrix(axis, angle), dcm)

    return dcm




class MultiVariablePiecewiseSignal:
    """
    MultiVariablePiecewiseSignal allows creating and evaluating piecewise-defined signals for multiple variables.

    Features:
    - **Supports multiple variables**: Each variable can have its own independent piecewise definition.
    - **Built-in signal types**:
        - `sin`: Sinusoidal wave with frequency, amplitude, and optional phase.
        - `cos`: Cosine wave with frequency, amplitude, and optional phase.
        - `square`: Square wave with customizable upper/lower bounds, period, and duty cycle.
        - `ramp`: Linearly increasing or decreasing signal based on start and end values or slope.
        - `constant`: Fixed-value signal over a specified interval.
        - `custom`: User-defined symbolic function, allowing advanced mathematical expressions.
        - `data`: Interpolation over user-provided data points.
    - **Direct Evaluation for Functions**:
        - For `sin`, `cos`, `ramp`, `constant`, `custom`, and `square`, values are computed directly at query time.
        - No global interpolation is applied for these function-based signals.
    - **Advanced Interpolation for `data`**:
        - Only `data` signals use interpolation at query time, based on specified methods (`"linear"`, `"pchip"`, `"spline"`, etc.).
    - **Out-of-Range Handling**:
        - Supports `"zero"`, `"continue"`, and `"function"` modes for times outside defined intervals.
        - Out-of-range logic is applied both at initialization (for the precomputed signal) and at query time.
    - **Relative and Absolute Time Handling**:
        - `time_mode="relative"`: Each interval's time starts at zero from its own start.
        - `time_mode="absolute"`: Uses the global time as-is.
    - **Continuity Handling**:
        - If `continuity=True`, adjusts the piece's starting value to ensure a smooth transition from the previous piece.
    - **Interval Endpoint Handling**:
        - Interval endpoints belong to the earlier piece if two intervals share a boundary. For example, if intervals are (0,3) and (3,7), the value at t=3 belongs to the first interval.
    - **Boundary Inclusion**:
        - All interval boundaries are included in the global `self.time` array, ensuring correct evaluation at exact boundaries.
    """

    def __init__(self, time, variable_pieces):
        """
        Parameters:
        - time (array-like): Global time array.
        - variable_pieces (list): List of piecewise definitions for each variable.

        Initialization steps:
        1. Convert the input `time` to a NumPy array.
        2. Extract all interval boundaries from the provided piecewise definitions.
        3. Combine the original `time` with these boundaries, ensuring they are included in `self.time`.
        4. Precompute the piecewise-defined signals for each variable over `self.time`, applying continuity and out-of-range rules.
        5. Store piecewise metadata for later direct evaluation at query time.
        """
        self.variable_pieces = variable_pieces

        # Convert to numpy array for consistent handling
        time = np.array(time, dtype=float)

        # Extract all start and end points of intervals from all variables
        boundaries = []
        for var_pieces in variable_pieces:
            for piece in var_pieces:
                start, end = piece["interval"]
                boundaries.append(start)
                boundaries.append(end)
        boundaries = np.unique(boundaries)

        # Combine user-provided time with interval boundaries
        combined_time = np.unique(np.concatenate((time, boundaries)))
        self.time = combined_time

        # Compute signals and store piece info
        self.signals = []
        self.variable_info = []  # Stores metadata needed for direct evaluation at query time
        for pieces in self.variable_pieces:
            sig, info = self._generate_signal(pieces)
            self.signals.append(sig)
            self.variable_info.append(info)

    def _evaluate_function(self, name, params, t, t_start, t_end, offset=0):
        """
        Evaluates a given function for time array `t`, applying any continuity `offset` if needed.

        Supported Functions and their parameters:
        - `sin` and `cos`: freq (Hz), amp, optional phase.
        - `square`: period, upper, lower, duty cycle.
        - `ramp`: start_val, end_val/slope.
        - `constant`: val.
        - `custom`: formula (string).
        - `data`: data_points, interp_method.

        If `data` is used, interpolation is performed from given data points.
        For all others, values are computed directly from mathematical formulas.

        The `offset` shifts the evaluated result to ensure continuity if `continuity=True` was used.
        """
        if name == "sin":
            freq = params.get("freq", 1)
            amp = params.get("amp", 1)
            return amp * np.sin(2 * np.pi * freq * t + offset)
        elif name == "cos":
            freq = params.get("freq", 1)
            amp = params.get("amp", 1)
            return amp * np.cos(2 * np.pi * freq * t + offset)
        elif name == "square":
            period = params.get("period", 1)
            upper = params.get("upper", 1)
            lower = params.get("lower", -1)
            duty = params.get("duty", 50) / 100
            t_adjusted = t % period
            return np.where(t_adjusted < (duty * period), upper, lower)
        elif name == "ramp":
            start_val = params.get("start_val", 0) + offset
            if "end_val" in params:
                end_val = params["end_val"]
                return start_val + (end_val - start_val) * (t - t_start) / (t_end - t_start)
            elif "slope" in params:
                slope = params["slope"]
                return start_val + slope * (t - t_start)
            else:
                raise ValueError("Ramp must define either 'end_val' or 'slope'.")
        elif name == "constant":
            return np.full_like(t, params.get("val", 0) + offset)
        elif name == "custom":
            formula = params.get("formula", "0")
            t_sym = symbols("t")
            custom_func = lambdify(t_sym, formula, "numpy")
            return custom_func(t) + offset
        elif name == "data":
            # For data, we interpolate from given points
            data_points = params.get("data_points")
            interp_method = params.get("interp_method", "linear")
            if not data_points or len(data_points) < 2:
                raise ValueError("Data interpolation requires at least two points.")
            data_t, data_vals = zip(*data_points)
            data_t = np.array(data_t, dtype=float)
            data_vals = np.array(data_vals, dtype=float)

            # Choose appropriate interpolation method
            if interp_method == "pchip":
                interpolator = PchipInterpolator(data_t, data_vals)
            elif interp_method == "spline":
                interpolator = CubicSpline(data_t, data_vals)
            else:
                interpolator = interp1d(data_t, data_vals, kind=interp_method, fill_value="extrapolate")

            return interpolator(t) + offset
        else:
            raise ValueError(f"Unsupported function name: {name}")

    def _generate_signal(self, pieces):
        """
        Generates the piecewise-defined signal for a single variable over `self.time`.

        Steps:
        1. Initialize a zero array for `signal`.
        2. Iterate over each piece (interval).
        3. Apply continuity if `continuity=True`.
        4. Compute the piece's values and store them in the `signal`.
        5. Keep track of `last_value` for continuity with the next piece.
        6. After all pieces are processed, handle out-of-range behavior for times beyond the last interval.

        This method also collects `piece_info` which includes:
        - start, end
        - name, params
        - time_mode (relative/absolute)
        - offset (for continuity)
        - out_of_range mode
        - last_value (for continuing the signal if needed out-of-range)

        The final computed `signal` over `self.time` includes in-range values and properly assigned out-of-range values.
        """
        signal = np.zeros_like(self.time)
        last_value = 0
        prev_end = None

        piece_info = []

        # Variables to store final piece info for out-of-range handling after the loop
        final_name = None
        final_params = {}
        final_offset = 0
        final_start = None
        final_end = None
        final_out_of_range = "zero"

        for idx, piece in enumerate(pieces):
            start, end = piece["interval"]
            name = piece["name"]
            params = piece.get("params", {})
            continuity = piece.get("continuity", False)
            out_of_range = piece.get("out_of_range", "zero") if idx == len(pieces) - 1 else None
            time_mode = piece.get("time_mode", "absolute")

            # Determine the mask for this interval:
            # If start equals the previous end, then this interval starts strictly after that point.
            if prev_end is not None and np.isclose(start, prev_end, atol=1e-15):
                mask = (self.time > start) & (self.time <= end)
            else:
                mask = (self.time >= start) & (self.time <= end)

            # Determine input time array for this piece (relative or absolute)
            t_input = self.time[mask] - start if time_mode == "relative" else self.time[mask]

            # Handle continuity if needed
            if continuity and mask.any():
                if name == "square":
                    # Continuity doesn't really apply for a discrete jump signal like square, but we warn anyway.
                    print(f"Warning: Continuity ignored for square wave at {start}-{end}.")
                    offset = 0
                else:
                    # Evaluate the first point of this piece to see if we need an offset for continuity
                    calculated_start = self._evaluate_function(name, params, np.array([t_input[0]]), start, end)[0]
                    if not np.isclose(last_value, calculated_start, atol=1e-6):
                        print(f"Warning: Continuity enforced at interval {start}-{end}. Adjusting start value.")
                    offset = last_value - calculated_start
            else:
                offset = 0

            # Evaluate this piece and store in the signal
            if mask.any():
                signal[mask] = self._evaluate_function(name, params, t_input, start, end, offset)
                last_value = signal[mask][-1]  # Update last_value for continuity/out_of_range

            # Store metadata for query-time direct evaluations
            piece_info.append({
                "start": start,
                "end": end,
                "name": name,
                "params": params,
                "time_mode": time_mode,
                "offset": offset,
                "out_of_range": out_of_range,
                "last_value": last_value
            })

            # Update final piece info
            final_name = name
            final_params = params
            final_offset = offset
            final_start = start
            final_end = end
            if out_of_range is not None:
                final_out_of_range = out_of_range

            prev_end = end

        # Handle out-of-range for times beyond the last interval
        if final_end is not None:
            beyond_mask = self.time > final_end
            if final_out_of_range == "zero":
                # Assign zero beyond the last piece
                signal[beyond_mask] = 0
            elif final_out_of_range == "continue":
                # Hold the last value constant beyond the last piece
                signal[beyond_mask] = last_value
            elif final_out_of_range == "function":
                # Continue the function beyond its end
                extended_time = self.time[beyond_mask]
                t_input = extended_time - final_end
                out_of_range_values = self._evaluate_function(final_name, final_params, t_input, final_start, final_end, final_offset)
                signal[beyond_mask] = out_of_range_values

        return signal, piece_info

    def __call__(self, t, method=None):
        """
        Evaluates the signals at the given time points `t`.

        Query-Time Logic:
        - For each queried time and each variable, determine which piece interval it falls into.
        - If it's a function-based piece (sin, cos, square, ramp, constant, custom), directly compute using stored piece params and offset.
        - If it's a data-based piece, interpolate using that piece's data and interpolation method.
        - If the query time is out-of-range, apply the final piece's out_of_range rules.

        The `method` parameter is retained for interface compatibility but isn't used to override per-piece interpolation methods.

        Returns:
        - A list of arrays, one per variable, with the evaluated signals at the queried times.
        """
        t = np.array(t, dtype=float)
        results = []

        for var_idx, var_info in enumerate(self.variable_info):
            var_results = np.zeros_like(t, dtype=float)

            # The last piece defines out-of-range rules for times beyond the last interval
            last_piece = var_info[-1]

            for i, query_time in enumerate(t):
                piece_found = False
                # Determine which piece this query time belongs to
                for idx, piece in enumerate(var_info):
                    start = piece["start"]
                    end = piece["end"]
                    name = piece["name"]
                    params = piece["params"]
                    time_mode = piece["time_mode"]
                    offset = piece["offset"]
                    out_of_range = piece["out_of_range"]
                    last_val_piece = piece["last_value"]

                    # Check if query_time falls into this interval.
                    # If the start matches previous piece's end, start is exclusive for this piece.
                    if idx > 0 and np.isclose(start, var_info[idx-1]["end"], atol=1e-15):
                        in_interval = (query_time > start) and (query_time <= end)
                    else:
                        in_interval = (query_time >= start) and (query_time <= end)

                    if in_interval:
                        # Evaluate directly for function-based, or interpolate if data-based
                        t_input = query_time - start if time_mode == "relative" else query_time
                        t_input = np.array([t_input])
                        val = self._evaluate_function(name, params, t_input, start, end, offset)[0]
                        var_results[i] = val
                        piece_found = True
                        break

                if not piece_found:
                    # If not found in any piece, it's out-of-range
                    first_piece = var_info[0]
                    if query_time < first_piece["start"]:
                        # Before the first interval: default to zero
                        var_results[i] = 0
                    else:
                        # Beyond the last interval
                        start = last_piece["start"]
                        end = last_piece["end"]
                        name = last_piece["name"]
                        params = last_piece["params"]
                        offset = last_piece["offset"]
                        out_of_range = last_piece["out_of_range"]
                        last_val_piece = last_piece["last_value"]

                        if out_of_range == "zero":
                            var_results[i] = 0
                        elif out_of_range == "continue":
                            var_results[i] = last_val_piece
                        elif out_of_range == "function":
                            t_input = np.array([query_time - end])
                            val = self._evaluate_function(name, params, t_input, start, end, offset)[0]
                            var_results[i] = val
                        else:
                            var_results[i] = 0

            results.append(var_results)

        return results
