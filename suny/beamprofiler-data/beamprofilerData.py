#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage

class BeamprofilerImageData():
    def __init__(self, datafile: str) -> None:
        self.DATA = np.loadtxt(datafile, delimiter = ',')

    def getAngleForRotation(self) -> float:
        # To obtain the angle, we use https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/#2-Raw-image-moments
        # Write something about PCA and moments and the equation
        
        cov = BeamprofilerImageData.moments_cov(self.DATA)
        eigvals, eigvecs = np.linalg.eig(cov)

        largest_eig_idx = np.argmax(eigvals)
        # We only look at the eigenvector with the largest eigenvalue
        _x, _y = eigvecs[largest_eig_idx]
        theta = np.rad2deg(np.arctan(_x/_y)) + 90 + 2 # small adjustment

        return theta

    def rotateImage(self, degrees: float) -> None:
        self.ORIGINAL_DATA = self.DATA
        self.DATA = scipy.ndimage.rotate(self.DATA, angle = degrees)
    
    def displayImage(self) -> None:
        fig, ax = plt.subplots()
        ax.imshow(self.DATA)
        plt.show()

    ## AUXILLARY METHODS
    @staticmethod
    def raw_moment(data: np.ndarray, i_order: int, j_order: int) -> np.ndarray:
        # CITE: https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/#2-Raw-image-moments
        nrows, ncols = data.shape
        y_indices, x_indices = np.mgrid[:nrows, :ncols]
        return (data * x_indices**i_order * y_indices**j_order).sum()
    
    @staticmethod
    def moments_cov(data: np.ndarray) -> np.ndarray:
        data_sum = data.sum()
        m10 = BeamprofilerImageData.raw_moment(data, 1, 0)
        m01 = BeamprofilerImageData.raw_moment(data, 0, 1)
        x_centroid = m10 / data_sum
        y_centroid = m01 / data_sum
        u11 = (BeamprofilerImageData.raw_moment(data, 1, 1) - x_centroid * m01) / data_sum
        u20 = (BeamprofilerImageData.raw_moment(data, 2, 0) - x_centroid * m10) / data_sum
        u02 = (BeamprofilerImageData.raw_moment(data, 0, 2) - y_centroid * m01) / data_sum
        cov = np.array([[u20, u11], [u11, u02]])
        return cov

class BeamprofilerTimeseriesData():
    def __init__(self, datafile: str) -> None:
        pass

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.realpath(__file__))
    x = BeamprofilerImageData(datafile = os.path.join(base_dir, "./2022-08-05_High Frequency Painting/100kHz_+-1.250.0V_10MHzModulation.csv"))
    x.rotateImage(degrees = x.getAngleForRotation())
    x.displayImage()