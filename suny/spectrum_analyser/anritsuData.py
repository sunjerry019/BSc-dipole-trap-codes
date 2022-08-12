#!/usr/bin/env python3

from datetime import datetime
from multiprocessing.sharedctypes import Value
from typing import Tuple
import numpy as np
import numpy._typing as np_t
import re

class AnritsuData():
    def __init__(self, datafile: str, no_process: bool = False) -> None:
        """Bridging Class to handle the data from Anritsu Spectrum Master. Data is returned in the form of self.DATA[trace_id]["FREQ"] and ...["POWER"]. THe frequency is in MHz and power is given in dBm.

        Args:
            datafile (str): Path to the datafile
            no_process (bool, optional): Whether to process the data immediately. If set to True, the data will only be processed upon calling the function self.processFile(). Defaults to False.
        """
        assert isinstance(datafile, str), "Datafile argument should be a string"

        self.datafile = open(datafile, 'r')

        # Initialize variables
        self.MODEL   = ""
        self.SN      = 0
        self.SETUP   = {}
        self.MARKERS = []
        self.DATA    = {}

        if not no_process:
            self.processFile()

    def processFile(self) -> None:
        line_no = 0
        
        # MODES
        trace_setup = False
        marker_mode = False
        trdata_mode = False

        trace_id = None
        
        marker_regex = r"([^\d\s]+)(\d+)"
        
        while True:
            line = next(self.datafile, None)
            if line is None:
                break
            
            line = line.strip()

            if line == "": # ignore blank lines
                continue
            if line.startswith("<"): # ignore <APP...> lines
                continue

            if line_no > 9:
                if line.startswith("# Begin TRACE"):
                    trace_id = line[14:15]
                    # print(f"Trace {trace_id}")

                    # PROCESS TRACE SETUP
                    if not trace_setup and line.endswith("Setup"):
                        assert trace_id not in self.SETUP
                        self.SETUP[trace_id] = {}
                        trace_setup = True

                    # PROCESS TRACE DATA
                    elif not trdata_mode and line.endswith("Data"):
                        assert trace_id not in self.DATA
                        self.DATA[trace_id] = {"FREQ": [], "POWER": []}
                        trdata_mode = True

                # PROCESS TRACE SETUP
                elif trace_setup:
                    if line == "# Setup Done":
                        trace_setup = False
                        trace_id = None
                    else:
                        try:
                            key, val = line.split(",")
                            self.SETUP[trace_id][key] = AnritsuData.coerce_number(val)
                        except ValueError as e:
                            print("Skipping: ", line)
                
                # PROCESS TRACE DATA
                elif trdata_mode:
                    if line == "# Data Done":
                        self.DATA[trace_id]["FREQ"] = np.array(self.DATA[trace_id]["FREQ"])
                        self.DATA[trace_id]["POWER"] = np.array(self.DATA[trace_id]["POWER"])
                        trdata_mode = False
                        trace_id = None
                    else:
                        dtpt = [x.strip() for x in line.split(",")[1:]]
                        assert dtpt[2] == "MHz", "Units other than MHz not implemented!"
                        self.DATA[trace_id]["FREQ"].append(AnritsuData.coerce_number(dtpt[1]))
                        self.DATA[trace_id]["POWER"].append(AnritsuData.coerce_number(dtpt[0]))
                        

                # PROCESS MARKERS
                elif not marker_mode and line == "# Begin SPA Marker":
                    marker_mode = True
                elif marker_mode:
                    if line == "# SPA Marker Done":
                        marker_mode = False
                    else:
                        splat = line[8:].split(",")
                        marker_res = re.search(marker_regex, splat[0])
                        if marker_res is not None:
                            marker_no = int(marker_res.group(2))
                            key = marker_res.group(1)
                            val = AnritsuData.coerce_number(splat[1])

                            while marker_no >= len(self.MARKERS):
                                self.MARKERS.append({})
                            
                            self.MARKERS[marker_no][key] = val
            
            # PROCESS BASIC INFORMATION
            elif line_no < 3 and line[:5] == "MODEL":
                self.MODEL = line[6:]
            elif line_no < 4 and line[:2] == "SN":
                self.SN    = int(line[3:])
            elif line_no < 8 and line[:4] == "DATE":
                self.datetime = datetime.strptime(line[5:], '%Y-%m-%d-0%w-%H-%M-%S')

            line_no += 1

    # @staticmethod
    # def resample(data_freq: np.ndarray, data_power_dBm: np.ndarray, binsize: float) -> Tuple[np.ndarray, np.ndarray]:
    #     # binsize unit should be same as data_freq unit
    #     # actual binsize might be bigger or smaller

    #     original_binsize = np.average(np.diff(data_freq))
    #     assert binsize > original_binsize, f"New binsize ({binsize}) must be more than old ({original_binsize})"

    #     freq_max = np.max(data_freq)
    #     freq_min = np.min(data_freq)
    #     new_bin_num = int(np.around((freq_max - freq_min) / binsize))

    #     new_freq = bin_ndarray(ndarray = data_freq, new_shape = (new_bin_num,) operation = "average")
    #     print(data_freq, new_freq)
        

    @staticmethod
    def dBmToWatt(data: float | np.ndarray) -> float | np.ndarray:
        # CITE: https://www.rapidtables.com/convert/power/dBm_to_Watt.html
        return np.power(10, 0.1*(data - 30))

    @staticmethod
    def coerce_number(numlike: str) -> int | float | str:
        """Attempts to coerce a number-like argument to a number, otherwise returns it as it was

        Args:
            numlike (str): Number-like string to be converted

        Returns:
            int | float | str: 
                If the string is an integer, an integer will be returned.
                If the string is a float, a float will be returned.
                In other cases, the original string will be returned with no error thrown.
        """
        try:
            return int(numlike) 
        except ValueError:
            try:
                return float(numlike)
            except ValueError:
                return numlike

    def __enter__(self) -> None:
        pass

    def __exit__(self ,type, value, traceback) -> None:
        if not self.datafile.closed:
            self.datafile.close()


