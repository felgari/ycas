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
import numpy as np
from scipy import stats

def get_object_name_from_rdls(rdls_file):
    
    # From the file name get the name of the object.
    object_name_with_path = rdls_file[0:rdls_file.find(DATANAME_CHAR_SEP)]
     
    return os.path.basename(object_name_with_path)     

def get_ra_dec_for_object(objects, object_name):
    """
    
    This function receives the name of an object and the set of objects
    and returns the coordinates for that object contained in the
    list of objects.
    
    """
    
    ra = 0.0
    dec = 0.0
    
    for obj in objects:
        if obj[OBJ_NAME_COL] == object_name:
            ra = float(obj[OBJ_RA_COL])
            dec = float(obj[OBJ_DEC_COL])
    
    return ra, dec

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
    ar, dec = get_ra_dec_for_object(objects, object_name)    
    
    # Get RDLS data.
    rdls_data = get_rdls_data(rdls_file) 
    
    ra_diff = 1000.0
    dec_diff = 1000.0 
    
    i = 0
    for rd in rdls_data:
        # Compute the difference between the coordinates of the
        # object in this row and the object received.  
        temp_ra_diff = abs(float(rd[RDLS_RA_COL_NUMBER]) - ar)
        temp_dec_diff = abs(float(rd[RDLS_DEC_COL_NUMBER]) - dec)   
        
        # If current row coordinates are smaller than previous this
        # row is chosen as candidate for the object.
        if temp_ra_diff < ra_diff and temp_dec_diff < dec_diff:
            ra_diff = temp_ra_diff
            dec_diff = temp_dec_diff
            index = i        
    
        i += 1
        
    logging.info("Found index for object " + object_name + " at " + str(index))
        
    return index, object_name    

def get_inst_magnitudes_for_object(rdls_file, path, objects):
    """
    
    This function search in a given path all the files related to
    an object that contains magnitudes for that object.
    
    """
    
    # Get the index of this object in the files that contains the magnitudes.
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
    
    # To store the magnitudes.
    magnitudes = list()
    
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
                    magnitudes.append([fields[CSV_TIME_COL], 
                                         fields[CSV_MAG_COL],
                                         fields[CSV_AIRMASS_COL], 
                                         filter_name])
                
                nrow += 1
                
    return magnitudes 

def compile_instrumental_magnitudes(objects):
    """
    
    This function receives a list of object and compiles in a text
    file all the magnitudes found for each object.
    
    """
    
    # For each object a list is created to store its magnitudes.
    # In turn, all these lists are grouped in a list. 
    instrumental_magnitudes = list()
    
    # Create a dictionary to retrieve easily the appropriate list
    # using the name of the object.
    objects_index = {}
    
    for i in range(len(objects)):
        instrumental_magnitudes.append([])
        
        objects_index[objects[i][OBJ_NAME_COL]] = i
        
    # Walk all the directories searching for files containing magnitudes.
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
                    
                    # Get the magnitudes for this object in current path.
                    im = get_inst_magnitudes_for_object(rdls_file, path, objects)
                    
                    # If any magnitude has been get.
                    if len(im) > 0:
                        # Get the name of the object.
                        object_name = get_object_name_from_rdls(rdls_file)                    
                        
                        try:
                            # Retrieve the list that contains the magnitudes 
                            # for this object.
                            magnitudes_index = objects_index[object_name]
                        
                            object_mea_list = instrumental_magnitudes[magnitudes_index]
                        
                            # Add the magnitude to the object.
                            object_mea_list.append(im)
                        except KeyError as ke:
                            logging.error("RDLS file with no object of interest: " + \
                                          object_name)
                        
    return instrumental_magnitudes

def save_instrumental_magnitudes(object_name, inst_magnitudes_obj):
    """
    
    Save the instrumental magnitudes to a text file.
    
    """
    
    # Get the name of the output file.
    output_file_name = object_name + INST_MAG_SUFFIX + "." + TSV_FILE_EXT

    # Instrumental magnitudes are stored in files.
    with open(output_file_name, 'w') as fw:
        
        writer = csv.writer(fw, delimiter='\t')

        # It is a list that contains sublists, each sublist is
        # a different magnitude, so each one is written as a row.
        for imag in inst_magnitudes_obj:
        
            # Write each magnitude in a row.
            writer.writerows(imag)    
            
def get_day_of_measurement(time_jd):
    """
    
    Returns the julian day that is assigned to this value.
    The day is assigned to that which the night begins.
    So a JD between .0 (0:00:00) and .4 (+8:00:00) belongs 
    to the day before.
    
    """    
    
    day = None
    
    dot_pos = time_jd.find('.')
    
    first_decimal = time_jd[dot_pos + 1]
    
    int_first_decimal = int(first_decimal) 
    
    if int_first_decimal >= 0 and int_first_decimal <= 4:
        day = str(int(time_jd[:dot_pos]) - 1)
    else:
        day = time_jd[:dot_pos]
    
    return day

def get_standard_magnitude(object_data, filter):
    """
    
    Get the standard magnitude of an object in the filter indicated.
    
    """
    
    std_mag = None
    
    # Depending on the filter name received get the appropriate column.
    if filter == B_FILTER_NAME:
        std_mag = object_data[OBJ_B_MAG_COL]
    elif filter == V_FILTER_NAME:
        std_mag = object_data[OBJ_V_MAG_COL]      
    elif filter == R_FILTER_NAME:
        std_mag = object_data[OBJ_R_MAG_COL]       
        
    return std_mag

