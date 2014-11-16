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
This module calculates the photometry of the objects detected previously
by means of astrometry in a set of data images.
The photometry values calculated are stored in a text file that contains
all the measures for the objects of an image.
"""

import sys
import os
import glob
import astromatics
from pyraf import iraf
from pyraf.iraf import noao, digiphot, apphot
from constants import *
from textfiles import *
from fitfiles import *
from images import *

phot_progargs = None

def init_iraf():
    """
    
    This function initializes the pyraf environment.
    
    """
    
    # The display of graphics is not used, so skips Pyraf graphics 
    # initialization and run in terminal-only mode to avoid warning messages.
    os.environ['PYRAF_NO_DISPLAY'] = '1'

    # Set PyRAF process caching off to avoid errors if spawning multiple processes.
    iraf.prcacheOff()

    # Load iraf packages and does not show any output of the tasks.
    iraf.digiphot(_doprint = 0)
    iraf.apphot(_doprint = 0) 
    iraf.images(_doprint = 0)

    # Set the iraf.phot routine to scripting mode.
    iraf.phot.interactive = "no"
    iraf.phot.verify = "no"
    
def set_common_phot_pars():
    """
    
    This function sets the pyraf parameters used to perform
    the photometry of images that do not depends of each image.
    
    """        
    
    # Set photometry parameters.
    iraf.fitskypars.dannulus = DANNULUS_VALUE
    iraf.fitskypars.skyvalue = SKY_VALUE
    iraf.fitskypars.salgorithm = "mode"
    iraf.centerpars.cbox = 0
    iraf.centerpars.calgori = "centroid"
    
    # Name of the fields FITS that contains these values.
    iraf.datapars.exposure = "EXPOSURE"
    iraf.datapars.airmass = "AIRMASS"
    iraf.datapars.obstime = "MJD"
    iraf.datapars.readnoise = OSN_CCD_T150_READNOISE
    iraf.datapars.epadu = OSN_CCD_T150_GAIN
    iraf.datapars.datamax = OSN_CCD_T150_DATAMAX 

def set_image_specific_phot_pars(fwhm, datamin):
    """
    
    This function sets the pyraf parameters used to perform
    the photometry that depends on each image.
    
    """        
    
    # Set photometry parameters.
    iraf.photpars.apertures = APERTURE_MULT * fwhm
    iraf.fitskypars.annulus = ANNULUS_MULT * fwhm
    
    # Name of the fields FITS that contains these values.
    iraf.datapars.datamin = datamin

def save_parameters():
    """
    
    This function saves the parameters used to do the photometry.
    
    """    
    
    # Save parameters in files.
    iraf.centerpars.saveParList(filename='center.par')
    iraf.datapars.saveParList(filename='data.par')
    iraf.fitskypars.saveParList(filename='fitsky.par')
    iraf.photpars.saveParList(filename='phot.par') 


def calculate_datamin(image_file_name):
    """
    Calculate a datamin value for the image received using imstat.
    
    """
    
    # Set a default value for datamin.
    datamin = DATAMIN_VALUE
    
    try:
        imstat_output = iraf.imstat(image_file_name, fields='mean,stddev', Stdout=1)
        imstat_values = imstat_output[IMSTAT_FIRST_VALUE]
        values = imstat_values.split() # Set a calculated value for datamin.
        datamin = float(values[0]) - DATAMIN_MULT * float(values[1])
    except iraf.IrafError as exc:
        logging.error("Error executing imstat: Stats for data image: " + image_file_name)
        logging.error("Iraf error is: " + str(exc))
    except ValueError as ve:
        logging.error("Value Error calculating datamin for image: " + image_file_name)
        logging.error("mean is: " + values[0] + " stddev is: " + values[1])
        logging.error("Value Error is: " + str(ve))
        
    return datamin

def do_phot(image_file_name, catalog_file_name, output_mag_file_name, progargs):
    """
    
    This function calculates the photometry of the images. 
    Receives the image to use, a catalog with the position of the objects
    contained in the image and the name of the output file.
    
    """
    
    # If magnitude file exists, remove it to avoid error.
    if os.path.exists(output_mag_file_name):
        os.remove(output_mag_file_name)

    logging.debug("Calculating magnitudes for: " + image_file_name + \
                  " in " + output_mag_file_name)
    
    # Calculate datamin for this image.   
    datamin = calculate_datamin(image_file_name)                         
           
    # Calculate FWHM for this image.
    fwhm = astromatics.get_fwhm(progargs, image_file_name)
           
    # Set the parameters for the photometry that depends on the image.
    set_image_specific_phot_pars(fwhm, datamin)                
                
    try:           
        iraf.phot(image = image_file_name, 
                    coords = catalog_file_name, 
                    output = output_mag_file_name)
    except iraf.IrafError as exc:
        logging.error("Error executing phot on : " + image_file_name) 
        logging.error( "Iraf error is: " + str(exc))

def do_photometry(progargs):   
    """
    
    This function walk the directories searching for catalog files
    that contains the x,y coordinates of the objects detected by the
    astrometry. 
    For each catalog the corresponding data image is located and passes
    along with the catalog to a function that calculates the photometry
    of the objects in the catalog file.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == DATA_DIRECTORY:
                logging.debug("Found a directory for data: " + path)

                # Get the list of catalog files.
                catalog_files = glob.glob(os.path.join(path, "*." + \
                                                       CATALOG_FILE_EXT))
                
                logging.debug("Found " + str(len(catalog_files)) + \
                              " catalog files")
                
                # Each catalog indicates one or more images.
                for cat_file in catalog_files:
                    
                    # The images used are the aligned ones with a name that matches
                    # the name of the catalog, so the catalog references are valid
                    # for all these images.
                    object_name = cat_file[0:cat_file.find(DATANAME_CHAR_SEP)]
                     
                    image_file_pattern = object_name + "*" + DATA_FINAL_PATTERN
                    
                    images_of_catalog = glob.glob(image_file_pattern)
                        
                    logging.debug("Found " + str(len(images_of_catalog)) + \
                                  " images for this catalog.")
                        
                    # Calculate the magnitudes for each image related to the catalog.
                    for image in images_of_catalog:
                            
                        output_mag_file_name = \
                            image.replace(DATA_FINAL_PATTERN, 
                                                "." + MAGNITUDE_FILE_EXT)
                     
                        # If magnitude file exists, skip.
                        if not os.path.exists(output_mag_file_name):
                            do_phot(image, cat_file, output_mag_file_name, progargs)  
                        else:
                            logging.debug("Skipping phot for: " + \
                                          output_mag_file_name + \
                                          " already done.")
                    
