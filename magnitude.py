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

"""Obtains the magnitude of stars using the photometry calculated previously.

The magnitude values are stored in different files for each star.
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
import starsset
from starmag import StarMagnitudes
from extcorrmag import ExtCorrMagnitudes
from calibmag import get_calibrated_magnitudes

def get_instrumental_magnitudes(stars, target_dir, data_directoy_name):
    """Receives a list of star and compiles the magnitudes for each star.
    
    Args:
        stars: Features of the stars.
        target_dir: Directory that contains the files to process.
        data_directoy_name: Name of the directories that contains data images.     
    
    Returns:        
        A list containing the magnitudes found for each star.
    
    """
    
    star_mags = StarMagnitudes(stars)
        
    # Walk directories searching for files containing magnitudes.
    for path,dirs,files in os.walk(target_dir):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == data_directoy_name:
               
                logging.debug("Found a directory for data images: %s" % (path))

                # Get the list of RDLS files ignoring hidden files 
                # (starting with dot).
                mag_files_full_path = \
                    [f for f in glob.glob(os.path.join(path, "*%s" %
                                                       (MAG_CSV_PATTERN))) \
                    if not os.path.basename(f).startswith('.')]
                    
                logging.debug("Found %d files with magnitudes." % 
                              (len(mag_files_full_path)))    
                
                # Sort the list of files to ensure a right processing of MJD.
                mag_files_full_path.sort()               
                
                # Process the images of each star that has a RDLS file.
                for mag_file in mag_files_full_path:
                    
                    # Get the magnitudes for this star in current path.
                    star_mags.read_inst_magnitudes(mag_file, path)
                            
    star_mags.save_all_mag(target_dir)                            
                        
    return star_mags

def correct_extinction_in_magnitudes(inst_mag):
    """Returns the magnitudes corrected taking into account the atmospheric
    extinction, when possible.
    
    Args:
        stars: List of stars to process.    
        inst_mag: Instrumental magnitudes for all the stars.
    
    Returns:        
        The magnitudes corrected taking into account the atmospheric extinction.
    
    """
    
    # Creates an star that calculates and applies the extinction coefficients.
    ecm = ExtCorrMagnitudes(inst_mag)                   
            
    # First, calculate the extinction coefficients.
    ecm.calculate_extinction_coefficients()
    
    # Return the corrected magnitudes of stars applying the extinction 
    # coefficients calculated.
    ecm.correct_magnitudes()
                                       
def process_magnitudes(stars, target_dir, data_directoy_name):
    """Collect the instrumental magnitudes of all the stars of interest.
    Correct the magnitudes taking into account the atmospheric extinction.
    Get a calibrated magnitude for the stars of interest according to the
    standard magnitudes of the Landolt catalog.

    Args:
        stars: The list of stars.     
        target_dir: Directory that contains the files to process.
        data_directoy_name: Name of the directories that contains data images. 
        
    Returns:
        magnitudes: The magnitudes calculated.
    
    """
    
    # Get the instrumental magnitudes for the stars indicated.
    magnitudes = get_instrumental_magnitudes(stars, target_dir, 
                                             data_directoy_name)
    
    old_settings = np.seterr(all='ignore', over='warn')
    
    # If there is any standard star try the correction of atmospheric
    # extinction and the calibration of magnitudes.
    if stars.has_any_std_star:    
    
        # Get the magnitudes that have been extinction corrected.
        correct_extinction_in_magnitudes(magnitudes)
        
        # Get calibrated magnitudes.
        get_calibrated_magnitudes(magnitudes)
    else:
        logging.warning("There is not any no standard star, " + \
                        "so there is no extinction corrected magnitudes " + \
                        "nor calibrated ones.")
        
    np.seterr(**old_settings)
    
    # Save magnitudes.
    magnitudes.save_magnitudes(target_dir)
    
    return magnitudes