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
This module searches image files related to a set of objects of interest
whose magnitudes are going to be calculated.

The images are located in a directory with the bias and flats that also
exists for the images found.
"""

import sys
import os
import logging
import glob
import shutil
import csv
from fitfiles import *
from constants import *

# Constants for arguments.
MIN_NUM_ARGS = 3

DEST_DIR_PAR = 0
SRC_DIR_PAR = 1
OBJ_FILE_PAR = 2

def get_files_of_interest(obj_names, files):
    """
    
    This function returns a subset of the file list that
    contains the images corresponding to objects of interest,
    if any, and in this case also returns the bias and flat
    images found. 
    
    """
    
    file_list = []
    file_filter_list = []    
    bias_list = []
    flat_list = []
    flat_filter_list = []    
    
    # Add to the list the files whose name corresponds to a
    # object of interest.
    for f in files:
        # Get some fit header fields that can be used to organize
        # the image.
        header_fields = get_fit_fields(f)   
                
        # Get the file name.
        filename = os.path.split(f)[-1] 
        
        file_start_name = filename.split(DATANAME_CHAR_SEP)[0]
        
        # Determine the file type and add it to the appropriate list,
        # also save the filter for flats and images.
        if file_is_bias(header_fields, f):
            bias_list.extend([f])
            
        elif file_is_flat(header_fields, f):
            flat_list.extend([f])
            flat_filter_list.extend([header_fields[FILTER_FIELD_NAME]])
            
        elif file_start_name in obj_names:
            file_list.extend([f])
            file_filter_list.extend([header_fields[FILTER_FIELD_NAME]])
        
    # If any image file related to any object has been found.
    if len(file_list) > 0:
        
        # Get the set of filter used by images.
        images_filters =  set(file_filter_list)
        
        logging.debug("Found " + str(len(file_list)) + \
                      " image files, " + str(len(bias_list)) + \
                      " bias files and " + str(len(flat_list)) + \
                      " flat files.")
        
        # Add all the bias.
        file_list.extend(bias_list)
                
        # Add only the flats whose filter is used by some image.
        for i in range(len(flat_list)):
            if flat_filter_list[i] in images_filters:
                file_list.extend([flat_list[i]])            

    else:
        logging.debug("No image files found for objects.")
            
    return file_list
    
def copy_files_of_interest(destiny_path, files_of_interest):
    """
    
    This function creates a directory in the path indicated,
    with the name indicated and copy into it all the files
    of interest received.
    
    """
    
    # if destiny directory does not exists, create it.
    if not os.path.exists(destiny_path):
        os.makedirs(destiny_path)
    
    # Copy the files in destiny directory.
    for f in files_of_interest:
        # Get the name of the file.
        filename = os.path.split(f)[-1]
        
        shutil.copyfile(f, os.path.join(destiny_path, filename))

def search_images(destiny_path, source_path, obj_names):
    """
    
    This function search for file images related to the
    object of interest received and copy them to a new
    directory in the path indicated.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk(source_path):
    
        # Inspect only directories without subdirectories.
        if len(dirs) == 0:           
            logging.debug("Found a directory for data: " + path)
            
            split_path = os.path.split(path)

            # Get the list of files.
            files = glob.glob(os.path.join(path, "*" + FIT_FILE_EXT))
            logging.debug("Found " + str(len(files)) + " image files")
            
            files_of_interest = get_files_of_interest(obj_names, files)  
            
            if len(files_of_interest) > 0:            
                # For the destiny directory the name that contains the images 
                # is joined. 
                full_destiny_path = os.path.join(destiny_path, split_path[-1])
                
                copy_files_of_interest(full_destiny_path, files_of_interest)
            
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
            
def main(argv):
    """ 

    Main function. Configure logging, check a correct number of program arguments,
    and read the objects of interest to look for images related to them.

    """  
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging.DEBUG)    
    
    if len(argv) < MIN_NUM_ARGS:
        print str(MIN_NUM_ARGS) + " arguments are needed: " + \
                      "destiny_directory source_directory objects_file"           
    else:
        # Read the objects from the file received.
        obj_names = read_objects_of_interest(argv[OBJ_FILE_PAR])
        
        # Search images for the list of objects into the path indicated.
        search_images(argv[DEST_DIR_PAR], argv[SRC_DIR_PAR], obj_names)
       
            
# Where all begins ...
if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
