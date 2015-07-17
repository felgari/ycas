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

"""This module organize the files to process into different directories.

The organization takes into account the session (day) where was taken and 
the type of the image: bias, flat or data.
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
from fitfiles import *
from constants import *

def create_directory(path, dirname):
    """ Create a directory with the given name. 
    
    This function creates a directory with the given name located in the
    path received.
    
    Keyword arguments: 
    path -- Path where the directory is created.
    dirname -- Name of the directory to create.
    
    """

    complete_dirname = os.path.join(path, dirname)

    # Check if the directory exists.
    if not os.path.exists(complete_dirname):
        try: 
            logging.debug("Creating directory: " + complete_dirname)
            os.makedirs(complete_dirname)
        except OSError:
            if not os.path.isdir(complete_dirname):
                raise  

def analyze_and_organize_dir(filename, path, progargs):
    """Establish the type of each file and copies it to the appropriate folder. 
    
    This function determines the file type and moves the
    files to the proper directory created for that type of file.
    
    First try, is to establish the type of each file looking the file header,
    of not possible the name of the file is used.
    
    Keyword arguments:     
    filename  -- Name of the file to analyze.
    path -- Path where is the file.
    progargs -- Program arguments.
    	
    """

    full_file_name = os.path.join(path, filename)
    
    header_fields = None
    
    # If the use of header fields has been indicated, use them.
    if progargs.use_headers_to_get_image_type:
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
            create_directory(path, os.path.join(progargs.flat_directory, \
                                                filtername))

        file_destination = os.path.join(path, progargs.flat_directory, \
                                        filtername, filename)
        
        logging.debug(full_file_name + " identified as flat.")

    # Otherwise the file is considered a data image.
    else:
        create_directory(path, progargs.data_directory)

        filtername = get_image_filter(header_fields, filename)

        if len(filtername) > 0:
            create_directory(path, os.path.join(progargs.data_directory, \
                                                filtername))

        # Prefixes are removed from file name.
        file_destination = os.path.join(path, progargs.data_directory, \
                                        filtername, remove_prefixes(filename))
        
        logging.debug(full_file_name + " identified as data image.")

    logging.debug("Moving '" + full_file_name + "' to '" + \
                  file_destination + "'")

    shutil.move(os.path.abspath(full_file_name),
                os.path.abspath(file_destination))
    
def ignore_current_directory(dir, progargs):
    """ Determines if current directory should be ignored.
    
    A directory whose name matches that of bias, flat or data directories or
    has a parent directory named as a flat or data directory is ignored, 
    as this directory could be a directory created in a previous run and a new
    bias/flat/data and redundant directory should be created for it.
    
    Keyword arguments:
    dir -- Directory to process.
    progargs -- Program arguments.  
    
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

def get_binnings_of_images(data_path):
    """Returns the binnings used for the images in the path indicated.
    
    Keyword arguments:    
    data_path -- Directory with full path with images to analyze.
    
    Returns:
    The list of binning used for the data images in the directory indicated.
    
    """
    
    binnings = []
    
    # Walk from current directory.
    for path,dirs,files in os.walk(data_path):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            
            # Get the binning of each file in the directory.
            for f in files:
                path_file = os.path.join(path,f)
                
                bin = get_file_binning(path_file)
    
            # If the binning has been read.
            if bin is not None:
                # If this binning has not been found yet, add it.
                if not bin in binnings:
                    binnings.extend([bin])
                    
    if len(binnings) > 1:
        logging.warning("Images with more that one binning " + \
                        str(binnings) + " in: " + data_path)
            
    return binnings

def remove_images_with_diff_binning(data_path, binnings):
    """Remove images with a binning not included in the binnings received.
    
    Keyword arguments:    
    data_path -- Path that contains the images to analyze.
    binnings -- List of binnings to consider.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk(data_path):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            
            # Get the binning of each file in the directory.
            for f in files:
                path_file = os.path.join(path,f)
                
                bin = get_file_binning(path_file)
    
                # If the binning has been read.
                if bin is not None:
                    # If this binning has not been in the list of binnings,
                    # remove the image.
                    if not bin in binnings:
                        logging.debug("Removing file '" + path_file + \
                                      "' with binning " + str(bin) + \
                                      " not needed " + str(binnings))
                                                
                        os.remove(path_file) 
                else:
                    logging.warning("Binning not read for: " + path_file)  
    

def remove_dir_if_empty(source_path):
    """Check if the directory is empty and in that case is removed.
    
    Keyword arguments:    
    source_path -- Path to analyze.
        
    """
    
    # If current directory is empty, remove it.
    if os.listdir(source_path) == []:
        logging.debug("Removing empty directory: " + source_path)
        try:
            os.rmdir(source_path)
        except OSError as oe:
            logging.error("Removing directory " + source_path)
            logging.error("Error is: " + str(oe))
    else:        
        # Walk from current directory.
        for path,dirs,files in os.walk(source_path):
    
            # Iterate over the directories.
            for d in dirs:
                remove_dir_if_empty(os.path.join(path,d))

def remove_images_according_to_binning(path):
    """Remove bias and flat whose binning doesn't match that of the data images.
    
    Analyzes the binning of the bias and flat images and remove those whose 
    binning does not match that of the data images.
    
    Keyword arguments:    
    path -- Path where the analysis of the images should be done.
        
    """
    
    data_path = os.path.join(path, DATA_DIRECTORY)
    
    # If current path has data directory, process bias and flats
    if os.path.exists(data_path):
    
        logging.debug("Removing bias and flats with a binning not needed " + \
                      "in: " + path)
        
        # Get the binning of images in data directory.
        binnings = get_binnings_of_images(data_path)
        
        # Remove images in bias directory with different binning of that of 
        # images.
        bias_path = os.path.join(path, BIAS_DIRECTORY)
        
        if os.path.exists(bias_path):
            remove_images_with_diff_binning(bias_path, binnings)
            
            # If now bias directory is empty is removed.
            remove_dir_if_empty(bias_path)
                
        # Remove images in flat directory with different binning of that of 
        # images.
        flat_path = os.path.join(path, FLAT_DIRECTORY)
        
        if os.path.exists(flat_path):
            remove_images_with_diff_binning(flat_path, binnings)   
            
            # If now flat directory is empty is removed.
            remove_dir_if_empty(flat_path)

def organize_files(progargs):
    """ Search directories with images to organize.
    
    This function walks the directories searching for image files,
    when a directory with image files is found the directory contents
    are analyzed and organized.
    
    Keyword arguments:    
    progargs -- Program arguments.
    
    Returns:    
        
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Check if current directory could be created previously
        # to contain bias or flat, in that case the directory is ignored.        
        if ignore_current_directory(path, progargs):
            logging.debug("Ignoring directory for organization: " + path)
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
                    
        # Check the directory to remove bias and flat
        # with a binning differente of that of data images.
        remove_images_according_to_binning(path)