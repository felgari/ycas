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

"""
This module groups some functions performed on text files.
"""

def read_objects_of_interest(objects_file):
    """
        
    Read the list of objects of interest from the file indicated.
    This file contains the name of the object and the AR, DEC 
    coordinates of each object.
    
    """
    
    objects = list()
    
    logging.debug("Reading object from file: " + objects_file)
    
    # Read the file that contains the objects of interest.
    with open(objects_file, 'rb') as fr:
        reader = csv.reader(fr, delimiter='\t')        
        
        for row in reader:    
            if len(row) > 0:
                # Only the column with name of the object.
                objects.append(row[OBJ_NAME_COL])   
            
    logging.debug("Read the following objects: " +  str(objects))            
            
    return objects  