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
This module groups some functions performed on fit files.
"""

import logging
import pyfits
from constants import *

DATE_FIELD_NAME = "DATE-OBS"
FILTER_FIELD_NAME = "FILTER"
IMAGE_TYPE_FIELD_NAME = "IMAGETYP"

BIAS_TYPE = "BIAS"
FLAT_TYPE = "FLAT"

ORG_FIT_HEADER_FIELDS = [DATE_FIELD_NAME, IMAGE_TYPE_FIELD_NAME, FILTER_FIELD_NAME]

def get_image_filter(header_fields, filename):
    """ Returns the filter indicated in the filename if any. 
    
    This function returns the filter used for this image.
    At first, the filter is searched in header file, if it is not found there,
    the filter is extracted from the file name.
    The filter name is part of the file name and is located in a
    particular position.
    
    """    

    filtername = ''
    field_processed = False
    
    
    # Check if any header field has been found.
    if header_fields != None and len(header_fields) > 0:
        
        # The header field could not have found.
        try:    
            # Retrieve the filter from the header field.
            field_value = header_fields[FILTER_FIELD_NAME]
            
            if field_value != None and field_value != "":
                field_processed = True
                
                filtername = field_value
        except KeyError as ke:
            logging.warning("Header field '" + FILTER_FIELD_NAME + \
                            "' not found in file " + filename)
            
    # If the header field has not been processed.
    if not field_processed:
        # Get the filter from the file name.
        filename_no_ext = filename[:-len('.' + FIT_FILE_EXT)]    

        for f in FILTERS:
            index = filename_no_ext.rfind(f)
    
            if index > 0:
                filtername = f
        
    # If the filter has been identified, show the method used.
    if len(filtername) > 0:      
        if field_processed:
            logging.debug(filename + " filter read from file headers.")
        else:
            logging.warning(filename + " filter read from file name.") 
    
    return filtername

def get_fit_fields(fit_file_name):
    """
    
    This function retrieves some fields of the fit header
    corresponding to the file name received.
    
    """
    
    logging.debug("Extracting header fields for: " + fit_file_name)
    
    # Create a dictionary to retrieve easily the appropriate list
    # using the name of the object.
    header_fields = {}        
    
    try:
        # Open FIT file.
        hdulist = pyfits.open(fit_file_name)
        
        # Get header of first hdu, only one hdu is used.
        header = hdulist[0].header
        
        # For all the header fields of interest.
        for i in range(len(ORG_FIT_HEADER_FIELDS)):
            
            field = ORG_FIT_HEADER_FIELDS[i]
            
            # Retrieve and store the value of this field.
            header_fields[field] = header[field]
        
        hdulist.close() 
    except IOError as ioe:
        logging.error("Error reading fit file '" + fit_file_name + \
                      "'. Error is: " + str(ioe))
    except KeyError as ke:
        logging.warning("Header field '" + ORG_FIT_HEADER_FIELDS[i] + \
                        "' not found in file " + fit_file_name)        
        
    return header_fields  

def file_is_type(header_fields, filename, field_type, type_string):
    """
    
    This function determine if the data received are
    related to a specific type of file. 
    First the header fields are evaluated and if the 
    result is not conclusive the file name is analyzed.
    The file name has the the form type-orderfilter.fit'.
    Where 'type' could be 'flat', 'bias' or a proper name.
    A '-' character separates the 'orderfilter' part that
    indicates the ordinal number of the image and optionally
    a filter, only bias has no filter.     
    
    """  
    
    is_type = False
    field_processed = False
    
    # Check if any header field has been found.
    if header_fields != None and len(header_fields) > 0:
        
        # The header field could not have found.
        try:    
            # Retrieve the image type from the header field.
            field_value = header_fields[IMAGE_TYPE_FIELD_NAME]
            
            if field_value != None and field_value != "":
                field_processed = True
                
                if field_value == field_type:
                    is_type = True
        except KeyError as ke:
            logging.warning("Header field '" + IMAGE_TYPE_FIELD_NAME + \
                            "' not found in file " + filename)       
        
    # If the header field has not been processed.
    if not field_processed:
        
        # Some files have prefixes with numbers delimited by dots
        # that is necessary to remove to identify the file type.
        clean_filename = filename.split(".")[-1]
         
        # Get the type from the file name.
        is_type = clean_filename.startswith(type_string)
        
    # If the type has been identified, show the method used.
    if is_type:      
        if field_processed:
            logging.debug(filename + " type using file headers.")
        else:
            logging.warning(filename + " type using file name.")        
    
    return is_type       

def file_is_bias(header_fields, filename):    
    """
    
    This function determine if the data received are
    related to a bias file. 
    
    """
    
    return file_is_type(header_fields, filename, \
                        BIAS_TYPE, BIAS_STRING)
    
def file_is_flat(header_fields, filename):    
    """
    
    This function determine if the data received are
    related to a flat file. 
    
    """
    
    return file_is_type(header_fields, filename, \
                        FLAT_TYPE, FLAT_STRING)