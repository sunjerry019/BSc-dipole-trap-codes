#!/usr/bin/env python3

import numpy as np
import scipy.constants as sc
from typing import Callable, Union, Tuple

from scipy.spatial.transform import Rotation
import scipy.integrate


class DipoleTrapLi():
    @staticmethod
    def to_freq_ang(wavelength: float) -> float:
        """Converts a wavelength to its angular frequency using the formula 
        omega = 2*pi*c / lambda

        Args:
            wavelength (float): Wavelength [m, nm]

        Returns:
            float: Angular frequency in s^-1
        """

        if wavelength > 1:
            # its in nm
            # Converts a wavelength in nanometers of light to radians
            return (2*np.pi*sc.speed_of_light*1e9)/(wavelength)
        else:
            return (2*np.pi*sc.speed_of_light)/(wavelength)

    @staticmethod
    def alpha(wavelength: float) -> complex:
        """Calculates the polarizability alpha using equation (8) from the Grimm review paper

        Args:
            wavelength (float): wavelength [nm]

        Returns:
            complex: Complex polarizability alpha
        """
        # Units = (A^2s^4)/(kg rad)
        # Use Equation (8)

        # https://jet.physics.ncsu.edu/techdocs/pdf/PropertiesOfLi.pdf

        omega_0       = DipoleTrapLi.to_freq_ang(wavelength = 671)
        omega         = DipoleTrapLi.to_freq_ang(wavelength = wavelength)
        gamma_omega_0 = 36.898e6  
        # Line width of the transition (We are only interested in the damping there)

        result  = 6 * np.pi * sc.epsilon_0 * (sc.speed_of_light**3)
        result *= gamma_omega_0 / (omega_0**2)
        result /= complex(omega_0**2 - omega**2, - (omega**3/omega_0**2)*gamma_omega_0)

        return result

    @staticmethod
    def potential(intensity: Union[float, np.ndarray], wavelength: float) -> Union[float, np.ndarray]:
        """Calculates the dipole potential using equation (2) of the Grimms Review Paper

        Args:
            intensity (float): Intensity   [W/m^2]
            wavelength (float): Wavelength [nm]

        Returns:
            float: Potential [J]
        """
        
        # Equation (2) of Grimm
        _alpha = DipoleTrapLi.alpha(wavelength = wavelength)

        U_dip  = - np.real(_alpha) * intensity
        U_dip /= 2 * sc.epsilon_0 * sc.speed_of_light

        return U_dip

    @staticmethod
    def trap_temperature(trap_depth: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Converts a trap depth (i.e. min dipole potential) to a temperature using T = U/kB

        Args:
            trap_depth (float): Trap Depth [J]

        Returns:
            float: Temperature of the trap
        """
        
        return -trap_depth/sc.Boltzmann

    @staticmethod
    def gaussian_beam_width(z: Union[float, np.ndarray], w_0: float , z_0: float, Msq: float, wavelength: float) -> Union[float, np.ndarray]:
        """ Returns the gaussian beam width based on a gaussian beam propagation
        
        Note that this function is normalized if:
        - Everything is in SI-Units, or
        - w, w_0: [um], z, z_0: [mm], lmbda: [nm] (preferred)


        Args:
            z (Union[float, np.ndarray]): Position in propagation direction [m, mm]
            w_0 (float): Beam waist                                         [m, um]
            z_0 (float): Position of beam waist                             [m, mm]
            Msq (float): M-squared beam quality factor                      [no unit]
            wavelength (float): Wavelength of light                         [m, nm]

        Returns:
            float: Gaussian beam width [m, um]
        """

        return w_0 * np.sqrt(
            1 + ((z - z_0)**2)*((
                (Msq * wavelength)/
                (np.pi * (w_0**2))
            )**2)
        )

    @staticmethod
    def get_spot_size(f: float, radius_at_lens: float, Msq: float, wavelength: float):
        return (Msq * wavelength * f) / (np.pi * radius_at_lens)

    @staticmethod
    def max_intensity(power: float, width_x: Union[float, np.ndarray], width_y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Generate the max-intensity of the gaussian intensity distribution given power, w_x and w_y

        Function is normalized if:
        - Everything in SI-units, or
        - P [W], w_x [um], w_y [um] (preferred)

        Args:
            power (float): Power                      [W]
            width_x (Union[float, np.ndarray]): width [m, um]
            width_y (Union[float, np.ndarray]): width [m, um]

        Returns:
            float: Max intensity I_0 in [W/m^2, W/um^2]
        """
        return (2 * power) / (np.pi * (width_x*width_y))

    @staticmethod
    def intensity(
            x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray],
            power: float, 
            wavelength: float,
            w_0: Tuple[float, float],
            z_0: Tuple[float, float],
            Msq: Tuple[float, float]
        ) -> Union[float, np.ndarray]:

        """Returns the intensity of a guassian beam at a point in 3D space. Assumes a simple astigmatic beam

        Note that this function is normalized if:
        - Everything is in SI-Units, or
        - w, w_0: [um], z, z_0: [mm], lmbda: [nm] (preferred)

        Args:
            x (Union[float, np.ndarray]): x position (one of the main axes)     [m, um]
            y (Union[float, np.ndarray]): y position (one of the main axes)     [m, um]
            z (Union[float, np.ndarray]): z position (propagation direction)    [m, mm]
            power (float): Power of the beam                                    [W]
            wavelength (float): Wavelength of the light                         [m, nm]
            w_0 (Tuple[float, float]): Tuple of the beam waist (x, y axes)      [m, um]
            z_0 (Tuple[float, float]): Tuple of the rayleigh length (x, y axes) [m, mm]
            Msq (Tuple[float, float]): Tuple of the beam quality factor M^2 (x, y axes)

        Returns:
            float: The intensity at that point [W/m^2, W/um^2]
        """ 

        # the x and y are the main axes for astigmatism

        x_params = { "w_0": w_0[0], "z_0": z_0[0], "Msq": Msq[0], "wavelength": wavelength }
        y_params = { "w_0": w_0[1], "z_0": z_0[1], "Msq": Msq[1], "wavelength": wavelength }

        w_x = DipoleTrapLi.gaussian_beam_width(z = z, **x_params)
        w_y = DipoleTrapLi.gaussian_beam_width(z = z, **y_params)

        I0 = DipoleTrapLi.max_intensity(power = power, width_x = w_x, width_y = w_y)

        if isinstance(x, np.ndarray) and x.ndim > 1:
            assert isinstance(I0, np.ndarray)
            assert isinstance(y, np.ndarray)
            assert isinstance(w_x, np.ndarray)
            assert isinstance(w_y, np.ndarray)

            I0  = I0 [:, np.newaxis]
            y   = y  [:, np.newaxis]
            w_x = w_x[:, np.newaxis]
            w_y = w_y[:, np.newaxis]
        
        print("Calculating Intensities...", end = "\r")
        intensity = I0 * np.exp(-2*((x/w_x)**2 + (y/w_y)**2))
        print("Calculating Intensities...Done!")

        return intensity

    @staticmethod
    def intensity_average(
            x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray],
            power: float, 
            wavelength: float,
            w_0: Tuple[float, float],
            z_0: Tuple[float, float],
            Msq: Tuple[float, float],
            numsamples: int, 
            deviation: float,
            modulation_function: Callable
        ) -> Union[float, np.ndarray]:
        """Returns the intensity of a guassian beam at a point in 3D space averaged over time using the modulation function. Assumes a simple astigmatic beam

        Note that this function is normalized if:
        - Everything is in SI-Units, or
        - w, w_0: [um], z, z_0: [mm], lmbda: [nm] (preferred)

        Args:
            x (Union[float, np.ndarray]): x position (one of the main axes)     [m, um]
            y (Union[float, np.ndarray]): y position (one of the main axes)     [m, um]
            z (Union[float, np.ndarray]): z position (propagation direction)    [m, mm]
            power (float): Power of the beam                                    [W]
            wavelength (float): Wavelength of the light                         [m, nm]
            w_0 (Tuple[float, float]): Tuple of the beam waist (x, y axes)      [m, um]
            z_0 (Tuple[float, float]): Tuple of the rayleigh length (x, y axes) [m, mm]
            Msq (Tuple[float, float]): Tuple of the beam quality factor M^2 (x, y axes)
            numsamples (int): Number of samples to take for the integration
            deviation (float): Amplitude of the modulation for the propagation axis [m, um]
            modulation_function (Callable): Function to modulate the position with. This function should take one parameter t (0 to 1) and have range -1 to 1

        Returns:
            float: The averaged intensity at that point [W/m^2, W/um^2]
        """ 

        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.simpson.html?highlight=simps#scipy.integrate.simpson

        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            xs_t = x[:, np.newaxis]
        else:
            xs_t = x

        # sample t from 0 to 1
        ts     = np.linspace(start = 0, stop = 1, endpoint = True, num = numsamples)
        f_of_t = DipoleTrapLi.intensity(
            x = xs_t - deviation * modulation_function(ts), 
            y = y, 
            z = z, 
            power = power,
            wavelength = wavelength,
            w_0 = w_0, z_0 = z_0, Msq = Msq)

        try:
            integrated = scipy.integrate.simpson(y = f_of_t, x = ts)
        except AttributeError as e:
            integrated = scipy.integrate.simps(y = f_of_t, x = ts)
        
        return integrated

