#!/usr/bin/env python3

from datetime import datetime
from multiprocessing.sharedctypes import Value
import numpy as np
import re

class AnritsuData():
    def __init__(self, datafile: str, no_process: bool = False) -> None:
        assert isinstance(datafile, str), "Datafile argument should be a string"

        self.datafile = open(datafile, 'r')

        # Initialize variables
        self.MODEL   = ""
        self.SN      = 0
        self.SETUP   = {}
        self.MARKERS = []

        if not no_process:
            self.processFile()
            print(self.MARKERS)

    def processFile(self) -> None:
        line_no = 0
        
        # MODES
        trace_setup = False
        marker_mode = False
        trdata_mode = False

        trace_id = None
        
        marker_regex = r"([^\d\s]+)(\d+)"
        
        while True:
            line = next(self.datafile).strip()

            if line == "": # ignore blank lines
                continue
            if line.startswith("<"): # ignore <APP...> lines
                continue

            if line_no > 9:
                # PROCESS TRACE SETUP
                if not trace_setup and line.startswith("# Begin TRACE") and line.endswith("Setup"):
                    trace_id = line[14:15]
                    print(f"Trace {trace_id}")
                    self.SETUP[trace_id] = {}
                    trace_setup = True

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

                if line_no > 473:
                    break
            
            # PROCESS BASIC INFORMATION
            elif line_no < 3 and line[:5] == "MODEL":
                self.MODEL = line[6:]
            elif line_no < 4 and line[:2] == "SN":
                self.SN    = int(line[3:])
            elif line_no < 8 and line[:4] == "DATE":
                self.datetime = datetime.strptime(line[5:], '%Y-%m-%d-0%w-%H-%M-%S')

            line_no += 1

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


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.realpath(__file__))
    x = AnritsuData(datafile = os.path.join(base_dir, "./data/2022-08-02-HBW-1kHz.csv"))