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
This module organize the files to process into different directories
depending on the type of image: bias, flat or data.
The module assume that images are initially stored in directories that 
corresponds to the day which were taken.
Into each day the images are organized in a directory for bias, another
for flats and another for data.
Also flats and data images are organized in different subdirectories,
one for each filter. 
"""

import sys
import os
import logging
import yargparser
import shutil
import pyfits
from constants import *

FILTER_FIELD_NAME = "FILTER"
IMAGE_TYPE_FIELD_NAME = "IMAGETYP"

BIAS_TYPE = "BIAS"
FLAT_TYPE = "FLAT"

ORG_FIT_HEADER_FIELDS = ["DATE-OBS", IMAGE_TYPE_FIELD_NAME, FILTER_FIELD_NAME]

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

def create_directory(path, dirname):
    """ Create a directory with the given name. 
    
    This function creates a directory with the given name located in the
    path received.
    
    """

    complete_dirname = os.path.join(path,dirname)

    # Check if the directory exists.
    if not os.path.exists(complete_dirname):
        try: 
            logging.debug("Creating directory: " + complete_dirname)
            os.makedirs(complete_dirname)
        except OSError:
            if not os.path.isdir(complete_dirname):
                raise
            
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
        # Get the type from the file name.
        is_type = filename.startswith(type_string)
        
    # If the type has been identified, show the method used.
    if is_type:      
        if field_processed:
            logging.debug(filename + " organized using file headers.")
        else:
            logging.warning(filename + " organized using file name.")        
    
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

def analyze_and_organize_dir(filename, path, progargs):
    """ 
    
    This function determines the file type and moves the
    files to the proper directory created for that type of file.
    	
    """

    full_file_name = os.path.join(path, filename)
    
    # Get some fit header fields that can be used to organize
    # the image.
    header_fields = get_fit_fields(full_file_name)

    # If the file is a bias.
    if file_is_bias(header_fields, full_file_name):
        create_directory(path, progargs.bias_directory)

        file_destination = os.path.join(path, progargs.bias_directory, filename)
        
        logging.debug(full_file_name + " identified as bias.")

    # If the file is a flat.
    elif file_is_flat(header_fields, full_file_name):
        create_directory(path, progargs.flat_directory)

        filtername = get_image_filter(header_fields, filename)

        if len(filtername) > 0:
            create_directory(path, os.path.join(progargs.flat_directory, filtername))

        file_destination = os.path.join(path, progargs.flat_directory, filtername, filename)
        
        logging.debug(full_file_name + " identified as flat.")

    # Otherwise the file is considered a data image.
    else:
        create_directory(path, progargs.data_directory)

        filtername = get_image_filter(header_fields, filename)

        if len(filtername) > 0:
            create_directory(path, os.path.join(progargs.data_directory, filtername))

        file_destination = os.path.join(path, progargs.data_directory, filtername, filename)
        
        logging.debug(full_file_name + " identified as data image.")

    logging.debug("Moving '" + full_file_name + "' to '" + file_destination + "'")

    shutil.move(os.path.abspath(full_file_name),
                os.path.abspath(file_destination))
    
def ignore_current_directory(dir, progargs):
    """ Determines if current directory should be ignored.
    
    A directory whose name matches that of bias, flat or data directories or
    has a parent directory named as a flat or data directory, it is ignored 
    as this directory could be a directory created in a previous run and a new
    bias/flat/data directory should be created from them 
    
    """
    ignore  = False
    
    head, current_directory = os.path.split(dir)
    rest, parent_directrory = os.path.split(head)
    
    if current_directory == progargs.bias_directory or \
        current_directory == progargs.flat_directory or \
        parent_directrory == progargs.flat_directory or \
        current_directory == progargs.data_directory or \
        parent_directrory == progargs.data_directory:
        ignore  = True
    
    return ignore    

def organize_files(progargs):
    """ Search directories with images to organize.
    
    This function walks the directories searching for image files,
    when a directory with image files is found the directory contents
    are analyzed and organized.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Check if current directory could be created previously
        # to contain bias or flat,  in that case the directory is ignored.        
        if ignore_current_directory(path, progargs):
            logging.debug("Ignoring directory: " + path)
        else:
            # For each file move it to he proper directory.
            for fn in files:
                # The extension is the final string of the list 
                # without the initial dot.
                filext = os.path.splitext(fn)[-1][1:]
    
                if filext == FIT_FILE_EXT:
                    # Analyze name.
                    logging.debug("Analyzing: " + os.path.join(path, fn))
                    analyze_and_organize_dir(fn, path, progargs)
                else:
                    logging.debug("Ignoring file: " + fn)