def transform_quaternion_angle(axis: np.ndarray, degrees: float) -> Rotation: 
    """Generates a scipy.spatial.transform.Rotation object from a rotation axis and how many degrees to rotate.
    The Rotation object is generated using quarternions

    q = cos(a/2) + sin(a/2)(x*i + y*j + z*k)

    Args:
        axis (np.ndarray): Rotation axis in the form of (1,3) or (3,1) np array
        degrees (float): Degrees to rotate

    Returns:
        Rotation: scipy.spatial.transform.Rotation object
    """

    halfangle = np.deg2rad(degrees)/2

    unit_axis = axis.flatten()
    unit_axis = unit_axis / np.linalg.norm(unit_axis)

    ax = np.sin(halfangle) * unit_axis
    q  = np.concatenate(([np.cos(halfangle)], ax))

    return Rotation.from_quat(q)

def rotate_points(points: np.ndarray, axis: np.ndarray, degrees: float) -> np.ndarray:
    """Rotate a point or multiple points by rotating them

    Args:
        points (np.ndarray): Points to be transformed
        axis (np.ndarray): Rotation axis in the form of (1,3) or (3,1) np array
        degrees (float): Degrees to rotate

    Returns:
        np.ndarray: Transformed points
    """
    _R  = transform_quaternion_angle(axis = axis, degrees = degrees)
    _xp = _R.apply(points)

    return _xp

# https://stackoverflow.com/a/11146645
def cartesian_product(*arrays: np.ndarray) -> np.ndarray:
    """Creating a cartesian product of the input arrays.

    Returns:
        np.ndarray: The cartesian product of the input arrays
    """
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)