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


def vec3_to_yaw_pitch(vec3):
    """
    given a direction vector, returns the yaw and pitch angles in radians.
    ignores the length of the vector
    vec3 = (x,y,z)
    """
    x,y,z = vec3
    if z == 0:
        pitch = 0
    else:
        pitch = np.arctan2(z, math.sqrt(x**2 + y**2) )

    if x == 0 and y == 0:
        yaw = 0
    else:
        yaw = vec2_directed_angle([1,0],[x,y])

    return yaw, pitch

def vec2_toroidal_vec(A, B, xmax, ymax):
    """
    Given a toroidal space described by -xmax < x < xmax, -ymax < 0 < ymax.

    This function returns the imaginary points that would affect another point A
    around the torus.
    This is done by duplicating B 8 times by adding/subbing the ranges
    so that the 'other side's of B exist and create forces on A as if they
    were going around the torus.

    assumes the sapce is [0,0] centered and symmetric. The bounds are then
    [-xmax, xmax], [-ymax,ymax].
    """
    A = np.array(A, dtype='float64')
    B = np.array(B, dtype='float64')

    # we also want 'only change x' type
    # interactions too!
    x_range = [xmax, -xmax, 0]
    y_range = [ymax, -ymax, 0]

    vecs = []
    for x in x_range:
        for y in y_range:
            # this is the 'around the torus'
            # version of B
            BB = B + [x,y]
            vec = BB-A
            vecs += [vec]
    return np.array(vecs)






#########################################################################
# GEOMETRIC CONSTRUCTS
#########################################################################

def euclid_distance(p1, p2):
    """
    returns the distance between p1 and p2.
    p1,p2 can be (N,2) or (N,3) or just (x,y,z) or (x,y)
    """
    p1 = np.array(p1)
    p2 = np.array(p2)

    v = p2-p1
    return vec_len(v)


def line_slope_intercept(A,B):
    """
    return the slope and x-intercept of the line that
    goes through points A and B.
    """
    Ax, Ay = A
    Bx, By = B
    m = (Ay-By) / (Ax-Bx)
    b = Ay - Ax*m
    return m,b

def perp_line(src_m, p):
    """
    returns the slope and intercept of the line that goes
    through p. The returned line will be perpendicular to src_m.
    src_m is the slope of a line, p is a point on that line.
    """
    m = -1/src_m
    x,y = p
    b = y - x*m
    return m,b


#http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/19550879#19550879
#taken from above
def line_intersect(l1, l2):
    """
    return the point of intersection for the two lines l1 and l2.
    l1 = [p0,p1]
    l2 = [p2,p3]
    pX = (x,y)
    """
    p0,p1 = l1
    p2,p3 = l2

    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = s10_x * s32_y - s32_x * s10_y

    if denom == 0:
        raise ValueError('LINES COLLINEAR! '+str(l1)+' '+str(l2))

    denom_is_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]

    s_numer = s10_x * s02_y - s10_y * s02_x

    if (s_numer < 0) == denom_is_positive : return None # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x

    if (t_numer < 0) == denom_is_positive : return None # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision


    # collision detected

    t = t_numer / denom

    intersection_point = [ p0[0] + (t * s10_x), p0[1] + (t * s10_y) ]
    return intersection_point


def circle_intersection(circle1, circle2):
    """
    return the possible intersection points between two
    circles (x,y,r)
    """
    x1,y1,r1 = circle1
    x2,y2,r2 = circle2
    # http://stackoverflow.com/a/3349134/798588
    dx,dy = x2-x1,y2-y1
    d = np.sqrt(dx*dx+dy*dy)
    if d > r1+r2:
        return None # no solutions, the circles are separate
    if d < abs(r1-r2):
        return None # no solutions because one circle is contained within the other
    if d == 0 and r1 == r2:
        return None # circles are coincident and there are an infinite number of solutions

    a = (r1*r1-r2*r2+d*d)/(2*d)
    h = np.sqrt(r1*r1-a*a)
    xm = x1 + a*dx/d
    ym = y1 + a*dy/d
    xs1 = xm + h*dy/d
    xs2 = xm - h*dy/d
    ys1 = ym - h*dx/d
    ys2 = ym + h*dx/d

    return (xs1,ys1),(xs2,ys2)


