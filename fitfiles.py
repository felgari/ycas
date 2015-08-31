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

import os
import logging
import pyfits
import fitsheader
from constants import *

# First index for a FIT table.
FIT_FIRST_TABLE_INDEX = 1

XBINNING_FIELD_NAME = "XBINNING"
YBINNING_FIELD_NAME = "YBINNING"

BIAS_TYPE = "BIAS"
FLAT_TYPE = "FLAT"

def search_filter_from_set_in_file_name(filename):
    """ Get from a file name, a filter name belonging to the set filters used. 
    
    Args:
        filename: File name where the filter name is extracted.
    
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

def get_fit_fields(fit_file_name, fields):
    """Retrieves the fields of the fit header from the file indicated.
    
    Args:
        fit_file_name: Name of the fit file
        fields: The fields to return.
    
    Returns:    
        The requested fields found in the file name indicated. 
        
    """
    
    logging.debug("Extracting header fields for: %s" % (fit_file_name))
    
    # Create a dictionary to retrieve easily the appropriate list
    # using the name of the object.
    header_fields = {}        
    
    try:
        # Open FIT file.
        hdulist = pyfits.open(fit_file_name)
        
        # Get header of first hdu, only one hdu is used.
        header = hdulist[0].header
        
        # For all the header fields of interest.
        for f in fields:
            
            # Retrieve and store the value of this field.
            header_fields[f] = header[f]
        
        hdulist.close()
        
    except IOError as ioe:
        logging.error("Error reading fit file: '%s'. Error is: %s." % 
                      (fit_file_name, ioe))
        
    except KeyError as ke:
        logging.warning("Header field '%s' not found in file %s." %
                        (f,fit_file_name))   
    except:
        logging.error("Unknown error reading fit file: %s." % (fit_file_name))             
        
    # If the object has not the field for tha name, add it with the default 
    # value.
    if not fitsheader.DEFAULT_OBJECT_NAME in header_fields:
        header_fields[fitsheader.DEFAULT_OBJECT_NAME] = \
            fitsheader.DEFAULT_OBJECT_NAME
        
    return header_fields
  
def remove_prefixes(file_name):
    """ Returns a file where the numeric prefixes and of other types are removed.
    
    The numeric prefixes should be separated by dots.
    
    Args:
        file_name: Name of the file to process.
    
    Returns:    
        The name of the file without prefixes.
        
    """
    
    # By default the file name returned is the name received.
    final_file_name = file_name 
    
    # Split the name by dots.
    dot_splitted = file_name.split(".")
    
    # If there is more than one dot. Join the last two plus the previous that
    # contains at least one letter. 
    if len(dot_splitted) > 1:        
        final_file_name = "%s.%s" % (dot_splitted[-2], dot_splitted[-1])
        
        for i in range(3, len(dot_splitted) + 1):
            if any(c.isalpha() for c in dot_splitted[-i]):
                final_file_name = "%s.%s" % (dot_splitted[-i], final_file_name)
        
    if not ( final_file_name[0].isdigit() or final_file_name[0].isalpha() ):
        final_file_name = final_file_name[1:]
        
    logging.debug("Removing prefixes: %s to %s" % (file_name, final_file_name))
        
    return final_file_name 

def file_is_type(header_fields, filename_path, field_type, type_string):
    """Determines if the data received are related to a specific type of file.
     
    First the header fields are evaluated and if the result is not conclusive 
    the file name is analyzed.
    The file name has the the form type-orderfilter.fit'. Where 'type' could be
    'flat', 'bias' or a proper name. A '-' character separates the 'orderfilter'
    part that indicates the ordinal number of the image and optionally a filter,
    only bias has no filter.     
    
    Args:
        header_fields: The headers of the file.
        filename_path: The path of the file.
        field_type: The value to compare with that of the fields.
        type_string: The value expected in the file name to check the type.
    
    Returns:    
        True if it is the type indicated, False otherwise.
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
            logging.debug("%s type using file headers." % (filename))
        else:
            logging.warning("%s type using file name." % (filename))        
    
    return is_type       

def file_is_bias(file_header, header_fields_names):    
    """Determine if the file received corresponds to a bias image. 
    
    Args:
        file_header: Fields from the file header to check if it is a bias.
        header_fields_names: Information about the headers fields of FIT files.
    
    Returns:    
        True if the file is for a bias, False otherwise.
        
    """
    
    is_type = file_header[header_fields_names.image_type] == \
                header_fields_names.bias_value
    
    logging.debug("%s is bias is: %s" % (filename, str(is_type)))
    
    return is_type
    
def file_is_flat(file_header, header_fields_names):    
    """Determine if the file received corresponds to a flat image. 
    
    Args:
        file_header: Fields from the file header to check if it is a bias.
        header_fields_names: Information about the headers fields of FIT files.
    
    Returns:    
        True if the file is for a flat, False otherwise.  
        
    """
    
    return file_header[header_fields_names.image_type] == \
                header_fields_names.flat_value

def get_file_binning(fit_file_name):
    """ Returns the binning of a fit file reading its header.
    
    The return format is: 1x1, 2x2, and so on.
    
    Args:
        fit_file_name: Name of the fit file.
    
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
        logging.error("Error reading fit file '%s'. Error is: %s" % 
                      (fit_file_name, ioe))
    except KeyError as ke:
        logging.warning("Header field for binning not found in file: '%s'" %
                        (fit_file_name))   
    except:
        logging.error("Unknown error reading fit file: '%s'" % (fit_file_name))             
    
    return bin

def get_fit_table_data(fit_table_file_name):
    """Get the data of a the first table contained in the fit file indicated.
    
    Args:
        fit_table_file_name: File name of the fit file that contains the table.
    
    Returns:
        The table contained in the fit file.
        
    """
    
    ldata = None
    
    try:
        # Open the FITS file received.
        fit_table_file = pyfits.open(fit_table_file_name) 
    
        # Assume the first extension is a table.
        table_data = fit_table_file[FIT_FIRST_TABLE_INDEX].data    
        
        fit_table_file.close()
        
        # Convert data from fits table to a list.
        ldata = list()
        
        # To add an index to the rows.
        n = 1
        
        # Read the table data and save it in a list.
        for row in table_data:
            ldata.append([row[0], row[1]])
            n += 1
        
    except IOError as ioe:
        logging.error("Opening file: '%s'." % (fit_table_file_name))            
    
    return ldata

def get_header_value(file_name, field):
    """Returns the value of a field in the header of a FIT file.
    
    Args:
        file_name: Name of the file.
        field: Field to get.
        
    Returns:
        The value of the field.
    
    """
    
    value = None
    
    # Get value of the field.
    try:
        # Open FIT file.
        hdulist = pyfits.open(file_name)   
             
        value = hdulist[0].header[field].strip()
        
        hdulist.close()  
        
        logging.debug("Star %s identified for file %s." %
                      (value, file_name))
        
    except IOError as ioe:
        logging.error("Opening file: '%s'." % (file_name))    
              
    except KeyError as ke:
        logging.error("Field '%s' not found in file '%s'." %
                      (field, file_name))    
    
    return value

def get_star_name_from_file_name(file_name):
    """Sometimes the header doesn't contain the name of the star, in these
    cases, the name could be obtained from the file name
    
    Args:
        file_name: Name of the file.
        
    Returns:
        The name of the object obtained from the file name.
    
    """
    
    # Split file name from the path.
    _, file = os.path.split(file_name)
    
    # Get the star name from the filename, the name is at 
    # the beginning and separated by a special character.
    return file.split(DATANAME_CHAR_SEP)[0]    