# CITE: https://gist.github.com/derricw/95eab740e1b08b78c03f
# ........ https://gist.github.com/zonca/1348792
# ........ https://stackoverflow.com/questions/8090229/resize-with-averaging-or-rebin-a-numpy-2d-array
def bin_ndarray(ndarray: np.ndarray, new_shape: np_t._ShapeLike, operation: str ='sum') -> np.ndarray:
    """
    Bins an ndarray in all axes based on the target shape, by summing or
        averaging.
    Number of output dimensions must match number of input dimensions.
    Example
    -------
    >>> m = np.arange(0,100,1).reshape((10,10))
    >>> n = bin_ndarray(m, new_shape=(5,5), operation='sum')
    >>> print(n)
    [[ 22  30  38  46  54]
     [102 110 118 126 134]
     [182 190 198 206 214]
     [262 270 278 286 294]
     [342 350 358 366 374]]
    """
    if not operation.lower() in ['sum', 'mean', 'average', 'avg']:
        raise ValueError("Operation {} not supported.".format(operation))
    if ndarray.ndim != len(new_shape):
        raise ValueError("Shape mismatch: {} -> {}".format(ndarray.shape,
                                                           new_shape))
    compression_pairs = [(d, c//d) for d, c in zip(new_shape,
                                                   ndarray.shape)]
    flattened = [l for p in compression_pairs for l in p]
    _temp = np.zeros(flattened).squeeze()
    ndarray = ndarray.reshape(_temp.shape)
    for i in range(len(new_shape)):
        if operation.lower() == "sum":
            ndarray = ndarray.sum(-1*(i+1))
        elif operation.lower() in ["mean", "average", "avg"]:
            ndarray = ndarray.mean(-1*(i+1))
    return ndarray

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.realpath(__file__))
    x = AnritsuData(datafile = os.path.join(base_dir, "./2022-08-02_data/2022-08-02-HBW-1kHz.csv"))
    # x.resample(data_freq = x.DATA["A"]["FREQ"], data_power_dBm = x.DATA["A"]["POWER"], binsize = 100e-3)