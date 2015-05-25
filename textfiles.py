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

""" This module groups some functions performed on text files. """

import logging
import csv
from constants import *

# Functions for text files with objects coordinates: .coo.

RA_POS_COO = 0
DEC_POS_COO = 1
ID_POS_COO = 2

def read_objects_of_interest(objects_file):
    """Read the list of objects of interest from the file indicated.
    
    This file contains the name of the object and the AR, DEC 
    coordinates of each object.
    
    Keyword arguments:
    objects_file -- Name of the file that contains the information of objects.
    
    """
    
    objects = list()
    
    logging.debug("Reading object from file: " + objects_file)
    
    # Read the file that contains the objects of interest.
    with open(objects_file, 'rb') as fr:
        reader = csv.reader(fr, delimiter=',')        
        
        for row in reader:    
            if len(row) > 0:
                # Only the column with name of the object.
                objects.append(row)   
            
    logging.debug("Read the following objects: " +  str(objects))            
            
    return objects  

def convert_deg_to_dec_deg(str_degress, is_ra = False):
    """Convert the coordinate in degrees received to decimal degrees.
    
    Keyword arguments:
    str_degress -- A string containing a value in degrees, minutes and seconds.
    is_ra -- Indicates if the value received is right ascension and so it
        should be multiplied to scale it from 24 to 360.
    
    Returns:    
    The value received converted to decimal degrees.
    """    
    
    multiplier = 1.0
    
    if is_ra:
        multiplier = 15.0
    
    degrees_list = str_degress.split(":")
    
    decimal_degrees = float(degrees_list[0])
    
    decimal_degrees += ( float(degrees_list[1]) / 60.0 )
                                    
    decimal_degrees += ( float(degrees_list[2]) / 3660.0 )
    
    return decimal_degrees * multiplier

def get_coordinates(content):
    """Convert the RA, DEC pair of coordinates received to decimal degrees.
    
    in degrees stored in the list received
    converted to a pair RA, DEC in decimal degrees.
    
    Keyword arguments:
    content -- String of coordinates of RA and DEC in degrees, minutes and 
        seconds.
    
    Returns:    
    RA and DEC values converted to decimal degrees.    
    """
    
    # Get RA and DEC strings in degrees.
    ra_deg = content[RA_POS_COO]
    dec_deg = content[DEC_POS_COO]
    id = content[ID_POS_COO]
    
    # Remove comma.
    ra_deg = ra_deg[:ra_deg.find(',')]
    dec_deg = dec_deg[:dec_deg.find(',')]
            
    ra_dec_deg = convert_deg_to_dec_deg(ra_deg, True)
    dec_dec_deg = convert_deg_to_dec_deg(dec_deg)
    
    return ra_dec_deg, dec_dec_deg, id

def read_references_for_object(object_name):
    """ Read a file with the coordinates of some objects in its field.
    
    Read a file with the name of the object that contains coordinates
    of reference objects in its same field to perform differential photometry.
    The first object object of the file are the coordinate of the proper object.
    Return a list of lists, each list contains the coordinates for the field 
    of an object
        
    Keyword arguments:
    object_name -- The name of the object.
    
    Returns:    
    The coordinates read from the file indicated.
    
    """
    
    references = []
    
    # Build the file name.
    file_name = object_name + "_field." + COORD_FILE_EXT
    
    logging.debug("Reading coordinates from: " + file_name)
    
    try:
        # Read the coordinates from the file.
        with open(file_name, 'rb') as fr:
            reader = csv.reader(fr, delimiter=' ')        
            
            included_cols = [2, 5, 6]
                
            for row in reader:
                if len(row) > max(included_cols):
                    content = list(row[i] for i in included_cols)
                    ra, dec, id = get_coordinates(content)
                    
                    references.append([ra, dec, id])    
    
        logging.debug("Coordinates read: " + str(references))
    except IOError:
        logging.error("Reading coordinates file: " + file_name)

    return references

def read_catalog_file(file_name):
    """ Read a catalog file containing coordinates and an identifier 
        for each one.
    
    Read a file containing in each file a x,y coordinate pair and a numeric 
    identifier for each coordinate.
        
    Keyword arguments:
    file_name -- The name of the file to read.
    
    Returns:    
    The list of coordinates read from the file indicated.
    
    """
    
    # List of coordinates read.
    coordinates = []
    
    # List of identifiers for the coordinates read.
    identifiers = []
    
    logging.debug("Reading coordinates from: " + file_name)
    
    # Read the coordinates from the file.
    with open(file_name, 'rb') as fr:
        reader = csv.reader(fr, delimiter=' ')        
            
        for row in reader:            
            coordinates.append(row)  
            
            identifiers.extend([row[CAT_ID_COL]])

    logging.debug("Coordinates read: " + str(identifiers))

    return coordinates    