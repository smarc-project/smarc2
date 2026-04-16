#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Author: Ozer Ozkahraman (ozkahramanozer@gmail.com)
# Date: 2018-07-10

from __future__ import print_function
import math
import numpy as np

RADTODEG = 360 / (np.pi * 2)
DEGTORAD = 1/RADTODEG

##############################################################
#  VECTOR STUFF
##############################################################

def vec_len(vec):
    """
    returns the length of the vector
    vec can be (N,d), the return will be (N,)
    """
    vec = np.array(np.atleast_2d(vec))
    N,d = vec.shape
    if N>1:
        return np.linalg.norm(vec, axis=1)
    else:
        return np.linalg.norm(vec)


def vec_normalize(vec):
    """
    returns the length and 1-long version of the given vector
    """
    vec = np.array(vec)
    vec2 = np.atleast_2d(vec)
    # one less function call here
    norm = np.linalg.norm(vec2, axis=1)
    # atleast2d stuff so that vec = (N,k) and divider=(N,l) can be divided like this easily
    unit = vec/(np.atleast_2d(norm).T)

    if len(norm) == 1:
        norm = norm[0]
        unit = unit[0]

    assert unit.shape == vec.shape, "unit shape: %r, given vec shape: %r" %(unit.shape, vec.shape)
    return norm, unit


def vec_limit_len(vec, max_len):
    """
    makes sure the vector has at most max_len length
    """
    norm, vec = vec_normalize(vec)
    return vec*min(max_len, norm)


def vec_set_len(vec, l):
    """
    sets the length of the vector
    """
    norm, vec = vec_normalize(vec)
    return vec*l


def project_vec(X,Y):
    """
    project a vector X onto a vector Y
    literally find the closest point on (0,0)-Y to X, return it

    X can be (N,2) or (N,3)
    """
    X = np.array(X)
    Y = np.array(Y)

    div = X.dot(Y)/Y.dot(Y)
    res = np.outer(div, Y)

    if X.shape == (2,) or X.shape == (3,):
        return res[0]

    return res


def vec2_rotate(vec2, rad):
    """
    rotate 2D vec rad radians around the origin

    vec2 and rad can be (N,2), list of vectors, and (N,1), list of radians
    all of the given vectors will be rotated.
    """
    vec2 = np.array(np.atleast_2d(vec2), dtype='float')
    rad = np.array(rad, dtype='float')

    x1s = vec2[:,0]
    y1s = vec2[:,1]

    x2s = np.cos(rad)*x1s - np.sin(rad)*y1s
    y2s = np.sin(rad)*x1s + np.cos(rad)*y1s

    res = np.zeros_like(vec2)
    res[:,0] = x2s
    res[:,1] = y2s

    N,_ = vec2.shape
    if N == 1:
        return res[0]
    else:
        return res


def vec2_directed_angle(v1, v2):
    """
    returns the shortest angle from v1 to v2 in radians.
    v1 + angle = v2.

    positive value means ccw rotation from v1 to v2.
    negative value means cw.

    v1, v2 can be (N,2)
    """
    v1 = np.array(np.atleast_2d(v1))
    v2 = np.array(np.atleast_2d(v2))
    assert v1.shape == v2.shape

    x1s = v1[:,0]
    x2s = v2[:,0]
    y1s = v1[:,1]
    y2s = v2[:,1]

    dots = x1s*x2s + y1s*y2s
    dets = x1s*y2s - y1s*x2s

    angles = np.arctan2(dets,dots)

    N,_ = v1.shape
    if N == 1:
        return angles[0]
    else:
        return angles