def txdump_photometry_info():
    """
    
    This function search files containing the results of photometry
    and using txdump extracts the coordinates and photometric measure
    to save it to a text file.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == DATA_DIRECTORY:
                logging.debug("Found a directory for data: " + path)

                # Get the list of magnitude files.
                mag_files = glob.glob(os.path.join(path, "*." + MAGNITUDE_FILE_EXT))
                logging.debug("Found " + str(len(mag_files)) + " magnitude files")    
                
                # Reduce each data file one by one.
                for mfile in mag_files:                  
    
                    # Get the name of the file where the magnitude data will be saved.
                    mag_dest_file_name = \
                        mfile.replace("." + MAGNITUDE_FILE_EXT, \
                                      MAGNITUDE_FILE_EXT + "." + CSV_FILE_EXT)
                    
                    # Remove the destiny file if exists.
                    if os.path.exists(mag_dest_file_name):
                        os.remove(mag_dest_file_name)
                    
                    mag_dest_file = open(mag_dest_file_name, 'w' )
                    
                    try:
                        iraf.txdump(mfile, fields=TXDUMP_FIELDS, expr='yes', Stdout=mag_dest_file)
                    except iraf.IrafError as exc:
                        logging.error("Error executing txdump to get: " + \
                                      mag_dest_file_name)
                        logging.error("Iraf error is: " + str(exc))
                        
                    mag_dest_file.close()
                           
def calculate_photometry(progargs):
    """ Calculates the photometry of data images.

    This function calculates the photometry for all the data images found.

    """

    # Init iraf package.
    init_iraf()
    
    # Set photometry parameters that do not depend on each image.
    set_common_phot_pars()

    # Calculate the photometry.
    do_photometry(progargs)
    
    # Export photometry info to a text file with only the columns needed.
    txdump_photometry_info()
    
def get_object_final_name(object_name, int_objects):
    """
    
    This function receives the name of an object and returns
    the final name given to that object according to the final
    name indicated in the objects file.
    
    """
    
    object_final_name = object_name
    
    for o in int_objects:
        if o[OBJ_NAME_COL] == object_name:
            object_final_name = o[OBJ_FINAL_NAME_COL]
    
    return object_final_name
    

def save_manitudes_diff(all_magnitudes):
    """
    
    Write all the differences of magnitudes in a text file.
    
    """
    
    loggin.info("Saving differences of magnitudes to: " + \
                DEFAULT_DIFF_PHOT_FILE_NAME)
                
    with open(DEFAULT_DIFF_PHOT_FILE_NAME, 'w') as fw:
        
        writer = csv.writer(fw, delimiter=',')

        for row in all_magnitudes:
            # Write each magnitude in a row.
            writer.writerow(row)

def differential_photometry(progargs):
    """
    
    This function calculates the differential photometry between the
    object of interest and one or more objects in the same image.    

    """
    
    # Read the object of interest.
    int_objects = read_objects_of_interest(progargs.interest_object_file_name)
    
    # To store all the magnitudes.
    all_magnitudes = []    
    
    num_data_dirs_found = 0
    num_magnitude_files = 0
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                logging.debug("Found a directory for data: " + path)   
                
                num_data_dirs_found += 1         

                # Get the list of files ignoring hidden files.
                files_full_path = \
                    [fn for fn in \
                     glob.glob(os.path.join(path, \
                                            "*" + MAGNITUDE_FILE_EXT + \
                                            "." + CSV_FILE_EXT)) \
                     if not os.path.basename(fn).startswith('.')]
                    
                logging.debug("Found " + str(len(files_full_path)) + " magnitude files")
                
                # Process the magnitude files to get all the data.
                for fl in files_full_path:
                    
                    num_magnitude_files += 1
    
                    # Identify the object of this file, the filter and save.
                    object_name = get_filename_start(fl)
                    
                    filter = get_filter_from_file_name(fl)
                    
                    # To store the magnitudes of current file.
                    file_rows = []                      

                    # Read the magnitudes from the file.
                    with open(fl, 'rb') as fr:
                        reader = csv.reader(fr)      
                            
                        # Add to the magnitudes data, the position of this 
                        # magnitude in the file, the name of the filter and
                        # object name.
                        for row in reader:      
                            # Process the row, only one string element.
                            split_row = row[0].split(' ')
                            
                            new_row = []
                            
                            # Convert numeric strings to integer or float
                            # taking into account possible INDEF values.
                            for i in split_row:
                                value = 0
                                
                                if len(i) > 0:
                                    if i != INDEF_VALUE:
                                        if i.find(".") < 0:
                                            value = int(i)
                                        else:
                                            value = float(i)
                                
                                    new_row.extend([value])
                                    
                            # Only use the columns necessary to calculate
                            # the differential magnitudes.
                            final_row = [ new_row[i] for i in COLS_MAG]
                                                  
                            # Add the filter.
                            final_row.insert(0, filter)
                            
                            # Get the final name to used for this object.
                            final_object_name = \
                                get_object_final_name(object_name, int_objects)
                            
                            final_row.insert(0, final_object_name)
                            
                            file_rows.append(final_row)
                            
                    first_row = file_rows[0]
                            
                    # Calculate the differences between the first row and the rest.
                    for i in range(1,len(file_rows),1):
                        current_row = file_rows[i]
                        
                        # Calculate the values for the row with the differences.
                        diff_row = [first_row[OBJ_NAME_COL_DF], \
                                    first_row[FILTER_COL_DF], \
                                    current_row[INDEX_COL_DF] - 1, \
                                    first_row[JD_COL_DF], \
                                    first_row[MAG_COL_DF] - \
                                        current_row[MAG_COL_DF], \
                                    abs(first_row[ERR_COL_DF]) + \
                                        abs(current_row[ERR_COL_DF])]
                        
                        # Add the difference calculated to the list that 
                        # contains all the differences.                        
                        all_magnitudes.append(diff_row)
             
    logging.debug("Found " + str(num_data_dirs_found) + " data directories.")
    logging.debug("Found " + str(num_magnitude_files) + " magnitude files.") 
    logging.debug("Compiled " + str(len(all_magnitudes)) + " magnitudes.")
    
    save_manitudes_diff(all_magnitudes) 
                    