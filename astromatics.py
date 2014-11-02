#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Felipe Gallego. All rights reserved.
#
# This file is part of ycas: https://github.com/felgari/ycas
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import logging
import glob
from subprocess32 import check_output
from scipy.stats import mode
from constants import *

def process_sextractor_output(command_out):
    """
    Process the output of sextractor to calculate the FWHM of the
    image. Only values of fwhm greater than a minimun value near zero
    are considered.
    The return value is the mode of the values considered.
    The mode is the statistics considered to get the best representation
    of the fwhm of the image. 
    
    """    
    
    # Get output in lines.
    lines = command_out.split("\n")
    
    # To accumulate the valid fwhm.
    sum = []
    
    # Process the output lines.
    for l in lines:
        # If it is not a commented line.
        if len(l) > 0 and l[0] != SEXTACTOR_COMMENT:
            
            # Get the columns of the line.
            cols = l.split(" ")
            
            # Discard empty strings.
            cols = filter(len, cols)      
            
            # Get the fwhm from the columns of the line.
            fwhm = float(cols[SEXTACTOR_FWHM_COL])
            
            # If it is a value considered valid, store it.
            if fwhm > SEXTACTOR_FWHM_MIN_VALUE:
                sum.extend([fwhm])
    
    # Return the mode of the fwhm values found.
    return mode(sum)[0][0]

def get_fwhm(progargs, img_filename):
    """
    Execute sextractor on the image received to get its fwhm.
    
    """

    # Build the command to execute.
    command = "sex -c " + \
        os.path.join(progargs.sextrator_cfg_path, SEXTRACTOR_CFG_FILENAME) \
        + " " + os.path.join(os.getcwd(), img_filename)
        
    logging.info("Executing: " + command)
    
    # Execute command.
    command_out = check_output(command, shell=True)

    # Process the output.
    fwhm = process_sextractor_output(command_out)
    
    logging.info("FWHM calculated is: " + str(fwhm))

    return fwhm