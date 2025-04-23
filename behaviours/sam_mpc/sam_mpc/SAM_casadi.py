#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SAM.py:

   Class for the SAM (Small and Affordable Maritime) cylinder-shaped autonomous underwater vehicle (AUV),
   designed for agile hydrobatic maneuvers, including obstacle avoidance, inspections, docking, and under-ice operations.
   The SAM AUV is controlled using counter-rotating propellers, a thrust vectoring system, a variable buoyancy system (VBS),
   and adjustable battery packs for center of gravity (c.g.) control. It is equipped with sensors such as IMU, DVL, GPS, and sonar.

   The length of the AUV is 1.5 m, the cylinder diameter is 19 cm, and the mass of the vehicle is 17 kg.
   It has a maximum speed of 2.5 m/s, which is obtained when the propellers run at 1525 rpm in zero currents.
   SAM was developed by the Swedish Maritime Robotics Center and is underactuated, meaning it has fewer control inputs than
   degrees of freedom. The control system uses both static and dynamic actuation for different maneuvers.

   Actuator systems:
   1. **Counter-Rotating Propellers**: Two propellers used for propulsion, rotating in opposite directions to balance the roll and provide forward thrust.
   2. **Thrust Vectoring System**: Propellers can be deflected horizontally (rudder-like) and vertically (stern-plane-like) with angles up to ±7°, enabling agile maneuvers.
   3. **Variable Buoyancy System (VBS)**: Allows for depth control by altering buoyancy through water intake and release.
   4. **Adjustable Center of Gravity (c.g.) Control**: Movable battery packs adjust the longitudinal and transversal c.g. positions, allowing for pitch and roll control.

   Sensor systems:
   - **IMU**: Inertial Measurement Unit for attitude and acceleration.
   - **DVL**: Doppler Velocity Logger for measuring underwater velocity.
   - **GPS**: For surface position tracking.
   - **Sonar**: For environment sensing during navigation and inspections.

   SAM()
       Step input for tail rudder, stern plane, and propeller revolutions.

Methods:

    [xdot] = dynamics(x, u_ref) returns for integration

    u_ref: control inputs as [x_vbs, x_lcg, delta_s, delta_r, rpm1, rpm2]

        - **vbs**: Variable buoyancy system control, which adjusts buoyancy to control depth.
        - **lcg**: Longitudinal center of gravity adjustment by moving the battery pack to control pitch.
        - **delta_s**: Stern plane angle for vertical thrust vectoring, used to control pitch (nose up/down).
        - **delta_r**: Rudder angle for horizontal thrust vectoring, used to control yaw (turning left/right).
        - **rpm_1**: Propeller RPM for the first (counter-rotating) propeller, controlling forward thrust.
        - **rpm_2**: Propeller RPM for the second (counter-rotating) propeller, also controlling forward thrust and balancing roll.

References:

    Bhat, S., Panteli, C., Stenius, I., & Dimarogonas, D. V. (2023). Nonlinear model predictive control for hydrobatic AUVs:
        Experiments with the SAM vehicle. Journal of Field Robotics, 40(7), 1840-1859. doi:10.1002/rob.22218.

    T. I. Fossen (2021). Handbook of Marine Craft Hydrodynamics and Motion Control. 2nd Edition, Wiley.
        URL: www.fossen.biz/wiley

Author:     Omid Mirzaeedodangeh

