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
This module obtains the magnitude of a set of object using the photometry
values calculated previously.
The magnitude values are stored in different files for each object.
"""

import sys
import os
import logging
import yargparser
import glob
import pyfits
import csv
from constants import *

def get_object_name_from_rdls(rdls_file):
    
    # From the file name get the name of the object.
    object_name_with_path = rdls_file[0:rdls_file.find(DATANAME_CHAR_SEP)]
     
    return os.path.basename(object_name_with_path)     

def get_ar_dec_for_object(objects, object_name):
    """
    
    This function receives the name of an object and the set of objects
    and returns the coordinates for that object contained in the
    list of objects.
    
    """
    
    ar = 0.0
    dec = 0.0
    
    for obj in objects:
        if obj[OBJ_NAME_COL] == object_name:
            ar = float(obj[OBJ_AR_COL])
            dec = float(obj[OBJ_DEC_COL])
    
    return ar, dec

def read_objects_of_interest(progargs):
    """
        
    Read the list of objects of interest from the file indicated.
    This file contains the name of the object and the AR, DEC 
    coordinates of each object.
    
    """
    
    objects = list()
    
    # Read the file that contains the objects of interest.
    with open(progargs.interest_object_file_name, 'rb') as fr:
        reader = csv.reader(fr, delimiter='\t')        
        
        for row in reader:    
            objects.append(row)   
            
    logging.info("Read the following objects: " +  str(objects))            
            
    return objects     

def get_rdls_data(rdls_file):
    """
    
    This function returns the AR, DEC values stores in a RDLS
    file generated during the photometry step.
    This file is a FIT file that contains a table and this
    function returns the values in a list.
    
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
    
    for row in tbdata:
        ldata.append([n, row[0], row[1]])
        n += 1
    
    return ldata  

def get_object_references(rdls_file, objects):
    """
    
    This function takes and RDLS file and a list of objects and 
    returns the index in the RDLS file whose coordinates get the
    better match for those of the object and also the name of the
    object.
    
    """
    
    index = -1
    
    # Get the name of the object related to this RDLS file.
    object_name = get_object_name_from_rdls(rdls_file)
    
    # Get coordinates for the object related to the RDLS file.
    ar, dec = get_ar_dec_for_object(objects, object_name)    
    
    # Get RDLS data.
    rdls_data = get_rdls_data(rdls_file) 
    
    ar_diff = 1000.0
    dec_diff = 1000.0 
    
    i = 0
    for rd in rdls_data:
        # Compute the difference between the coordinates of the
        # object in this row and the object received.  
        temp_ar_diff = abs(float(rd[RDLS_AR_COL_NUMBER]) - ar)
        temp_dec_diff = abs(float(rd[RDLS_DEC_COL_NUMBER]) - dec)   
        
        # If current row coordinates are smaller than previous this
        # row is chosen as candidate for the object.
        if temp_ar_diff < ar_diff and temp_dec_diff < dec_diff:
            ar_diff = temp_ar_diff
            dec_diff = temp_dec_diff
            index = i        
    
        i += 1
        
    logging.info("Found index for object " + object_name + " at " + str(index))
        
    return index, object_name    

def get_measurements_for_object(rdls_file, path, objects):
    """
    
    This function search in a given path all the files related to
    an object that contains measurements for that object.
    
    """
    
    # Get the index of this object in the files that contains the measurements.
    object_index, object_name = get_object_references(rdls_file, objects)
    
    # Get the list of files with magnitudes for the images of this object.
    # At this point all the csv are related to magnitude values. 
    csv_files = glob.glob(os.path.join(path, object_name + "*." + CSV_FILE_EXT))
    
    # The name of the directory that contains the file is the name of the filter
    path_head, filter_name = os.path.split(path)
    
    logging.info("Found " + str(len(csv_files)) + " csv files for object " \
                 + object_name)
    
    # Sort the list of csv files to ensure a right processing.
    csv_files.sort()
    
    # To store the measurements.
    measurements = list()
    
    # Read magnitudes from csv files and add it to RDLS data.
    # Each csv file contains the magnitudes for all the object of an image.
    for csv_fl in csv_files:
        
        with open(csv_fl, 'rb') as fr:
            reader = csv.reader(fr)
            
            nrow = 0
            
            for row in reader:
            
                # Check if current row corresponds to the object.
                if nrow == object_index:
                    # Get a list of values from the CSV row read.
                    fields = str(row).translate(None, "[]\'").split()
                    
                    # Add magnitude value to the appropriate row from RDLS file.
                    measurements.append([fields[CSV_TIME_COL], fields[CSV_MAG_COL], filter_name])
                
                nrow += 1
                
    return measurements 


def compile_measurements_of_objects(objects):
    """
    
    This function receives a list of object and compiles in a text
    file all the measurements found for each object.
    
    """
    
    # For each object a list is created to store its measurements.
    # In turn, all these lists are grouped in a list. 
    objects_measurements = list()
    
    # Create a dictionary to retrieve easily the appropriate list
    # using the name of the object.
    objects_index = {}
    
    for i in range(len(objects)):
        objects_measurements.append([])
        
        objects_index[objects[i][OBJ_NAME_COL]] = i
        
    # Walk all the directories searching for files containing measurements.
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
               
                logging.info("Found a directory with data images: " + path)

                # Get the list of RDLS files ignoring hidden files.
                rdls_files_full_path = \
                    [f for f in glob.glob(os.path.join(path, "*." + RDLS_FILE_EXT)) \
                    if not os.path.basename(f).startswith('.')]
                    
                logging.info("Found " + str(len(rdls_files_full_path)) + \
                             " RDLS files")        

                # Process the images of each object that has a RDLS file.
                for rdls_file in rdls_files_full_path:
                    
                    # Get the measurements for this object in current path.
                    me = get_measurements_for_object(rdls_file, path, objects)
                    
                    # If any measurement has been get.
                    if len(me) > 0:
                        # Get the name of the object.
                        object_name = get_object_name_from_rdls(rdls_file)                    
                        
                        try:
                            # Retrieve the list that contains the measurements 
                            # for this object.
                            measurements_index = objects_index[object_name]
                        
                            object_mea_list = objects_measurements[measurements_index]
                        
                            # Add the measurement to the object.
                            object_mea_list.append(me)
                        except KeyError as ke:
                            logging.error("RDLS file with no object of interest: " + \
                                          object_name)
                        
    return objects_measurements

def save_objects_measurements(objects, objects_measurements):
    """
    
    This function saves the measurements of each object in a different
    file.
    
    """
    
    # For each object. The two list received contains the same 
    # number of objects.
    for i in range(len(objects)):
        
        # Get the name of the output file.
        output_file_name = objects[i][OBJ_NAME_COL] + "." + TSV_FILE_EXT
        
        # Get the measurements for this object
        measurements = objects_measurements[i]
    
        with open(output_file_name, 'w') as fw:
            
            writer = csv.writer(fw, delimiter='\t')

            # It is a list that contains sublists, each sublist is
            # a different measurement, so each one is written as a row.
            for me in measurements:
            
                # Write each measurement in a row.
                writer.writerows(me)  
    
                                       
def compile_objects_measurements(progargs):
    """ 

    Get the magnitudes of the objects grouping all the measurements calculated.

    """
    
    # Read the list of objects whose measurements are needed.
    objects = read_objects_of_interest(progargs)
    
    objects_measurements = compile_measurements_of_objects(objects)
    
    save_objects_measurements(objects, objects_measurements)
