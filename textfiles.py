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
import csv
from constants import *

# Character to separate parameter name from its value in a configuration file.
CFG_FILE_SEP_CHAR = "="

def read_cfg_file(file_name):
    """Read parameters from a text file containing a pair parameter/value
    in each line separated by an equal character.
    
    Args:
        file_name: Name of the file to read.
    
    Returns:
        The list of parameters read as a dictionary.
    """
    
    cfg_params = {}
    
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
                         print "Format invalid in '%s' of file %s, line ignored." \
                            % (row, file_name)  
               
    except IOError as ioe:
        print "Error reading configuration file: %s" % (file_name)
        
        # Return an empty set.
        cfg_params = set()   
            
    return cfg_params 