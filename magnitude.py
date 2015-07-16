#!/usr/bin/env python
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
import math
from constants import *
from textfiles import *
from fitfiles import get_rdls_data
from instmag import get_instrumental_magnitudes
from extcorrmag import get_extinction_corrected_magnitudes
from calibmag import get_calibrated_magnitudes

def get_indexes_of_std_and_no_std(objects):
    """ Returns the indexes for the standard and no standard objects.
    
    Keyword arguments:
    objects -- List of objects to process.
    
    Returns:        
    The indexes for the standard and no standard objects.
    """
    
    standard_obj_index = []
    no_standard_obj_index = []
    
    # For each object. The two list received contains the same 
    # number of objects.
    for i in range(len(objects)):     
        # Check if it is a standard object to put the object in
        # the right list.
        if objects[i][OBJ_STANDARD_COL] == STANDARD_VALUE:
            standard_obj_index.extend([i])
        else:
            no_standard_obj_index.extend([i])     
                
    return standard_obj_index, no_standard_obj_index
                                       
def process_magnitudes(progargs):
    """ 

    Collect the instrumental magnitudes of all the objects of interest.
    Correct the magnitudes taking into account the atmospheric extinction.
    Get a calibrated magnitude for the objects of interest according to the
    standard magnitudes of the Landolt catalog.

    Keyword arguments:
    progargs -- program arguments.        
    
    """
    
    # Read the list of objects whose magnitudes are needed.
    objects = read_objects_of_interest(progargs.interest_object_file_name)
    
    # Get the instrumental magnitudes for the objects indicated.
    inst_mag = get_instrumental_magnitudes(objects)
    
    # Get the indexes for standard (if any) and no standard objects.
    std_obj_idxs, no_std_obj_idxs = get_indexes_of_std_and_no_std(objects)
    
    # If there is any no standard object try the correction of atmospheric
    # extinction and the calibration of magnitudes.
    if len(no_std_obj_idxs) > 0:    
    
        # Get the magnitudes that have been extinction corrected.
        ext_corrected_mag, days, filters = \
            get_extinction_corrected_magnitudes(objects, \
                                                std_obj_idxs, \
                                                no_std_obj_idxs, \
                                                inst_mag)
        
        # Get calibrated magnitudes.
        get_calibrated_magnitudes(objects, std_obj_idxs, no_std_obj_idxs, \
                                  ext_corrected_mag, days, filters)
    else:
        logging.warning("There is not any no standard object, " + \
                        "so there is no extinction corrected magnitudes " + \
                        "nor calibrated ones.")