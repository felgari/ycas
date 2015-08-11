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

"""This module provides some functions on text files. """

import os
import logging
import csv
from constants import *

# Character to separate parameter name from its value in a configuration file.
CFG_FILE_SEP_CHAR = "="
COMMENT_CHARACTER = "#"

def read_catalog_file(file_name):
    """Read a file containing in each file a x,y coordinate pair and a numeric 
    identifier for each coordinate.
        
    Args:
        file_name: The name of the file to read.
    
    Returns:    
        The list of coordinates read from the file indicated.
    
    """
    
    # List of coordinates read.
    coordinates = []
    
    # List of identifiers for the coordinates read.
    identifiers = []
    
    logging.debug("Reading coordinates from: %s" % (file_name))
    
    try:
        # Read the coordinates from the file.
        with open(file_name, 'rb') as fr:
            reader = csv.reader(fr, delimiter=' ')        
                
            for row in reader:            
                coordinates.append(row)  
                
                identifiers.extend([row[CAT_ID_COL]])
    except IOError as ioe:
        logging.error("Reading coordinates file: %s" % (file_name))                 

    logging.debug("Coordinates read: %s" % (identifiers))

    return coordinates  

def read_cfg_file(file_name):
    """Read parameters from a text file containing a pair parameter/value
    in each line separated by an equal character.
    
    Args:
        file_name: Name of the file to read.
    
    Returns:
        The list of parameters read as a dictionary.
    """
    
    cfg_params = {}
    
    logging.debug("Reading configuration from file: %s" % (file_name))
    
    try:
    
        # Read the file that contains the cfg_params of interest.
        with open(file_name, 'rb') as fr:
            reader = csv.reader(fr, delimiter=CFG_FILE_SEP_CHAR)        
            
            for row in reader:    
                # Discard if it is a comment line.
                if len(row) > 0 and \
                    row[0].strip()[0] <> COMMENT_CHARACTER:
                     
                    # Just two elements, the parameter name and value.
                    if len(row) == 2:             
                        try:
                            # Remove spaces before using the values.                
                            param_name = row[0].strip()
                            param_value = row[1].strip()
                            
                            cfg_params[param_name] = param_value
                            
                        except TypeError as te:
                            logging.error(te)
                    else:
                        # the line has not a valid number of elements.
                        logging.warning("Format invalid in '%s' of file %s, line ignored." %
                                        (row, file_name))  
                
        logging.debug("Read these configurations parameters: %s from %s" % 
                      (cfg_params, file_name))
               
    except IOError as ioe:
        logging.error("Reading configuration file: %s" % (file_name))
        
        # Return an empty set.
        cfg_params = set()   
            
    return cfg_params 