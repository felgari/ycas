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

"""Generate plots with different types of light curves that could be done from
the magnitudes calculated.

"""

import sys
import csv
import logging
import argparse
import magnitude
from constants import *

TSV_FILE_DELIM = '\t'

MJD_COL = 3
MAG_COL = 4
ERR_COL = 5

NO_VALUE = "NA"
        
class LightCurves(object):
    """Class to generate light curves from the magnitudes calculated for the
    objects of interest.
    
    Two types of light curves are generated. One type of curves shows 
    differential magnitudes and the other one shows magnitudes calibrated.
    
    """

def read_input_files(file_names, calculate_median):
    """Read a set of csv file whose names have been received as parameters.
    
    All the data read from the files is returned as a list that contains
    lists, each of these lists with data read from a file.
        
    Args:
        file_names: The names of the files to read.
        calculate_median: True if the median may be calculated.
    
    Returns:  
        The data read in the files.  
        
    """
    
    files_data = []
    
    # Iterate over the file names.
    for fn in file_names:
        
        try:
        
            data = []
            
            # Open current file.
            with open(fn, 'rb') as fr:
                reader = csv.reader(fr, delimiter=CSV_FILE_DELIM)  
                
                # Skip header.
                next(reader)      
            
                # Process each row.
                for row in reader:    
                    # Check if the row is valid.
                    if len(row) > 0:            
                        # Check if the median may be calculated.                            
                        if calculate_median:
                                        
                            new_row = []
                                                   
                            # For each data, each row, add all the items but for
                            # the column that contains the MJD, take only the 
                            # integer part of the MJD. All the data with the same 
                            # value in this part will be used to calculate a median 
                            # value.
                            for i in range(len(row)):
                                if i == MJD_COL:
                                    item = row[i]
                                    new_row.extend([item[:item.find('.')]])
                                else:
                                    new_row.extend([row[i]])   
                                      
                            data.append(new_row)
                        else:
                            data.append(row)  
                        
                files_data.append(data) 
                
        except IOError as ioe:
            logging.error("Reading magnitude file: '%s'" % (fn))             
            
        logging.debug("File " + fn + " read " + str(len(data)) + " lines.")

    return files_data

def generate_curves(stars, stars_mag):
    """Generate curves from the magnitudes files of the stars received.
    
    Args:
        stars: List of stars.
        stars_mag: The magnitudes calculated.
        
    """
    
    if stars_mag is None:
        # TODO
        pass