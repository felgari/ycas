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
import argparse
from textfiles import *
from fitfiles import *
from constants import *

class ImagesArguments(object):
    """ Encapsulates the definition and processing of program arguments.
        
    """
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ImagesArguments 
        with the definition of arguments to use.

        """   
        
        self.__objects_of_interest_file = INT_OBJECTS_FILE_NAME          
            
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-e", dest="e", action="store_true", \
                                   help='Extract images')
        
        self.__parser.add_argument("-l", dest="l", action="store_true", \
                                   help="List objects found in images")
        
        self.__parser.add_argument("-d", metavar="destiny directory", dest="d", \
                                   help="Destiny directory for images") 
        
        self.__parser.add_argument("-s", metavar="source directory", dest="s", \
                                   help="Source directory for images") 
        
        self.__parser.add_argument("-o", metavar="objects", dest="o", \
                                   help="File containing the objects of interest")
        
    @property    
    def is_extraction(self):        
        return self.__args.e
    
    @property     
    def is_object_list(self):        
        return self.__args.l      
    
    @property    
    def destiny_dir_provided(self): 
        return self.__args.d <> None     
    
    @property
    def destiny_dir(self):
        return self.__args.d        
    
    @property    
    def source_dir_provided(self): 
        return self.__args.s <> None     
    
    @property
    def source_dir(self):
        return self.__args.s       
    
    @property
    def interest_object_file_name(self):
        return self.__objects_of_interest_file      
    
    def parse(self):
        """ 
        
        Initialize properties and performs the parsing 
        of program arguments.
        
        """
        
        # Parse program arguments.
        self.__args = self.__parser.parse_args()
            
        if self.__args.o <> None:
            self.__objects_of_interest_file = self.__args.o    
            
    def print_usage(self):
        """ Print arguments options """
        
        self.__parser.print_usage()              
            
def get_filename_start(path_file):
    """
    
    This function returns the first part of the name of a file,
    this word indicated the file type or the name of the object
    related to this image.
    
    """
    
    # Discard the path and get only the filename.
    filename = os.path.split(path_file)[-1]
    
    # Get only the part of the name until the delimiter.
    filename_start = filename.split(DATANAME_CHAR_SEP)[0]    
    
    # Some file names have suffixes delimited by dots
    # that should be suppressed.    
    return filename_start.split(".")[-1]                

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
        
        # Determine the file type and add it to the appropriate list,
        # also save the filter for flats and images.
        if file_is_bias(header_fields, f):
            bias_list.extend([f])
            
        elif file_is_flat(header_fields, f):
            flat_list.extend([f])
            flat_filter_list.extend([header_fields[FILTER_FIELD_NAME]])
            
        elif get_filename_start(f) in obj_names:
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

def copy_images(destiny_path, source_path, objects_file):
    """
    
    This function search for file images related to the
    object of interest received and copy them to a new
    directory in the path indicated.
    
    """
    
    # Read the objects from the file received.
    objects = read_objects_of_interest(objects_file)
    
    # Get the names of the objects.
    obj_names = [ o[OBJ_NAME_COL] for o in objects]    
    
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

def list_objects_in_files(source_dir):
    """
    This function walks the directory and create a list of the
    objects with images.
    
    """
    
    objects = []
    
    logging.debug("Creating a list of objects with images from: " + source_dir)
    
    # Walk from current directory.
    for path,dirs,files in os.walk(source_dir):
    
        # Inspect only directories without subdirectories.
        if len(dirs) == 0:           
            logging.debug("Found a directory for images: " + path)
            
            split_path = os.path.split(path)

            # Get the list of files.
            files = glob.glob(os.path.join(path, "*" + FIT_FILE_EXT))
            
            logging.debug("Found " + str(len(files)) + " image files")
            
            # Process all the files found.
            for f in files:
                header_fields = get_fit_fields(f)
                
                # Determine the file type to exclude bias and flat.
                if ( not file_is_bias(header_fields, f) ) and \
                    ( not file_is_flat(header_fields, f) ):
                         
                    # Get only the name of the file.
                    filename_start = get_filename_start(f)  
            
                    objects.extend([filename_start])
                    
    # Get a set with the names of the objects only once.
    objects_set = set(objects)
                    
    print "Objects: " +  str(objects_set)               
            
def main(progargs):
    """ 

    Main function. Configure logging, check a correct number of program arguments,
    and read the objects of interest to look for images related to them.

    """  
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging.DEBUG)   
    
    progargs.parse()    
    
    if progargs.is_extraction:
        if progargs.destiny_dir_provided and \
            progargs.source_dir_provided:
            
            logging.debug("Copying images for the objects indicated to the destiny directory.")            
            
            # Copy images for the list of objects into the path indicated.
            copy_images(progargs.destiny_dir, \
                        progargs.source_dir, \
                        progargs.interest_object_file_name)      
        else:
            print "The following arguments are needed: " + \
                          "destiny_directory source_directory objects_file" 
                          
    elif progargs.is_object_list:
        list_objects_in_files(progargs.source_dir)
       
            
# Where all begins ...
if __name__ == "__main__":
    
    # Create object to process program arguments.
    progargs = ImagesArguments()      
    
    if len(sys.argv) <= 1:
        progargs.print_usage()
        sys.exit(1)
    else: 
        sys.exit(main(progargs))
