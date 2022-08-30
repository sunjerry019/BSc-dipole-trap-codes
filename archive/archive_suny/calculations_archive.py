#!/usr/bin/env python3

import numpy as np

def transform_matrix_angle(axis: np.ndarray, degrees: float) -> np.ndarray:
    """Produce a transformation matrix to transform from one coordinate system to another (Beam 1 vs Beam 2).
    Use the inverse to do a back-transformation

    Reference: https://en.wikipedia.org/wiki/Transformation_matrix#Rotation_2

    To be applied to a (1x3) row vector. r' = rT. Should be extensible to (nx3)

    Args:
        degrees (float): Angle to rotate along the x-z plane in degrees

    Returns:
        np.ndarray: Transformation matrix
    """

    # unit vector representing the rotation axis
    unit_axis = axis.flatten()
    unit_axis = unit_axis / np.linalg.norm(unit_axis)
    l,m,n = unit_axis[0], unit_axis[1], unit_axis[2]

    angle = np.deg2rad(degrees)

    cos  = np.cos(angle, dtype = np.float64)
    cosp = (1 - cos)
    sin  = np.sin(angle, dtype = np.float64)

    # without .T, it is for r' = Tr with r as a column vector
    ret = np.array([
        [l*l*cosp+cos  , m*l*cosp-n*sin, n*l*cosp+m*sin],
        [l*m*cosp+n*sin, m*m*cosp+cos  , n*m*cosp-l*sin],
        [l*n*cosp*m*sin, m*n*cosp+l*sin, n*n*cosp+cos  ]
    ]).T

    return ret

xps = [np.array([3, 0, 0])]

x = np.array([0, 0, 3])
T = transform_matrix_angle(axis = np.array([0,1,0]), degrees = 90)
xp = np.matmul(x, T)

xps.append(xp)

print(x, xp)


### Pure Quarternion implementation

import quaternion

def get_quaternion_angle(axis: np.ndarray, degrees: float) -> np.ndarray: 
    halfangle = np.deg2rad(degrees)/2

    unit_axis = axis.flatten()
    unit_axis = unit_axis / np.linalg.norm(unit_axis)

    ax = np.sin(halfangle) * unit_axis
    q_arr = np.concatenate(([np.cos(halfangle)], ax)).tolist()
    q  = np.quaternion(*q_arr)

    return q

q  = get_quaternion_angle(axis = np.array([0,1,0]), degrees = 90)

x  = np.quaternion(0, 0, 0, 3)
xp = q*x*q.conjugate()

xps.append(np.array([xp.x, xp.y, xp.z]))

print(x, xp)