def point_in_poly(pts, poly):
    """
    returns True if 'pt' is inside the poly.
    poly is a list of points in ccw order.
    pt can be a single [x,y] or in shape (N,2)

    this function will choose to use masking or looping
    depending on N. If N > 20, it will use masking, otherwise
    it will use a loop. This decision was made on a mobile i7
    """

    if len(pts) > 20:
        return points_in_poly(pts, poly)
    else:
        #prepare stuff
        poly = np.array(poly)
        pts = np.atleast_2d(pts)
        nvert = poly.shape[0]
        vertx = poly[:,0]
        verty = poly[:,1]
        cs = []
        for pt in pts:
            testx = pt[0]
            testy = pt[1]

            #https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
            # the following part is taken from above
            # MAGIC !!
            i = 0
            j = nvert-1
            c = False
            while i < nvert:
                #body
                if ((verty[i] > testy) != (verty[j] > testy)):
                    if (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]):
                        c = not c
                #/body
                j = i
                i += 1
            cs.append(c)
        if len(cs) == 1:
            return cs[0]
        else:
            return cs

def points_in_poly(pts, poly):
    #prepare stuff
    poly = np.array(poly)
    pts = np.atleast_2d(pts)
    nvert = poly.shape[0]
    vertx = poly[:,0]
    verty = poly[:,1]
    testx = pts[:,0]
    testy = pts[:,1]
    N = len(pts)


    #https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
    # the following part is taken from above
    # then modified to work on a list of points instead of just one
    # MAGIC !!
    i = 0
    j = nvert-1
    c = False
    c = np.array([False]*N)
    while i < nvert:
        #body
        testy_smaller = ((verty[i] > testy) != (verty[j] > testy))
        testx_smaller = (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i])
        #  if ((verty[i] > testy) != (verty[j] > testy)):
            #  if (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]):
        # this mask is a vectorized version of the two if statements above
        mask = np.logical_and(testy_smaller, testx_smaller)
        # OP |  1   0    = mask
        #    |----------
        #  1 |  0   1
        #  0 |  1   0
        #  ^= c
        # this is the truth table we want out of the mask and c
        # the first column is when the two ifs are true, where c is inverted
        # second column is when either if is false, leaving c as is
        # obvioulsy this OP is XOR
        #  c = not c
        np.logical_xor(c, mask, out=c)
        #/body
        j = i
        i += 1

    if N == 1:
        return c[0]
    else:
        return c


def distance_to_line_segment(A,B,p, comparison=False):
    """
    returns the shortest distance from p to the line segment A-B.
    if p is 'inside' the line segment, this is the length of perpendicular
    line segment from A-B to p. if p is 'outside' then the distance is the
    distance between p and A or B, whichever is closer.

    if comparison is True, the actual distance is not returned.
    Instead, a comparable measure is returned.
    """
    x1,y1 = A
    x2,y2 = B
    x3,y3 = p


    #http://stackoverflow.com/a/2233538
    #taken from above
    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    # Note: If the actual distance does not matter,
    # if you only want to compare what this function
    # returns to other results of this function, you
    # can just return the squared distance instead
    # (i.e. remove the sqrt) to gain a little performance

    if comparison:
        return dx*dx+dy*dy
    else:
        dist = np.sqrt(dx*dx + dy*dy)
        return dist


def trace_line_segment(p1,p2,ratio):
    """
    return a point that is on the line segment p1-p2,
    at some ratio of the way. ratio is (0,1]
    """
    L = euclid_distance(p1,p2)
    if L < 1e-15:
        return (p1[0], p1[1])
    l = ratio * L
    a = (p2[0]-p1[0]) * (l/L) + p1[0]
    b = (p2[1]-p1[1]) * (l/L) + p1[1]
    return (a,b)


def project_point_to_plane(P, A, n):
    """
    project a given point P to the closest point on the plane.
    A is a point on said plane and n is its normal vector
    P can be (N,3)

    returns the projected point and the distance of the point to the plane
    if distance is negative, then P is on the 'wrong' side of the plane.
    'wrong' meaning the point is not where the normal is pointing towards
    """

    P = np.array(P)
    A = np.array(A)
    n = np.array(n)

    v = P - A
    dist = np.dot(v,n)
    projected = P - np.outer(dist, n)
    if P.shape == (3,):
        return projected[0], dist

    return projected, dist


