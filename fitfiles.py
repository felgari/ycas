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

"""This module groups some functions performed on fit files. """

import logging
import pyfits
from constants import *

DATE_FIELD_NAME = "DATE-OBS"
FILTER_FIELD_NAME = "FILTER"
IMAGE_TYPE_FIELD_NAME = "IMAGETYP"
XBINNING_FIELD_NAME = "XBINNING"
YBINNING_FIELD_NAME = "YBINNING"
CRPIX1 = "CRPIX1"
CRPIX2 = "CRPIX2"

BIAS_TYPE = "BIAS"
FLAT_TYPE = "FLAT"

ORG_FIT_HEADER_FIELDS = [DATE_FIELD_NAME, IMAGE_TYPE_FIELD_NAME, \
                         FILTER_FIELD_NAME]

XY_CENTER_FIT_HEADER_FIELDS = [CRPIX1, CRPIX2]

def search_filter_from_set_in_file_name(filename):
    """ Get from a file name, a filter name belonging to the set filters used. 
    
    Keyword arguments:
    filename -- File name where the filter name is extracted.
    
    Returns:    
    The filter name extracted from the file name, if any.
    
    """
    
    # By default, no filter name.
    filtername = ""
    
    # Remove the extension from the file name.
    filename_no_ext = filename[:-len('.' + FIT_FILE_EXT)]
    
    # Search in the file name, the name of one of the filters in use.
    for f in FILTERS:
        index = filename_no_ext.rfind(f)
        
        # The filter must be at the end of the file name.
        if index + len(f) == len(filename_no_ext) :
            filtername = f
    
    return filtername

def get_image_filter(header_fields, filename):
    """ Returns the filter used for this image, if any. 
    
    At first, the filter is searched in header file. The filter name is part 
    of the file name and is located in a concrete position.
    If it is not found there, the filter is extracted from the file name.
    
    Keyword arguments:
    header_fields -- Header fields of the file. 
    filename -- Name of the file.
    
    Returns:    
    The filter name, if it is identified.
    
    """    

    filtername = ''
    field_processed = False
        
    # Check if any header field has been found.
    if header_fields is not None and len(header_fields) > 0:
        
        # The header field could not have found.
        try:    
            # Retrieve the filter from the header field.
            field_value = header_fields[FILTER_FIELD_NAME]
            
            if field_value is not None and field_value != "":
                field_processed = True
                
                # Remove white spaces.
                filtername = field_value.strip()
        except KeyError as ke:
            logging.warning("Header field '" + FILTER_FIELD_NAME + \
                            "' not found in file " + filename)
            
    # If the header field has not been processed.
    if not field_processed:
        # Get the filter from the file name.
        filtername = search_filter_from_set_in_file_name(filename)
        
    # If the filter has been identified, show the method used.
    if len(filtername) > 0:      
        if field_processed:
            logging.debug(filename + " filter read from file headers: " + \
                          filtername)
        else:
            logging.warning(filename + " filter read from file name: " + \
                            filtername) 
    
    return filtername

def get_image_filter_from_file(filename):
    """ Returns the filter used for this image, if any. 
    
    This function get the header fields and pass them and the file name to
    another function that actually gets the filter name.
    
    Keyword arguments:
    filename -- Name of the file whose filter is requested.
    
    Returns:    
    The filter name, if it is identified.
            
    """    
    
    # Get some fit header fields that can be used to organize
    # the image.
    header_fields = get_fit_fields(filename)
    
    # Get the image filter from the header fields or the file name
    # if the filter can not be read from header fields.
    return get_image_filter(header_fields, filename)  

