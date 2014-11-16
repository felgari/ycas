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
XBINNING_FIELD_NAME = "XBINNING"
YBINNING_FIELD_NAME = "YBINNING"

BIAS_TYPE = "BIAS"
FLAT_TYPE = "FLAT"

ORG_FIT_HEADER_FIELDS = [DATE_FIELD_NAME, IMAGE_TYPE_FIELD_NAME, FILTER_FIELD_NAME]


def get_filter_from_file_name(filename):
    """ Get the filter from the file name. """
    
    filtername = ""
    
    filename_no_ext = filename[:-len('.' + FIT_FILE_EXT)]
    
    for f in FILTERS:
        index = filename_no_ext.rfind(f)
        if index > 0:
            filtername = f
    
    return filtername

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
        filtername = get_filter_from_file_name(filename)
        
    # If the filter has been identified, show the method used.
    if len(filtername) > 0:      
        if field_processed:
            logging.debug(filename + " filter read from file headers: " + filtername)
        else:
            logging.warning(filename + " filter read from file name: " + filtername) 
    
    return filtername

def get_image_filter_from_file(filename):
    """ Returns the filter indicated in the filename if any. 
    
    This function returns the filter used for this image.
    First, the filter is searched in header file, if it is not found there,
    the filter is extracted from the file name.
    The filter name is part of the file name and is located in a
    particular position.
    
    """    
    
    # Get some fit header fields that can be used to organize
    # the image.
    header_fields = get_fit_fields(filename)
    
    # Get the image filter from the header fields or the file name
    # if the filter can not be read from header fields.
    return get_image_filter(header_fields, filename)  

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
    except:
        logging.error("Unknown error reading fit file: " + fit_file_name)             
        
    return header_fields
  
def remove_prefixes(file_name):
    """
    
    This function returned a file where the numeric prefixes, indicated by dots,
    that the file name received can have are removed.
    
    """
    
    # By default the file name returned is the name received.
    final_file_name = file_name 
    
    # Find the position of the character that delimits the end of 
    # the file type part.
    pos_sep = file_name.find(DATANAME_CHAR_SEP)
    
    # Split the name by dots.
    dot_splitted = file_name[:pos_sep].split(".")
    
    # If there is any dot.
    if len(dot_splitted) > 1:
        
        # Indicated the first split that is not removed.
        first_valid_split = 0

        # Iterate over the split discarding the firsts one that are
        # numeric.    
        for s in dot_splitted:
            if s.isdigit(): 
                first_valid_split += 1
            else:
                break
            
        # The splits that are valid are concatenated using dots.
        final_file_name = ".".join(dot_splitted[first_valid_split:]) \
            + file_name[pos_sep:]
        
    return final_file_name 

def file_is_type(header_fields, filename_path, field_type, type_string):
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
                            "' not found in file " + filename_path)       
        
    # If the header field has not been processed.
    if not field_processed:
        
        filename = os.path.split(filename_path)[-1]
        
        # Some files have prefixes with numbers delimited by dots
        # that is necessary to remove to identify the file type.
        clean_filename = remove_prefixes(filename)
        
        # Take only the part that indicates the type.
        type_part = clean_filename[:clean_filename.find(DATANAME_CHAR_SEP)]
        
        print filename_path + " -> " + filename + " -> " + clean_filename + " -> " + type_part
         
        # Check if the type is found in the appropriate part of the file name.
        is_type = type_part.lower() == type_string
        
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
    
    type = file_is_type(header_fields, filename, \
                        BIAS_TYPE, BIAS_STRING)
    
    logging.debug(filename + " is bias is: " + str(type))
    
    return type
    
def file_is_flat(header_fields, filename):    
    """
    
    This function determine if the data received are
    related to a flat file. 
    
    """
    
    type = file_is_type(header_fields, filename, \
                        FLAT_TYPE, FLAT_STRING)
    
    logging.debug(filename + " is flat is: " + str(type))
    
    return type

def get_file_binning(fit_file_name):
    """
    
    Returns the binning of a fit file reading its header.
    The return format is: 1x1, 2x2, and so on.
    
    """
    
    bin = None
    
   # Create a dictionary to retrieve easily the appropriate list
    # using the name of the object.
    header_fields = {}        
    
    try:
        # Open FIT file.
        hdulist = pyfits.open(fit_file_name)
        
        # Get header of first hdu, only one hdu is used.
        header = hdulist[0].header
        
        xbin = header[XBINNING_FIELD_NAME]
        ybin = header[YBINNING_FIELD_NAME]    
        
        bin = str(xbin) + "x" + str(ybin)    
        
        hdulist.close() 
    except IOError as ioe:
        logging.error("Error reading fit file '" + fit_file_name + \
                      "'. Error is: " + str(ioe))
    except KeyError as ke:
        logging.warning("Header field for binning not found in file " + \
                        fit_file_name)   
    except:
        logging.error("Unknown error reading fit file: " + fit_file_name)             
    
    return bin