def create_cage(pts):
    """
    given a list of (N,3) points, returns the edges of the convex hull
    """
    # triangulate the points and generate a convex hull out of it
    # for well-formed spherical-formations, this convex hull is convex and approximates
    # the sphere.
    pts = np.array(pts)
    try:
        # import here since nothing else in the file uses this, and scipy is a huge
        # dependency thats not needed for _every_ project that needs geometry...
        from scipy.spatial import Delaunay
        tris = Delaunay(pts)
    except:
        # if can't triangulate, the vertices must be degenerate, so no cage.
        return None
    # hull is made of triangle edges in terms of indices for self._pos
    hull = tris.convex_hull

    edges = {}
    for triangle in hull:
        # for each triangle, we want to know the edge lengths
        # make the triangle a loop by adding the first vertex at the end
        poly = list(triangle) + [triangle[0]]
        for i in range(1, len(poly)):
            i1 = poly[i-1]
            i2 = poly[i]
            v1 = pts[i1]
            v2 = pts[i2]
            # i only want unique edges, dont give me '0:2 and 2:0' BS.
            if i1 > i2:
                edge_key = str(i1)+':'+str(i2)
            else:
                edge_key = str(i2)+':'+str(i1)
            edges[edge_key] = (v1,v2)

    return np.array(list(edges.values()))


def scale_range(values, new_min, new_max, org_min=None, org_max=None):
    """
    given a list of values, they will be scaled so that the minimum and
    maximum of the data is new_min and new_max. if org_x's are given
    then the data will be scaled to match org's to new's
    """
    if org_min is None:
        org_min = np.min(values)
    if org_max is None:
        org_max = np.max(values)
    org_range = org_max - org_min
    new_range = new_max - new_min
    values = np.array(values)
    ret = (((values - org_min) * new_range) / org_range) + new_min
    if ret.shape == (1,):
        return ret[0]
    return ret



########################################################################

# SPHERICAL STUFF

# Coordinate systems: x,y,z -> right-handed
#                     r,theta,phi or r,u,v -> sphere of radius r, r>=0
#                                             phi = angle from x to y, 'yaw', -pi < phi <= pi
#                                             theta = angle from z, 'pitch' for a vehicle that
#                                                     is looking towards (0,0,1)
#                                                     -pi/2 < theta < pi/2

########################################################################

def xyz_to_uvr(p):
    """
    convert cartesian point p=(x,y,z) to
    spherical coordinates (u,v,r)
    p can be (N,3), result will be (N,3)
    sphere is centered on origin
    does not limit rotations and such
    """
    p = np.array(p)
    p2 = np.atleast_2d(p)
    r = vec_len(p2)
    x = p2[:,0]
    y = p2[:,1]
    z = p2[:,2]
    u = np.arccos(z/r)
    v = np.arctan2(y,x)
    res = np.vstack( (u,v,r) ).T

    # return 1d if input was 1d
    if p.shape == (3,):
        return res[0]

    return res


def uvr_to_xyz(p):
    """
    convert a spherical point p=(u,v,r) to
    cartesian (x,y,z)
    p can be (N,3), result will be (N,3)
    does not limit rotations and such
    """
    p = np.array(p)
    p2 = np.atleast_2d(p)
    u = p2[:,0]
    v = p2[:,1]
    r = p2[:,2]
    x = r*np.sin(u)*np.cos(v)
    y = r*np.sin(u)*np.sin(v)
    z = r*np.cos(u)
    res = np.vstack((x,y,z)).T

    # return 1d if input was 1d
    if p.shape == (3,):
        return res[0]

    return res


