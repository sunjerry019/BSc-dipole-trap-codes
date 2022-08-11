#!/usr/bin/env python3

import numpy as np
import numpy._typing as np_t
import matplotlib.pyplot as plt
import scipy.ndimage

import sys

class BeamprofilerImageData():
    def __init__(self, datafile: str, autocrop: bool = True, autorotate: bool = True) -> None:
        self.DATA = np.loadtxt(datafile, delimiter = ',')
        self.ORIGINAL_DATA = self.DATA

        if autocrop:
            self.cropToContent()

        if autorotate:
            self.rotateImage(degrees = self.getAngleForRotation())

        # MAYBE at some point: https://stackoverflow.com/questions/45177154/how-to-decode-color-mapping-in-matplotlibs-colormap

    def cropToContent(self, padding: int = 5, threshold: float = 2) -> None:
        # CITE: https://stackoverflow.com/a/48987831

        coords = np.argwhere(self.DATA > threshold)
        x_min, y_min = coords.min(axis=0)
        x_max, y_max = coords.max(axis=0)

        x_min -= padding; y_min -= padding
        x_max += padding; y_max += padding

        self.DATA = self.DATA[x_min:x_max+1, y_min:y_max+1]

        # with np.printoptions(threshold=sys.maxsize):
        #     print(self.DATA)

    def getAngleForRotation(self) -> float:
        # To obtain the angle, we use https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/#2-Raw-image-moments
        # https://stackoverflow.com/questions/9005659/compute-eigenvectors-of-image-in-python
        # Write something about PCA and moments and the equation
        
        cov = BeamprofilerImageData.moments_cov(self.DATA)
        eigvals, eigvecs = np.linalg.eig(cov)

        largest_eig_idx = np.argmax(eigvals)
        # We only look at the eigenvector with the largest eigenvalue
        _x, _y = eigvecs[largest_eig_idx]
        theta = np.rad2deg(np.arctan(_x/_y)) + 90 + 1 # small adjustment

        return theta

    def rotateImage(self, degrees: float) -> None:
        self.DATA = scipy.ndimage.rotate(self.DATA, angle = degrees)
    
    def displayImage(self) -> None:
        _, ax = plt.subplots()
        ax.imshow(self.DATA)
        plt.show()
    
    def padToSize(self, shape: np_t._ShapeLike) -> None:
        biggerImage = np.zeros(shape = shape)

        n_x, n_y = np.shape(biggerImage)
        o_x, o_y = np.shape(self.DATA)

        left = int(np.ceil((n_x - o_x) / 2))
        top  = int(np.ceil((n_y - o_y) / 2))

        biggerImage[left:left+o_x, top:top+o_y] = self.DATA
        self.DATA = biggerImage

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
    x = BeamprofilerImageData(datafile = os.path.join(base_dir, "/mnt/data/School/University/Deutschland/LMU/Modules/1_PH/2022SS/Bachelorarbeit/dipole-trap-codes/suny/beamprofiler_data/2022-08-05_High Frequency Painting/100kHz_1.250.0V_10MHzModulation.csv"))
    # x.cropToContent()
    # x.padToSize((500, 500))
    x.displayImage()