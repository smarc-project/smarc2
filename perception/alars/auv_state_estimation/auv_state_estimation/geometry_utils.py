import numpy as np

def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi

def residual_z(a, b):
    # assumes measurement layout [u, v, alpha, ...]
    r = np.asarray(a).reshape(-1) - np.asarray(b).reshape(-1)
    r[2] = yaw_residual_mod_pi(np.asarray(a).reshape(-1)[2], np.asarray(b).reshape(-1)[2])
    return r

def yaw_residual_mod_pi(meas, pred):
    d0 = wrap(meas - pred)
    d1 = wrap((meas + np.pi) - pred)
    return d0 if abs(d0) < abs(d1) else d1  
