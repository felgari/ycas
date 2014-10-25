#!/usr/bin/python
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
The magnitud values are stored in different files for each object.
"""

import sys
import os
import glob
import pyfits
import csv
from constants import *

# Number of the column that contains the magnitude value.
CSV_TIME_COL = 3 
CSV_MAG_COL = 4 

# Name of the file that contains information about the objects of interest.
INT_OBJECTS_FILE_NAME = "objects.tsv"

# Number of the columns that contains AR and DEC values in each type of file.
OBJECTS_AR_COL_NUMBER = 1
OBJECTS_DEC_COL_NUMBER = 2

MEASURES_AR_COL_NUMBER = 1
MEASURES_DEC_COL_NUMBER = 2
MEASURE_FIRST_COL_NUMBER = 3 

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

def group_measures_for_object(rdls_file, full_dir):
    """
    
    This function generates a text file that groups in a line
    all the photometry measures that exists in a directory for
    a set of object contained in a fit image.
    The output file contains a row for each object with the
    AR, DEC coordinates and the list of values measured for
    the object.
    
    """
    
    # Get RDLS data.
    rdls_data = get_rdls_data(rdls_file)    
    
    # From the file name get the name of the object.
    object_name = rdls_file[0:rdls_file.find(DATANAME_CHAR_SEP)]
    
    # Get the list of files with magnitudes for the images of this object.
    # At this point all the csv are related to magnitude values. 
    csv_files = glob.glob(object_name + "*." + CSV_FILE_EXT)
    
    print "Found " + str(len(csv_files)) + " csv files for object " + object_name
    
    # Sort the list of csv files to ensure a right processing.
    csv_files.sort()
    
    # Read magnitudes from csv files and add it to RDLS data.
    # Each csv file contains the magnitudes for all the object of an image.
    for csv_fl in csv_files:
        
        with open(csv_fl, 'rb') as fr:
            reader = csv.reader(fr)
            
            nrow = 0
            
            for row in reader:
                # Get a list of values from the CSV row read.
                fields = str(row).translate(None, "[]\'").split()
                
                # Add magnitude value to the appropriate row from RDLS file.
                rdls_data[nrow].extend([fields[CSV_MAG_COL]])
                
                nrow += 1
                
    # Write results with all the measures taken, for the object that
    # corresponds to the RDLS file, to a file in tsv format.
    output_file = object_name + "." + TSV_FILE_EXT
    
    print "Writing file: " + output_file
    
    with open(output_file, 'w') as fw:
        
        writer = csv.writer(fw, delimiter='\t')
        
        writer.writerows(rdls_data)
        
def group_measures():
    """
    
    This function searches directories that contains RDLS files.
    When a RDLS file is found, another function is called to
    generate a test file that contains all the photometric measures
    that exists in that directory for the objects related to the
    RDLs file.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of RDLS files ignoring hidden files.
                rdls_files_full_path = \
                    [f for f in glob.glob(os.path.join(full_dir, "*." + RDLS_FILE_EXT)) \
                    if not os.path.basename(f).startswith('.')]
                print "Found " + str(len(rdls_files_full_path)) + " RDLS files"        

                for rdls_file in rdls_files_full_path:
                    group_measures_for_object(rdls_file, full_dir)
                    
def search_mesures_files(obj_name):
    """
    
    This function searches directories that contains files with
    photometric measures.
    The function returns a list that contains all the files with
    measures that has been found.
    
    """
    
    objs_files = list()
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                #print "Found a directory for data: " + full_dir

                # Get the list of RDLS files ignoring hidden files.
                obj_files_full_path = \
                    [f for f in glob.glob(os.path.join(full_dir, obj_name + "*." + TSV_FILE_EXT)) \
                    if not os.path.basename(f).startswith('.')]
                    
                # Add the files found to the list of files for this object.
                objs_files.extend(obj_files_full_path)
        
    return objs_files      

def extract_object_measures(objs_files, ar_str, dec_str):
    """
    
    This function received a set of files and a pair or AR, DEC
    coordinates and returns a list of measures that exists in
    these files for the object whose AR, DEC coordinates are more
    similar to those received.
    
    """
    
    ar = float(ar_str)
    dec = float(dec_str)
    
    measures = list()
                   
    for fl in objs_files:
        
        # Read a file that contains measures.
        with open(fl, 'rb') as fr:
            reader = csv.reader(fr, delimiter='\t')
            
            # These value
            ar_diff = 1000.0
            dec_diff = 1000.0
            
            object_row = None
            
            for row in reader:
                # Identify the measures of the object using the coordinates.
                                  
                # Compute the difference between the coordinates of the
                # object in this row and the object received.  
                temp_ar_diff = abs(float(row[MEASURES_AR_COL_NUMBER]) - ar)
                temp_dec_diff = abs(float(row[MEASURES_DEC_COL_NUMBER]) - dec)   
                
                # If current row coordinates are smaller than previous this
                # row is chosen as candidate for the object.
                if temp_ar_diff+temp_dec_diff < ar_diff+dec_diff:
                    ar_diff = temp_ar_diff
                    dec_diff = temp_dec_diff
                    object_row = row
                    
            # At this point the row of the object has been identified,
            # so save all the measures of this file with the name of the
            # name of the file that contained the measures. 
            measures.extend([[fl] + object_row[MEASURE_FIRST_COL_NUMBER:]])
                     
    return measures    

def save_object_measures(obj_name, measures):
    """
    
    This function receives the name of an object and a set of measures 
    that corresponds to that object and writes this measures to a text
    file with a name that references the object.
    
    """
    
    output_file_name = obj_name + "." + TSV_FILE_EXT
    
    with open(output_file_name, 'w') as fw:
        
        writer = csv.writer(fw, delimiter='\t')
        
        writer.writerows(measures)    

def get_measures_of_objects():
    """
    
    This function read from a text file a list of objects whose
    photometric measures are needed. For each object, this function 
    calls another function that read the measures that exists for 
    an object and returns a list of the measures. 
    This list of measures for an object is saved to a text file.
    
    """
    
    # Read the file that contains the objects of interest.
    with open(INT_OBJECTS_FILE_NAME, 'rb') as fr:
        reader = csv.reader(fr, delimiter='\t')
        
        objects = list()
        
        for row in reader:    
            objects.append(row)
            
    # For each object look for files that contains measures for that object.
    for obj in objects:
        obj_name = obj[0]
        
        print "Searching measures for object: " + obj_name
        objs_files = search_mesures_files(obj_name)
        
        # Sort the files by name to ensure that early measures are processed first.
        objs_files.sort()        
        
        print "Found: " + str(objs_files)
        
        measures = extract_object_measures(objs_files, \
                                               obj[OBJECTS_AR_COL_NUMBER], \
                                               obj[OBJECTS_DEC_COL_NUMBER])
        
        #print "Measures: " + str(measures)
        
        save_object_measures(obj_name, measures)
    
def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv
            
    group_measures()
    
    get_measures_of_objects()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())