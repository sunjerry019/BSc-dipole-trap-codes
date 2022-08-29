#!/usr/bin/env python3

import __init__
import os

import cv2
import numpy as np

import laserbeamsize as lbs

from beamprofilerData import BeamprofilerImageData

import matplotlib.pyplot as plt

pixel_um = 5.2

img_data_dir = os.path.join(__init__.base_dir, "2022-08-05_High Frequency Painting")
image_fp = os.path.join(img_data_dir, "3.4MHz_1.250.0V_10MHzModulation.csv")

image = BeamprofilerImageData(datafile = image_fp)

# https://github.com/koopaduo2/Beam-GUI/blob/c6daf0720140032e5ee60336d4a44016ad4c7afd/beam_gui.py#L406
MOM = cv2.moments(image.DATA)
if MOM['m00'] != 0:
    centroid_x = MOM['m10']/MOM['m00']
    centroid_y = MOM['m01']/MOM['m00']
    #note 1 pixel has physical dimension: pixel_um * pixel_um (= 1.55 um (micron) * 1.55 um for Raspi HQ Camera module)
    #With no scaling (lens) the physical beam widths are then d4x (px) * 1.55 um, d4y (px) * 1.55 um
    d4x = pixel_um*4*np.sqrt(abs(MOM['m20']/MOM['m00'] - centroid_x**2))
    d4y = pixel_um*4*np.sqrt(abs(MOM['m02']/MOM['m00'] - centroid_y**2))
else:
    d4x = 0
    d4y = 0

print(d4x/2, d4y/2)

x, y, dx, dy, phi = lbs.beam_size(image.DATA)
print("The center of the beam ellipse is at (%.0f, %.0f)" % (x,y))
print("The ellipse radius (closest to horizontal) is {} um".format(dx * pixel_um/2))
print("The ellipse radius (closest to   vertical) is {} um".format(dy * pixel_um/2))
print("The ellipse is rotated %.0f° ccw from horizontal" % (phi*180/3.1416))

lbs.beam_size_plot(image.DATA)
plt.show()