Refactored: David Doerner
"""

import numpy as np
import casadi as ca

try:
    from .gnc import *
    from .gnc_casadi import *
except: 
    from gnc import *
    from gnc_casadi import *


class SolidStructure:
    """
    Represents the Solid Structure (SS) of the SAM AUV.

    Attributes:
        l_SS: Length of the solid structure (m).
        d_SS: Diameter of the solid structure (m).
        m_SS: Mass of the solid structure (kg).
        p_CSsg_O: Vector from frame C to CG of SS expressed in O (m)
        p_OSsg_O: Vector from CO to CG of SS expressed in O (m)
    """

    def __init__(self, l_ss, d_ss, m_ss, p_CSsg_O, p_OC_O):
        self.l_ss     = l_ss
        self.d_ss     = d_ss
        self.m_ss     = m_ss
        self.p_CSsg_O = p_CSsg_O
        self.p_OSsg_O = p_OC_O + self.p_CSsg_O


class VariableBuoyancySystem:
    """
    VariableBuoyancySystem Class

    Represents the Variable Buoyancy System (VBS) of the AUV.

    Parameters:
        d_vbs (float): Diameter of the VBS (m).
        l_vbs_l (float): Length of the VBS capsule (m).
        p_CVbs_O: Vector from frame C to CG of VBS in CO (m)
        p_OC_O: Vector from CO to C in CO

    Vectors follow Tedrake's monogram:
    https://manipulation.csail.mit.edu/pick.html#monogram
    """

    def __init__(self, r_vbs, l_vbs_l, p_CVbs_O, p_OC_O, rho_w):
        # Physical parameters
        self.r_vbs    = r_vbs # Radius of VBS chamber (m)
        self.l_vbs_l  = l_vbs_l  # Length of VBS capsule (m)
        self.p_CVbs_O = p_CVbs_O
        self.p_OVbs_O = p_OC_O + p_CVbs_O # FIXME: Check this how it goes into the CG calculation of the VBS. It changes with x_vbs, so you might want to adjust it as well.
        self.m_vbs    = rho_w * np.pi * self.r_vbs ** 2 * self.l_vbs_l/2 # Init the vbs with 50%

        # Motion bounds
        self.x_vbs_min = 0  # Minimum VBS position (m)
        self.x_vbs_max = l_vbs_l  # Maximum VBS position (m)
        self.x_vbs_dot_min = -10  # Maximum retraction speed (m/s)
        self.x_vbs_dot_max = 10 # FIXME: This is an estimate. Need to adjust, since the speed is given in mm/s, but we control on percentages right now. Maximum extension speed (m/s)


class LongitudinalCenterOfGravityControl:
    """
    Represents the Longitudinal Center of Gravity Control (LCG) of the SAM AUV.

    Attributes:
        l_lcg_l: Length of the LCG structure along the x-axis (m).
        l_lcg_r: Maximum position of the LCG in the x-direction (m).
        m_lcg: Mass of the LCG (kg).
        h_lcg_dim: Height of the LCG structure (m).
        p_OC_O: Vector from CO to C in CO
    """

    def __init__(self, l_lcg_l, l_lcg_r, m_lcg, h_lcg_dim, p_OC_O):
        # Physical parameters
        self.l_lcg_l    = l_lcg_l    # Length of LCG structure (m)
        self.l_lcg_r    = l_lcg_r    # Maximum x-direction position (m)
        self.m_lcg      = m_lcg      # Mass of LCG (kg)
        self.h_lcg_dim  = h_lcg_dim  # Height of LCG structure (m)
        p_CLcgpos_O     = ca.MX(np.array([0.608+self.l_lcg_l/2, 0, 0.130])) # "Beginning" of the LCG in C frame. Mass moves from here
        self.p_OLcgPos_O = ca.MX(p_OC_O) + p_CLcgpos_O # Vector from CO to LCG position 0 in O

        # Motion bounds
        self.x_lcg_min = 0  # Minimum LCG position (m)
        self.x_lcg_max = l_lcg_r  # Maximum LCG position (m)
        self.x_lcg_dot_min = -0.1  # Maximum retraction speed (m/s)
        self.x_lcg_dot_max = 15  # FIXME: This is an estimate. Need to adjust, since the speed is given in mm/s, but we control on percentages right now. Maximum extension speed (m/s)


class Propellers:
    """
    Represents the Propellers (TP) of the SAM AUV.

    Attributes:
        n_p: Number of propellers.
        r_t_p_sh: List of each propeller location on thruster shaft (np.array) relative to the thruster frame (m).
    """

    def __init__(self, n_p, r_t_p_sh):
        # Physical parameters
        self.n_p = n_p  # Number of propellers
        self.r_t_p_sh = r_t_p_sh  # Shaft center locations list

        # RPM bounds
        self.rpm_min = np.zeros(n_p) - 1525  # Min RPM per propeller
        self.rpm_max = np.zeros(n_p) + 1525  # Max RPM per propeller
        self.rpm_dot_min = np.zeros(n_p) - 100  # Max deceleration (RPM/s)
        self.rpm_dot_max = np.zeros(n_p) + 100  # Max acceleration (RPM/s)


# Class Vehicle
class SAM_casadi():
    """
    SAM()
        Integrates all subsystems of the Small and Affordable Maritime AUV.


    Attributes:
        eta: [x, y, z, q0, q1, q2, q3] - Position and quaternion orientation
        nu: [u, v, w, p, q, r] - Body-fixed linear and angular velocities

    Vectors follow Tedrake's monogram:
    https://manipulation.csail.mit.edu/pick.html#monogram
    """
    def __init__(
            self,
            dt=0.02,
            V_current=0,
            beta_current=0,
    ):
        self.dt = dt # Sim time step, necessary for evaluation of the actuator dynamics

        # Constants
        self.p_OC_O = ca.MX(np.array([-0.75, 0, 0.06], float))  # Measurement frame C in CO (O)
        self.D2R = math.pi / 180  # Degrees to radians
        self.rho_w = self.rho = 1026  # Water density (kg/m³)
        self.g = 9.81  # Gravity acceleration (m/s²)

        # Initialize Subsystems:
        self.init_vehicle()
        self.create_model = True
        # Reference values and current
        self.V_c = V_current  # Current water speed
        self.beta_c = beta_current * self.D2R  # Current water direction (rad)

        # Initialize state vectors
        self.nu = np.zeros(6)  # [u, v, w, p, q, r]
        self.eta = np.zeros(7)  # [x, y, z, q0, q1, q2, q3]
        self.eta[3] = 1.0

        # Initialize the AUV model
        self.name = ("SAM")
        self.L = self.ss.l_ss  # length (m)
        self.diam = self.ss.d_ss  # cylinder diameter (m)

        # Hydrodynamics (Fossen 2021, Section 8.4.2)
        self.a = self.L / 2  # semi-axes
        self.b = self.diam / 2

        self.p_OG_O = np.array([0., 0, 0.12], float)  # CG w.r.t. to the CO, we
                                                        # recalculate that in calculate_cg
        self.p_OB_O = np.array([0., 0, 0], float)  # CB w.r.t. to the CO

        # Rigid-body mass matrix expressed in CO
        self.m = self.ss.m_ss + self.vbs.m_vbs + self.lcg.m_lcg
        self.J_total = np.zeros((3,3)) 
        self.MRB = np.zeros((6,6)) 
        self.MA = np.zeros((6,6)) 
        self.M = np.zeros((6,6)) 
        self.Minv = np.zeros((6,6)) 

        # Added moment of inertia in roll: A44 = r44 * Ix
        self.r44 = 0.3

        # Lamb's k-factors
        e = math.sqrt(1 - (self.b / self.a) ** 2)
        alpha_0 = (2 * (1 - e ** 2) / pow(e, 3)) * (0.5 * math.log((1 + e) / (1 - e)) - e)
        beta_0 = 1 / (e ** 2) - (1 - e ** 2) / (2 * pow(e, 3)) * math.log((1 + e) / (1 - e))

        self.k1 = alpha_0 / (2 - alpha_0)
        self.k2 = beta_0 / (2 - beta_0)
        self.k_prime = pow(e, 4) * (beta_0 - alpha_0) / (
                (2 - e ** 2) * (2 * e ** 2 - (2 - e ** 2) * (beta_0 - alpha_0)))

        # Weight and buoyancy
        self.W = self.m * self.g
        self.B = self.W # NOTE: Init buoyancy as dry mass + half the VBS

        # Damping matrix based on Bhat 2021
        # Parameters from smarc_advanced_controllers mpc_inverted_pendulum...

        self.D = np.zeros((6,6))

        # NOTE: These need to be identified properly
        # Damping coefficients
        self.Xuu = 3 #100     # x-damping
        self.Yvv = 50    # y-damping
        self.Zww = 50    # z-damping
        self.Kpp = 40    # Roll damping
        self.Mqq = 200    # Pitch damping
        self.Nrr = 10    # Yaw damping

        # Center of effort -> where the thrust force acts?
        self.x_cp = 0.1
        self.y_cp = 0
        self.z_cp = 0

        # Propeller Coefficients
        self.D_prop = 0.14
        self.Va_coef = 0.944
        self.KT_0 = 0.4566
        self.KQ_0 = 0.0700
        self.KT_max = 0.1798
        self.KQ_max = 0.0312
        self.Ja_max = 0.6632

        self.gamma = 100 # Scaling factor for numerical stability of quaternion differentiation

    def init_vehicle(self):
        """
        Initialize all subsystems based on their respective parameters
        """
        self.ss = SolidStructure(
            l_ss=1.5,
            d_ss=0.19,
            m_ss=14.9,
            p_CSsg_O = np.array([0.74, 0, 0.06]),
            p_OC_O=self.p_OC_O
        )

        self.vbs = VariableBuoyancySystem(
            r_vbs=0.0425,
            l_vbs_l=0.045,
            p_CVbs_O = np.array([0.404, 0, 0.0125]),
            p_OC_O=self.p_OC_O,
            rho_w=self.rho_w
        )

        self.lcg = LongitudinalCenterOfGravityControl(
            l_lcg_l=0.223,
            l_lcg_r=0.06,
            m_lcg=2.6,
            h_lcg_dim=0.08,
            p_OC_O=self.p_OC_O
        )

        self.propellers = Propellers(
            n_p=2,
            r_t_p_sh=[
                np.array([0.03, 0, 0]),
                np.array([0.04, 0, 0])
            ]
        )

    def dynamics(self, export = False):
        """
        Main dynamics function for integrating the complete AUV state.

        Args:
            t: Current time
            x: state space vector with [eta, nu, u]
            u_ref: control inputs as [x_vbs, x_lcg, delta_s, delta_r, rpm1, rpm2]
            export: export the model to acados [bool]. Standard is False

        Returns:
            state_vector_dot: Time derivative of complete state vector
        """
        
        # Create the dynamical model the first time this method is executed
        if self.create_model == True and export == False:
            x_sym = ca.MX.sym('x', 19,1)
            u_ref_sym = ca.MX.sym('u_ref', 6,1)
            eta = x_sym[0:7]
            nu = x_sym[7:13]
            u = x_sym[13:19]

            # Bound_actuators is removed -see SAM for reference

            self.calculate_system_state(nu, eta, u_ref_sym)
            self.calculate_cg()
            self.update_inertias()
            self.calculate_M()
            self.calculate_C()
            self.calculate_D()
            self.calculate_g()
            self.calculate_tau(u_ref_sym)

            nu_dot = self.Minv @ (self.tau - ca.mtimes(self.C,self.nu_r) - ca.mtimes(self.D,self.nu_r) - self.g_vec)
            u_dot = self.actuator_dynamics(u, u_ref_sym)
            eta_dot = self.eta_dynamics(eta, nu)

            x_dot = ca.vertcat(eta_dot, nu_dot, u_dot)
            self.x_dot_sym = ca.Function('x_dot', [x_sym, u_ref_sym], [x_dot])
            self.create_model = False

        # Export the casadi model to acados or for the LQR
        elif export == True:
            x_sym = ca.MX.sym('x', 13,1)
            u_ref_sym = ca.MX.sym('u_ref', 6,1)
            eta = x_sym[0:7]
            nu = x_sym[7:13]

            # Bound_actuators is removed -see SAM for reference

            self.calculate_system_state(nu, eta, u_ref_sym)
            self.calculate_cg()
            self.update_inertias()
            self.calculate_M()
            self.calculate_C()
            self.calculate_D()
            self.calculate_g()
            self.calculate_tau(u_ref_sym)

            nu_dot = self.Minv @ (self.tau - ca.mtimes(self.C,self.nu_r) - ca.mtimes(self.D,self.nu_r) - self.g_vec)
            eta_dot = self.eta_dynamics(eta, nu)

            x_dot = ca.vertcat(eta_dot, nu_dot)
            self.x_dot_sym = ca.Function('x_dot', [x_sym, u_ref_sym], [x_dot])

        #return self.x_dot_sym(x, u_ref) # returns a ca.DM
        return self.x_dot_sym  # returns a casadi MX.function

    # def export_dynamics_model(self):
    #     # Create symbolic state and control variables
    #     x_sym     = ca.MX.sym('x', 19,1)
    #     u_ref_sym = ca.MX.sym('u_ref', 6,1)

    #     # Create symbolic derivative
    #     x_dot_sym = ca.MX.sym('x_dot', 19, 1)
        
    #     # Set up acados model
    #     model = AcadosModel()
    #     model.name = 'SAM_equation_system'
    #     model.x    = x_sym
    #     model.xdot = x_dot_sym
    #     model.u    = u_ref_sym

    #     # Declaration of explicit and implicit expressions
    #     x_dot  = self.dynamics(export=True)    # extract casadi.MX function
    #     f_expl = ca.vertcat(x_dot(x_sym[:13], x_sym[13:]), u_ref_sym)
    #     f_impl = x_dot_sym - f_expl
    #     model.f_expl_expr = f_expl
    #     model.f_impl_expr = f_impl

    #     return model

    def calculate_system_state(self, nu, eta, u_control):
        """
        Extract speeds etc. based on state and control inputs
        """

        # Extract Euler angles
        quat = eta[3:7]
        quat = quat/ca.norm_2(quat)
        self.psi, self.theta, self.phi = quaternion_to_angles_ca(quat) 
        # Relative velocities due to current
        u = nu[0]
        v = nu[1]
        w = nu[2]
        u_c = self.V_c * ca.cos(self.beta_c - self.psi)
        v_c = self.V_c * ca.sin(self.beta_c - self.psi)
        self.nu_c = ca.vertcat(u_c, v_c, 0, 0, 0, 0)
        self.nu_r = nu - self.nu_c

        self.U = ca.sqrt(u ** 2 + v ** 2 + w ** 2)
        self.U_r = ca.norm_2(self.nu_r[:3])

        self.alpha = 0.0
        condition = ca.fabs(self.nu_r[0]) > 1e-6
        self.alpha = ca.if_else(condition, ca.atan2(self.nu_r[2], self.nu_r[0]), self.alpha)

        # Update actuators - u_control is opti_variable
        self.x_vbs = self.calculate_vbs_position(u_control) 
        self.p_OLcg_O = self.calculate_lcg_position(u_control)

        # Update mass
        self.vbs.m_vbs = self.rho_w * np.pi * self.vbs.r_vbs ** 2 * self.x_vbs
        self.m = self.ss.m_ss + self.vbs.m_vbs + self.lcg.m_lcg

    def calculate_cg(self):
        """
        Compute the center of gravity based on VBS and LCG position
        """
        self.p_OG_O = ca.mtimes(self.ss.m_ss / self.m, self.ss.p_OSsg_O) + \
              ca.mtimes(self.vbs.m_vbs / self.m, self.vbs.p_OVbs_O) + \
              ca.mtimes(self.lcg.m_lcg / self.m, self.p_OLcg_O)

    def update_inertias(self):
        """
        Update inertias based on VBS and LCG
        Note: The propellers add more torque rather than momentum by moving.
            The exception would be steering, but that's complex and will change
            in the next iteration of SAM.
        """

        # Solid structure
        # Moment of inertia of a solid elipsoid
        # https://en.wikipedia.org/wiki/List_of_moments_of_inertia
        # with b = c.
        Ix = (2 / 5) * self.ss.m_ss * self.b ** 2  # moment of inertia
        Iy = (1 / 5) * self.ss.m_ss * (self.a ** 2 + self.b ** 2)
        Iz = Iy

        ss_inertias = ca.vertcat(Ix, Iy, Iz)
        J_ss_cg = ca.diag(ss_inertias) # In center of gravity
        S2_p_OSsg_O = skew_symmetric_ca(self.ss.p_OSsg_O) @ skew_symmetric_ca(self.ss.p_OSsg_O)
        J_ss_co = J_ss_cg - self.ss.m_ss * S2_p_OSsg_O


        # VBS
        # Moment of inertia of a solid cylinder
        Ix_vbs = (1/2) * self.vbs.m_vbs * self.vbs.r_vbs**2
        Iy_vbs = (1/12) * self.vbs.m_vbs * (3*self.vbs.r_vbs**2 + self.x_vbs**2)
        Iz_vbs = Iy_vbs

        vbs_inertias = ca.vertcat(Ix_vbs, Iy_vbs, Iz_vbs)
        J_vbs_cg = ca.diag(vbs_inertias)
        S2_r_vbs_cg = skew_symmetric_ca(self.vbs.p_OVbs_O) @ skew_symmetric_ca(self.vbs.p_OVbs_O)
        J_vbs_co = J_vbs_cg - self.vbs.m_vbs * S2_r_vbs_cg


        # LCG
        # Moment of inertia of a solid cylinder
        Ix_lcg = (1/2) * self.lcg.m_lcg * (self.lcg.h_lcg_dim/2)**2
        Iy_lcg = (1/12) * self.lcg.m_lcg* (3*(self.lcg.h_lcg_dim/2)**2 + self.lcg.l_lcg_l**2)
        Iz_lcg = Iy_lcg

        lcg_inertias = ca.vertcat(Ix_lcg, Iy_lcg, Iz_lcg)
        J_lcg_cg = ca.diag(lcg_inertias)
        S2_r_lcg_cg = skew_symmetric_ca(self.p_OLcg_O) @ skew_symmetric_ca(self.p_OLcg_O)
        J_lcg_co = J_lcg_cg - self.lcg.m_lcg * S2_r_lcg_cg

        self.J_total = J_ss_co + J_vbs_co + J_lcg_co

    def calculate_M(self):
        """
        Calculated the mass matrix M
        """

        # Rigid-body mass matrix expressed in CO
        diagonal_mass = ca.vertcat(self.m, self.m, self.m)
        m_diag = ca.diag(diagonal_mass)

        # Rigid-body mass matrix with total inertia in CO
        MRB_CO = ca.diagcat(m_diag, self.J_total)
        self.MRB = MRB_CO

        # Added moment of inertia in roll: A44 = r44 * Ix
        MA_44 = self.r44 * self.J_total[0,0]

        # Added mass system matrix expressed in the CO
        diagonal_added_mass = ca.vertcat(self.m * self.k1,
                                        self.m * self.k2,
                                        self.m * self.k2,
                                        MA_44,
                                        self.k_prime * self.J_total[1,1],
                                        self.k_prime * self.J_total[1,1])
        self.MA = ca.diag(diagonal_added_mass)

        # Mass matrix including added mass
        self.M = self.MRB + self.MA
        self.Minv = ca.inv(self.M)

    def calculate_C(self):
        """
        Calculate Corriolis Matrix
        """
        CRB = m2c_ca(self.MRB, self.nu_r)
        CA = m2c_ca(self.MA, self.nu_r)

        CA[4, 0] = 0
        CA[0, 4] = 0
        CA[4, 2] = 0
        CA[2, 4] = 0
        CA[5, 0] = 0
        CA[0, 5] = 0
        CA[5, 1] = 0
        CA[1, 5] = 0

        self.C = CRB + CA

    def calculate_D(self):
        """
        Calculate damping
        """
        # Init CasADi matrix
        self.D = ca.MX.zeros(6, 6)

        # Nonlinear damping
        self.D[0,0] = self.Xuu * ca.fabs(self.nu_r[0])
        self.D[1,1] = self.Yvv * ca.fabs(self.nu_r[1])
        self.D[2,2] = self.Zww * ca.fabs(self.nu_r[2])
        self.D[3,3] = self.Kpp * ca.fabs(self.nu_r[3])
        self.D[4,4] = self.Mqq * ca.fabs(self.nu_r[4])
        self.D[5,5] = self.Nrr * ca.fabs(self.nu_r[5])

        # Cross couplings
        self.D[4,0] = self.z_cp  * self.Xuu * ca.fabs(self.nu_r[0])
        self.D[5,0] = -self.y_cp * self.Xuu * ca.fabs(self.nu_r[0])
        self.D[3,1] = -self.z_cp * self.Yvv * ca.fabs(self.nu_r[1])
        self.D[5,1] = self.x_cp  * self.Yvv * ca.fabs(self.nu_r[1])
        self.D[3,2] = self.y_cp  * self.Zww * ca.fabs(self.nu_r[2])
        self.D[4,2] = -self.x_cp * self.Zww * ca.fabs(self.nu_r[2])

    def calculate_g(self):
        """
        Calculate gravity vector
        """
        self.W = self.m * self.g
        self.g_vec = gvect_ca(self.W, self.B, self.theta, self.phi, self.p_OG_O, self.p_OB_O)

    def calculate_tau(self, u):
        """
        All external forces

        Note: We use a non-diagonal damping matrix, that takes forceLiftDrag
            and the crossFlowDrag, i.e. the cross-couplings in the damping already
            into account. If you use a diagonal matrix, you have to add these
            forces here, as shown in the commented code below:

            tau_liftdrag = forceLiftDrag(self.diam, self.S, self.CD_0, self.alpha, self.nu)
            tau_crossflow = crossFlowDrag(self.L, self.diam, self.diam, self.nu_r)
        """
        tau_prop = self.calculate_propeller_force(u)
        self.tau = tau_prop

    def calculate_propeller_force(self, u):
        """
        Calculate force and torque of the propellers
        u: control inputs as [x_vbs, x_lcg, delta_s, delta_r, rpm1, rpm2]
        Azimuth Thrusters: Fossen 2021, ch.9.4.2
        """
        delta_s = u[2]
        delta_r = u[3]
        n_rpm = u[4:]

        # Compute propeller forces
        C_T2C = calculate_dcm_ca(order=[2, 3], angles=[delta_s, delta_r])

        n_rps = n_rpm / 60   
        Va = self.Va_coef * self.U

        tau_prop = ca.MX.zeros(6)  # Initialize tau_prop as a CasADi MX vector
        for i in range(n_rpm.size1()):
            X_prop_i = ca.if_else(ca.sign(n_rps[i]) > 0,
                                self.rho * (self.D_prop**4) * (self.KT_0 * ca.fabs(n_rps[i]) * n_rps[i] +
                                    (self.KT_max - self.KT_0) / self.Ja_max * (Va / self.D_prop) * ca.fabs(n_rps[i])),

                                self.rho * (self.D_prop**4) * (self.KT_0 * ca.fabs(n_rps[i]) * n_rps[i]) / 10)
            
            K_prop_i = ca.if_else(ca.sign(n_rps[i]) > 0,
                                self.rho * (self.D_prop**5) * (self.KQ_0 * ca.fabs(n_rps[i]) * n_rps[i] +
                                    (self.KQ_max - self.KQ_0) / self.Ja_max * (Va / self.D_prop) * ca.fabs(n_rps[i])),
                                    
                                self.rho * (self.D_prop ** 5) * self.KQ_0 * ca.fabs(n_rps[i]) * n_rps[i] / 10)

            F_prop_b = ca.mtimes(C_T2C, ca.vertcat(X_prop_i, 0, 0))
            r_prop_i = ca.mtimes(C_T2C, self.propellers.r_t_p_sh[i]) - self.p_OC_O
            M_prop_i = ca.cross(r_prop_i, F_prop_b) + ca.vertcat((-1)**i * K_prop_i, 0, 0)  # the -1 is because we have counter rotating
                                    # propellers that are supposed to cancel out the propeller induced
                                    # momentum
            tau_prop_i = ca.vertcat(F_prop_b, M_prop_i)
            tau_prop += tau_prop_i

        return tau_prop

    def calculate_vbs_position(self, u):
        """
        Control input is scaled between 0 and 100. This converts it into the actual position
        s.t. we can calculate the amount of water in the VBS.
        u: control inputs as [x_vbs, x_lcg, delta_s, delta_r, rpm1, rpm2]
        """
        x_vbs = (u[0]/100) * self.vbs.l_vbs_l
        return x_vbs

    def calculate_lcg_position(self, u):
        """
        Calculate the position of the LCG based on control input. The control
        input is scaled between 0 and 100. This function converts it to the
        actual physical location.
        """
        index0 = ca.mtimes(u[1]/100, self.lcg.l_lcg_l)
        index1 = 0
        index2 = 0

        p_LcgPos_LcgO = ca.vertcat(index0, index1, index2)# Position of the LCG w.r.t fixed LCG point
        p_OLcg_O = self.lcg.p_OLcgPos_O + p_LcgPos_LcgO

        return ca.MX(p_OLcg_O)

    def eta_dynamics(self, eta, nu):
        """
        Computes the time derivative of position and quaternion orientation.

        Args:
            eta: [x, y, z, q0, q1, q2, q3] - Position and quaternion
            nu: [u, v, w, p, q, r] - Body-fixed velocities

        Returns:
            eta_dot: [ẋ, ẏ, ż, q̇0, q̇1, q̇2, q̇3]
        """
        # Extract position and quaternion
        q = eta[3:7]  # [q0, q1, q2, q3] where q0 is scalar part
        q = q/ca.norm_2(q)

        # Convert quaternion to DCM for position kinematics
        C = quaternion_to_dcm_ca(q)

        # Position dynamics: ṗ = C * v
        pos_dot = C @ nu[0:3]

        ## From Fossen 2021, eq. 2.78:
        om = nu[3:6]  # Angular velocity
        q0 = q[0]
        q1 = q[1]
        q2 = q[2]
        q3 = q[3]

        T_q_n_b = 0.5 * ca.vertcat(ca.horzcat(-q1, -q2, -q3),
                                   ca.horzcat(q0, -q3, q2),
                                   ca.horzcat(q3, q0, -q1),
                                   ca.horzcat(-q2, q1, q0)
                                   )
        
        q_dot = ca.mtimes(T_q_n_b, om) + self.gamma / 2 * (1 - ca.mtimes(q.T, q)) * q
        return ca.vertcat(pos_dot, q_dot)

    def actuator_dynamics(self, u_cur, u_ref):
        """
        Compute the actuator dynamics.
        delta_X and rpmX are assumed to be instantaneous

        u: control inputs as [x_vbs, x_lcg, delta_s, delta_r, rpm1, rpm2]
        """

        u_dot = ca.MX.zeros(6)

        u_dot = (u_ref - u_cur)/self.dt

        u_dot[0] = ca.if_else(ca.fabs(u_dot[0]) > self.vbs.x_vbs_dot_max,
                          self.vbs.x_vbs_dot_max * ca.sign(u_dot[0]),
                          u_dot[0])
        u_dot[1] = ca.if_else(ca.fabs(u_dot[1]) > self.lcg.x_lcg_dot_max,
                          self.lcg.x_lcg_dot_max * ca.sign(u_dot[1]),
                          u_dot[1])
        return u_dot


