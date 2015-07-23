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

"""Obtains the magnitude of objects using the photometry calculated previously.

The magnitude values are stored in different files for each object.
"""

import sys
import os
import logging
import yargparser
import pyfits
import csv
import glob
import math
import numpy as np
from constants import *
from textfiles import *
from fitfiles import get_rdls_data
import starsset
from instmag import InstrumentalMagnitude
from extcorrmag import ExtCorrMagnitudes
from calibmag import get_calibrated_magnitudes

def get_instrumental_magnitudes(stars_set):
    """Receives a list of object and compiles the magnitudes for each object.
    
    Args:
    stars: The list of stars.
    
    Returns:        
    A list containing the magnitudes found for each object.
    
    """
    
    ins_mag = InstrumentalMagnitude(stars_set)
        
    # Walk directories searching for files containing magnitudes.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
               
                logging.debug("Found a directory for data images: " + path)

                # Get the list of RDLS files ignoring hidden files 
                # (starting with dot).
                mag_files_full_path = \
                    [f for f in glob.glob(os.path.join(path, "*" + \
                                                       MAG_CSV_PATTERN)) \
                    if not os.path.basename(f).startswith('.')]
                    
                logging.debug("Found " + str(len(mag_files_full_path)) + \
                             " files with magnitudes.")    
                
                # Sort the list of files to ensure a right processing of MJD.
                mag_files_full_path.sort()               
                
                # Process the images of each object that has a RDLS file.
                for mag_file in mag_files_full_path:
                    
                    # Get the magnitudes for this object in current path.
                    ins_mag.read_inst_magnitudes(mag_file, path)
                            
    ins_mag.save_magnitudes()                            
                        
    return ins_mag

def get_extinction_corrected_magnitudes(stars, inst_mag):
    """Returns the magnitudes corrected taking into account the atmospheric
    extinction, when possible.
    
    Args:
    stars: List of stars to process.    
    inst_mag: Instrumental magnitudes for all the stars.
    
    Returns:        
    The magnitudes corrected taking into account the atmospheric extinction.
    
    """
    
    # Creates an object that calculates and applies the extinction coefficients.
    ecm = ExtCorrMagnitudes(stars, inst_mag)                   
            
    # First, calculate the extinction coefficients.
    ecm.calculate_extinction_coefficients()
    
    # Get the corrected magnitudes of stars applying the extinction coefficients
    # calculated.
    ext_corr_mags = ecm.get_corrected_magnitudes()           

    return ext_corr_mags, days, filters
                                       
def process_magnitudes(progargs):
    """Collect the instrumental magnitudes of all the objects of interest.
    Correct the magnitudes taking into account the atmospheric extinction.
    Get a calibrated magnitude for the objects of interest according to the
    standard magnitudes of the Landolt catalog.

    Args:
    progargs: program arguments.        
    
    """
    
    # Read the list of objects whose magnitudes are needed.
    stars = starsset.StarsSet("stars_BQCam.csv")
    
    # Get the instrumental magnitudes for the objects indicated.
    inst_mag = get_instrumental_magnitudes(stars)
    
    old_settings = np.seterr(all='ignore', over='warn')
    
    # If there is any standard star try the correction of atmospheric
    # extinction and the calibration of magnitudes.
    if stars.has_any_std_star:    
    
        # Get the magnitudes that have been extinction corrected.
        ext_corrected_mag, days, filters = \
            get_extinction_corrected_magnitudes(stars, inst_mag)
        
        # Get calibrated magnitudes.
        get_calibrated_magnitudes(stars, ext_corrected_mag, days, filters)
    else:
        logging.warning("There is not any no standard object, " + \
                        "so there is no extinction corrected magnitudes " + \
                        "nor calibrated ones.")
        
    np.seterr(**old_settings)