if __name__=='__main__':
    print('TESTING GEOMETRY FUNCTIONS')

    assert vec_len([0,0]) == 0
    assert vec_len([1,0]) == 1
    assert vec_len([1,0,0]) == 1
    assert all(vec_len([[1,0,0],[0,0,1]]) == [1,1])
    print('vec_len ok')

    n, v = vec_normalize([0,1])
    assert all([ n==1, all(v==[0,1]) ])
    n, v = vec_normalize([1,1])
    assert all([ n==np.sqrt(2), all(v==np.array([1,1])/np.sqrt(2)) ])
    n, v = vec_normalize([1,1,1])
    assert all([ n==np.sqrt(3), all(v==np.array([1,1,1])/np.sqrt(3)) ])
    print('vec_normalize ok')


    assert all( vec_limit_len([0,5],1)==np.array([0,1]) )
    print('vec_limit_len ok')

    assert all( project_vec( [1,0], [0,1] ) == [0,0] )
    assert all( project_vec( [1,0], [1,1] ) == [0.5,0.5] )
    print('project_vec ok')

    assert all( vec2_rotate( [1,0], np.pi ) == [-1,0] )
    assert sum(sum(( vec2_rotate( [[1,0], [-1,0]], [np.pi, np.pi/2] ) == [[-1,0], [0,-1]] )))==4
    print('vec2_rotate ok')

    assert vec2_directed_angle( [1,0], [0,1] ) == np.pi/2
    assert all(vec2_directed_angle( [[1,0], [1,1]], [[0,1], [-1,-1]] ) == [np.pi/2, np.pi])
    print('vec2_directed_angle ok')

    y,p = vec3_to_yaw_pitch([0, 0, 1])
    assert all([ y==0, p==np.pi/2 ])
    y,p = vec3_to_yaw_pitch([1, 0, 1])
    assert all([ y==0, p==np.pi/4 ])
    y,p = vec3_to_yaw_pitch([1,1,1])
    # the value for p is a little wonky
    assert all([ y==np.pi/4, p-(1/np.sqrt(2)) < 0.0000001])
    print('vec3_to_yaw_pitch ok')

    assert euclid_distance( [0,0], [1,0] ) == 1
    assert all( euclid_distance( [[0,0], [1,0]], [[5,0], [1,1]] ) == [5,1] )
    assert all( euclid_distance( [[0,0,1], [1,0,1]], [[5,0,1], [1,1,1]] ) == [5,1] )
    print('euclid_distance ok')

    assert all( line_slope_intercept( [0,0], [1,1] ) == np.array([1,0]) )
    print('line_slope_intercept ok')

    assert all( perp_line( 1, [5,5] ) == np.array([-1, 10]) )
    print('perp_line ok')

    assert all (line_intersect( [[-1,-1], [1,1]], [[1,-1], [-1,1]] ) == np.array([0,0]))
    print('line_intersect ok')

    assert point_in_poly( [0.5,0.5], [[0,0], [1,0], [1,1], [0,1]] ) == True
    print('point_in_poly ok')


    poly = [[0.1,0.3], [1.4,0.1], [1.2,1.2], [0.1,1.1]]
    N = 1000
    pts = (np.random.rand(N,2)*2) - 1

    import time
    res_single = []
    res_vec = []

    t0 = time.time()
    for pt in pts:
        res_single.append(point_in_poly(pt, poly))
    t1 = time.time()
    single = t1-t0

    t0 = time.time()
    res_vec = points_in_poly(pts, poly)
    t1 = time.time()
    vec = t1-t0

    assert all(res_single == res_vec)
    print('points_in_poly ok, speedup:' , int(single/vec), 'times over 1k points')


    assert distance_to_line_segment([0,0], [1,1], [0.5,0.5]) == 0
    assert distance_to_line_segment([0,0], [1,1], [2,2]) == np.sqrt(2)
    assert distance_to_line_segment([0,0], [1,1], [1,0]) == euclid_distance([1,0], [0.5,0.5])
    print('distance_to_line_segment ok')


    assert all( trace_line_segment([0,1], [0,11], 0.1) == np.array([0,2]) )
    print('trace_line_segment ok')

    assert all(xyz_to_uvr((1,0,0)) == [np.pi/2,0.,1])
    assert all(xyz_to_uvr((0,1,0)) == [np.pi/2, np.pi/2,1])
    assert all(xyz_to_uvr((0,0,1)) == [0.,0.,1])
    print('xyz_to_uvr ok')

    zero = 1e-15
    # zero used here because of float errors
    assert all( np.abs(uvr_to_xyz((np.pi/2,0,1)) - [1.,0.,0.]) <= [0,0,zero] )
    assert all( np.abs(uvr_to_xyz((np.pi/2,np.pi/2,1)) - [0.,1.,0.]) <= [zero,zero,zero] )
    assert all( np.abs(uvr_to_xyz((0,0,1)) - [0.,0.,1.]) <= [0,0,0] )
    print('uvr to xyz ok')

    proj, dist = project_point_to_plane([0,0,10], (0,0,1), (0,0,1))
    assert all(proj==(0,0,1)) and dist==9
    proj, dist = project_point_to_plane([0,0,10], (0,0,1), (0,0,-1))
    assert all(proj==(0,0,1)) and dist==-9
    print('project_point_to_plane ok')

    X = np.random.random((20,2))
    #  X = [1,2]
    Y = [0,1]

    X = np.array(X)
    Y = np.array(Y)

    div = X.dot(Y)/Y.dot(Y)
    res = np.outer(div, Y)