def calculate_extinction_coefficient(mag_data):
    """
    
    Calculate the extinction coefficient using the data received.
    
    """
    
    # Create a numpy array with the data received.
    a = np.array(mag_data)
    
    # Sort the data only by JD time.
    na = a[a[:,JD_TIME_CE_COL].argsort()]
    
    # Extract the columns necessary to calculate the linear regression.
    inst_mag = na[:,INST_MAG_CE_COL]
    std_mag = na[:,STD_MAG_CE_COL]
    airmass = na[:,AIRMASS_CE_COL]
    
    # Subtract these columns to get the y.
    y = inst_mag.astype(np.float) - std_mag.astype(np.float)
    
    # The calculation is:
    # Minst = Mo + K * airmass
    # Where K is the regression coeficcient 
    slope, intercept, r_value, p_value, std_err = \
        stats.linregress(airmass.astype(np.float), y)
    
    logging.info("Lineal regression for day: " + str(a[0][DAY_CE_COL]) +
                 " slope: " + str(slope) + " intercept: " + str(intercept) + \
                 " r-value: " + str(r_value) + " p-value: " + str(p_value) + \
                 " std_err: " + str(std_err))
    
    return slope, intercept
    
def get_extinction_coefficient(objects, \
                                     standard_obj_index,\
                                     instrumental_magnitudes):
    """
    
    Calculate the atmospheric extinction coefficient using the standard objects.
    
    """
    
    ext_coef = []
    
    # To store all the magnitudes
    all_magnitudes = []
    
    # To store the different days and filters.
    days = set()
    filters = set()    
    
    # Process each standard object.
    for i in standard_obj_index:
                
        # Retrieve the object data and the instrumental magnitudes measured.
        obj = objects[i]   
        object_inst_mags = instrumental_magnitudes[i]
        
        # Process the instrumental magnitudes measured for this object.
        for inst_mag in object_inst_mags:
            # For each object the magnitudes are grouped in different lists.
            for im in inst_mag:

                day = get_day_of_measurement(im[JD_TIME_COL])
                
                days.add(day)
                
                std_mag = get_standard_magnitude(obj, im[FILTER_COL])
                
                # Check that a standard magnitude has been found for
                # this object and filter.
                if std_mag != None:
                    # Also check that there is a valid
                    # instrumental magnitude value.
                    # It is a different 'if' to log a proper message.
                    if im[INST_MAG_COL] != INDEF_VALUE :
                
                        filters.add(im[FILTER_COL])
                        
                        all_magnitudes.append([day, \
                                               im[JD_TIME_COL], \
                                               im[INST_MAG_COL], \
                                               std_mag, \
                                               im[AIRMASS_COL],
                                               im[FILTER_COL]])
                    else:
                        logging.info("Standard magnitude undefined for object " + \
                                     obj[OBJ_NAME_COL])
                else:
                    logging.info("Standard magnitude not found for object " + \
                                 obj[OBJ_NAME_COL] + " in filter " + im[FILTER_COL])
    
    for d in days:
        for f in filters:
            mag = [m for m in all_magnitudes \
                   if m[DAY_CE_COL] == d and m[FILTER_CE_COL] == f] 
        
            ext_coef.append([d, f, calculate_extinction_coefficient(mag)])
        
    return ext_coef

def calculate_magnitude_out_of_atmosphere(objects, \
                                          no_standard_obj_index, \
                                          instrumental_magnitudes, \
                                          ext_coef):
    """
    
    Calculate the magnitude of the objects of interest out of the atmosphere using the
    extinction coefficient calculated previously.
    
    """
    
    pass

def process_instrumental_magnitudes(objects, instrumental_magnitudes):
    """
    
    This function process the instrumental magnitudes to get magnitudes
    out of the atmosphere.
    
    """
    
    standard_obj_index = []
    no_standard_obj_index = []
    
    # For each object. The two list received contains the same 
    # number of objects.
    for i in range(len(objects)):
        
        # Save instrumental magnitudes to a file.
        save_instrumental_magnitudes(objects[i][OBJ_NAME_COL], instrumental_magnitudes[i])        
        
        # Check if it is a standard object to put the object in
        # the right list.
        if objects[i][OBJ_STANDARD_COL] == STANDARD_VALUE:
            standard_obj_index.extend([i])
        else:
            no_standard_obj_index.extend([i])                       
            
    ext_coef = get_extinction_coefficient(objects, \
                                                standard_obj_index, \
                                                instrumental_magnitudes)   
    
    calculate_magnitude_out_of_atmosphere(objects, \
                                          no_standard_obj_index, \
                                          instrumental_magnitudes, \
                                          ext_coef) 
                                       
def compile_objects_magnitudes(progargs):
    """ 

    Get the magnitudes of the objects grouping all the magnitudes.

    """
    
    # Read the list of objects whose magnitudes are needed.
    objects = read_objects_of_interest(progargs)
    
    instrumental_magnitudes = compile_instrumental_magnitudes(objects)
    
    process_instrumental_magnitudes(objects, instrumental_magnitudes)
