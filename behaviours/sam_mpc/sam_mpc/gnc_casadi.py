"""
GNC functions for the casadi model. 
Only the necessary functions from gnc.py to make the model work are converted in this script

"""
import casadi as ca


def skew_symmetric_ca(v):
    """
    Skew symmetric matrix
    """
    return ca.vertcat(
        ca.horzcat(0, -v[2], v[1]),
        ca.horzcat(v[2], 0, -v[0]),
        ca.horzcat(-v[1], v[0], 0)
    )

def m2c_ca(M, nu):
    """
    C = m2c(M, nu) computes the Coriolis and centripetal matrix C from the
    mass matrix M and generalized velocity vector nu (Fossen 2021, Ch. 3)
    """

    M = 0.5 * (M + M.T)  # systematization of the inertia matrix

    if nu.size1() == 6:  # 6-DOF model
        M11 = M[0:3, 0:3]
        M12 = M[0:3, 3:6]
        M21 = M[3:6, 0:3]
        M22 = M[3:6, 3:6]

        nu1 = nu[0:3]
        nu2 = nu[3:6]
        dt_dnu1 = ca.mtimes(M11, nu1) + ca.mtimes(M12, nu2)
        dt_dnu2 = ca.mtimes(M21, nu1) + ca.mtimes(M22, nu2)

        C = ca.MX.zeros(6, 6)
        C[0:3, 3:6] = -skew_symmetric_ca(dt_dnu1)
        C[3:6, 0:3] = -skew_symmetric_ca(dt_dnu1)
        C[3:6, 3:6] = -skew_symmetric_ca(dt_dnu2)

    else:  # 3-DOF model (surge, sway, and yaw)
        C = ca.MX.zeros(3, 3)
        C[0, 2] = -M[1, 1] * nu[1] - M[1, 2] * nu[2]
        C[1, 2] = M[0, 0] * nu[0]
        C[2, 0] = -C[0, 2]
        C[2, 1] = -C[1, 2]

    return C

def gvect_ca(W,B,theta,phi,r_bg,r_bb):
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

    sth  = ca.sin(theta)
    cth  = ca.cos(theta)
    sphi = ca.sin(phi)
    cphi = ca.cos(phi)

    g = ca.vertcat(
        (W-B) * sth,
        -(W-B) * cth * sphi,
        -(W-B) * cth * cphi,
        -(r_bg[1]*W-r_bb[1]*B) * cth * cphi + (r_bg[2]*W-r_bb[2]*B) * cth * sphi,
        (r_bg[2]*W-r_bb[2]*B) * sth         + (r_bg[0]*W-r_bb[0]*B) * cth * cphi,
        -(r_bg[0]*W-r_bb[0]*B) * cth * sphi - (r_bg[1]*W-r_bb[1]*B) * sth      
        )
    
    return g

def calculate_dcm_ca(order, angles):
    """
    Calculates the Direction Cosine Matrix (DCM) for a given rotation order and angles.

    Parameters:
        order (list or tuple): A sequence of integers specifying the order of rotation (e.g., 1 for X, 2 for Y, 3 for Z).
        angles (list or tuple): A vector of rotation angles in radians.

    Returns:
        casadi.MX: A 3x3 DCM matrix.
    """

    def rotation_matrix_ca(axis, angle):
        """
        Creates a rotation matrix for a given axis and angle.

        Parameters:
            axis (int): An identifier for the axis of rotation (arbitrary numbers are mapped to X, Y, Z).
            angle (float): Rotation angle in radians.

        Returns:
            casadi.MX: 3x3 rotation matrix for the axis.
        """
        c = ca.cos(angle)
        s = ca.sin(angle)

        # Map arbitrary numbers to X, Y, Z
        if axis in [1, 'X']:  # X-axis
            return ca.vertcat(
                ca.horzcat(1, 0, 0),
                ca.horzcat(0, c, s),
                ca.horzcat(0, -s, c)
            )
        elif axis in [2, 'Y']:  # Y-axis
            return ca.vertcat(
                ca.horzcat(c, 0, -s),
                ca.horzcat(0, 1, 0),
                ca.horzcat(s, 0, c)
            )
        elif axis in [3, 'Z']:  # Z-axis
            return ca.vertcat(
                ca.horzcat(c, s, 0),
                ca.horzcat(-s, c, 0),
                ca.horzcat(0, 0, 1)
            )
        else:
            raise ValueError("Invalid axis identifier. Use 1 (X), 2 (Y), or 3 (Z).")

    # Validate inputs
    if len(order) != len(angles):
        raise ValueError("Order and angles must have the same number of elements.")

    # Compute the DCM
    dcm = ca.MX.eye(3)  # Start with the identity matrix
    for axis, angle in zip(order, angles):
        dcm = ca.mtimes(rotation_matrix_ca(axis, angle), dcm)

    return dcm

def quaternion_to_dcm_ca(q):
    """
    Converts a quaternion [q0, q1, q2, q3], with scalar part q0, to a Direction
    Cosine Matrix (DCM).

    Parameters:
        q (list or casadi.MX): Quaternion [q0, q1, q2, q3]

    Returns:
        casadi.MX: 3x3 Direction Cosine Matrix (DCM)
    """
    q0, q1, q2, q3 = q[0], q[1], q[2], q[3]

    dcm = ca.vertcat(
        ca.horzcat(1 - 2 * (q2**2 + q3**2), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)),
        ca.horzcat(2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1**2 + q3**2), 2 * (q2 * q3 - q0 * q1)),
        ca.horzcat(2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1**2 + q2**2))
    )

    return dcm

def quaternion_to_angles_ca(quat):
        # Assuming quat is a CasADi SX or MX variable
        q0, q1, q2, q3 = quat[0], quat[1], quat[2], quat[3]
    
        # Compute the Euler angles from the quaternion
        psi = ca.atan2(2 * (q0*q3 + q1*q2), 1 - 2 * (q2**2 + q3**2))
        theta = ca.asin(2 * (q0*q2 - q3*q1))
        phi = ca.atan2(2 * (q0*q1 + q2*q3), 1 - 2 * (q1**2 + q2**2))
    
        return psi, theta, phi