def get_fit_fields(fit_file_name, fields = ORG_FIT_HEADER_FIELDS):
    """Retrieves the fields of the fit header from the file indicated.
    
    Keyword arguments:
    fit_file_name -- Name of the fit file
    fields -- The fields to return.
    
    Returns:    
    The requested fields found in the file name indicated. 
        
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
        for i in range(len(fields)):
            
            field = fields[i]
            
            # Retrieve and store the value of this field.
            header_fields[field] = header[field]
        
        hdulist.close() 
    except IOError as ioe:
        logging.error("Error reading fit file '" + fit_file_name + \
                      "'. Error is: " + str(ioe))
    except KeyError as ke:
        logging.warning("Header field '" + fields[i] + \
                        "' not found in file " + fit_file_name)   
    except:
        logging.error("Unknown error reading fit file: " + fit_file_name)             
        
    return header_fields
  
def remove_prefixes(file_name):
    """ Returns a file where the numeric prefixes are removed.
    
    The numeric prefixes should be separated by dots.
    
    Keyword arguments:
    file_name -- Name of the file to process.
    
    Returns:    
    The name of the file without prefixes.
        
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
    """Determines if the data received are related to a specific type of file.
     
    First the header fields are evaluated and if the result is not conclusive 
    the file name is analyzed.
    The file name has the the form type-orderfilter.fit'. Where 'type' could be
    'flat', 'bias' or a proper name. A '-' character separates the 'orderfilter'
    part that indicates the ordinal number of the image and optionally a filter,
    only bias has no filter.     
    
    Keyword arguments:
    header_fields -- The headers of the file.
    filename_path -- The path of the file.
    field_type -- The value to compare with that of the fields.
    type_string -- The value expected in the file name to check the type.
    
    Returns:    
        
    """  
    
    is_type = False
    field_processed = False
    
    # Check if any header field has been found.
    if header_fields is not None and len(header_fields) > 0:
        
        # The header field could not have found.
        try:    
            # Retrieve the image type from the header field.
            field_value = header_fields[IMAGE_TYPE_FIELD_NAME]
            
            if field_value is not None and field_value != "":
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
        
        logging.debug(filename_path + " -> " + filename + " -> " + \
                      clean_filename + " -> " + type_part)
         
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
    """Determines if the data received are related to a bias file. 
    
    Keyword arguments:
    header_fields -- Fields from the file header to check if it is a bias.
    filename -- Name of the file.
    
    Returns:    
    True if the file is for a bias, False otherwise.
        
    """
    
    type = file_is_type(header_fields, filename, \
                        BIAS_TYPE, BIAS_STRING)
    
    logging.debug(filename + " is bias is: " + str(type))
    
    return type
    
def file_is_flat(header_fields, filename):    
    """Determine if the data received are related to a flat file. 
    
    Keyword arguments:
    header_fields -- Fields from the file header to check if it is a flat.
    filename -- Name of the file.
    
    Returns:    
    True if the file is for a flat, False otherwise.  
        
    """
    
    type = file_is_type(header_fields, filename, \
                        FLAT_TYPE, FLAT_STRING)
    
    logging.debug(filename + " is flat is: " + str(type))
    
    return type

def get_file_binning(fit_file_name):
    """ Returns the binning of a fit file reading its header.
    
    The return format is: 1x1, 2x2, and so on.
    
    Keyword arguments:
    fit_file_name -- Name of the fit file.
    
    Returns:    
    The binning value, if found.
        
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

def get_rdls_data(rdls_file):
    """Returns the AR, DEC values stores in a RDLS file.
    
    This file is a FIT file that contains a table and this function returns
    the coordinates values in a list.
    
    Keyword arguments:
    rdls_file -- RDLS file where to look for the coordinates. 
    
    Returns:
    A list containing in each item an index, and the AR, DEC for all the 
    coordinates read form the RDLA file.    
    
    """
    
    # Open the FITS file received.
    fits_file = pyfits.open(rdls_file) 

    # Assume the first extension is a table.
    tbdata = fits_file[1].data       
    
    fits_file.close
    
    # Convert data from fits table to a list.
    ldata = list()
    
    # To add an index to the rows.
    n = 1
    
    # Iterate over the table read from the RDLS file.
    for row in tbdata:
        ldata.append([n, row[0], row[1]])
        n += 1
    
    return ldata  