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

"""This module calculates a FWHM for an astronomical image.

The calculation is performed using sextractor. sextractor identifies the objects
in the images and calculates a FWHM for each one.

A FWHM from all the FWHM returned by sextractor is calculated as the FWHM of 
the image.

"""

import sys
import os
import logging
import glob
from scipy.stats import mode
from constants import *

# Depending on Python version this module has a different name.
if sys.version_info < (3, 3):
    from subprocess32 import check_output
else:
    from subprocess import check_output

def process_sextractor_output(command_out):
    """Process sextractor' output to calculate the FWHM of the image. 
    
    Only values of FWHM greater than a minimun value near zero
    are considered.
    The value returned is the mode of all the FWHM values of the image.
    The mode is the statistics considered to get the best representation
    of the FWHM of the image.
    
    Keyword arguments:
    command_out -- The output of the sextractor execution.
    
    Returns:
    The mode of the all the FWHM values received.
    
    """    
    
    # Get the output received in lines.
    lines = command_out.split("\n")
    
    # To accumulate the valid FWHM values.
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
    
    # Return the mode of the FWHM values found.
    return mode(sum)[0][0]

def get_fwhm(progargs, img_filename):
    """Execute sextractor on the image received to get its fwhm. 
    
    Keyword arguments:
    progargs -- Program arguments.
    img_filename -- Name of the file with image whose FWHM is calculated.
    
    Returns:    
    The FWHM value calculated for the image indicated.
    
    """

    # Build the command to execute.
    command = "sex -c " + \
        os.path.join(progargs.sextrator_cfg_path, SEXTRACTOR_CFG_FILENAME) \
        + " " + os.path.join(os.getcwd(), img_filename)
        
    logging.debug("Executing: " + command)
    
    # Execute sextractor command to calculate the FWHM of the objects detected
    # in the image.
    command_out = check_output(command, shell=True)

    # Process the output.
    fwhm = process_sextractor_output(command_out)
    
    logging.debug("FWHM calculated is: " + str(fwhm))

    return fwhm