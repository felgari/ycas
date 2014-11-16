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
This module calculates the astrometry for a set of data images that
exists from a given directory.
The astrometry is calculated with a external program from 'astrometry.net'.
"""

import sys
import os
import logging
import yargparser
import glob
import pyfits
import csv
from constants import *
from textfiles import *

if sys.version_info < (3, 3):
    import subprocess32 as subprocess
else:
    import subprocess
    
class ObjectNotFound(StandardError):
    """ Raised if object is not found from file name. """
    
    def __init__(self, filename):
        self.filename = filename

def get_object(objects, filename):
    """
    
    Returns the object indicated by the file name received.
    
    """
    
    object = None
    index = -1
    
    # Split file name from path.
    path, file = os.path.split(filename)
    
    # Get the object name from the filename, the name is at the beginning
    # and separated by a special character.
    obj_name = file.split(DATANAME_CHAR_SEP)[0]
    
    logging.debug("In astrometry, searching coordinates for object: " + obj_name)
    
    for i in range(len(objects)):
        obj = objects[i]
        if obj[OBJ_NAME_COL] == obj_name:
            object = obj
            index = i
    
    if object is None:
        raise ObjectNotFound(filename)
    
    return object, index

def get_fit_table_data(fit_table_file_name):
    """
    
    This function returns the data of a the first table contained
    in the fit whose name has been received as parameter.
    
    """
    
    # Open the FITS file received.
    fit_table_file = pyfits.open(fit_table_file_name) 

    # Assume the first extension is a table.
    table_data = fit_table_file[FIT_FIRST_TABLE_INDEX].data    
    
    fit_table_file.close()
    
    # Convert data from fits table to a list.
    ldata = list()
    
    # To add an index to the rows.
    n = 1
    
    for row in table_data:
        ldata.append([row[0], row[1]])
        n += 1
    
    return ldata  

def get_rd_index(rd_data, ra, dec): 
    """
    
    Return the index of the ra,dec data whose values are more
    close to those received.
    
    """
    
    index = -1
    
    ra_diff = 1000.0
    dec_diff = 1000.0 
    
    i = 0
    for rd in rd_data:
        # Compute the difference between the coordinates of the
        # object in this row and the object received.  
        temp_ra_diff = abs(float(rd[0]) - ra)
        temp_dec_diff = abs(float(rd[1]) - dec)   
        
        # If current row coordinates are smaller than previous this
        # row is chosen as candidate for the object.
        if temp_ra_diff < ra_diff and temp_dec_diff < dec_diff:
            ra_diff = temp_ra_diff
            dec_diff = temp_dec_diff
            index = i        
    
        i += 1
        
    return index

def get_indexes_for_obj_cood(rd_data, object, object_references):
    """
    
    Get the indexes of the ra,dec coordinates received more close to
    those of the objects received.
    
    """
    
    indexes = []
    
    # Get the index for the object.
    new_index = get_rd_index(rd_data, float(object[OBJ_RA_COL]), \
                             float(object[OBJ_DEC_COL]))
    
    if new_index >= 0:
        logging.debug("Index for object '" + object[OBJ_NAME_COL] + \
                      "' is " +  str(new_index))
        
        indexes.extend([new_index])
        
        # Get the indexes for the objects references (the first is the
        # object of interest).
        for obj_ref in object_references:
            new_index = get_rd_index(rd_data, float(obj_ref[0]), \
                                     float(obj_ref[1]))
            
            if new_index >= 0:
                logging.debug("Index for references " + str(obj_ref[0]) + \
                              "," + str(obj_ref[1]) + " is " + str(new_index))        
                                         
                indexes.extend([new_index])      
            else:
                logging.debug("Index for references " + str(obj_ref[0]) + \
                              "," + str(obj_ref[1]) + " not found")
    else:
        logging.debug("Index for object " + object[OBJ_NAME_COL] + \
                      " not found")

    return indexes


def write_catalog_file(catalog_file_name, indexes, xy_data):
    """
    
    Write text files with the x,y and ra,dec coordinates of the data
    received corresponding to the indexes set.
    
    """
    
    logging.debug("Writing catalog file: " + catalog_file_name)
    
    # Write x,y coordinates to a text file.
    catalog_file = open(catalog_file_name, "w")
        
    for i in indexes:
        catalog_file.write(str(xy_data[i][0]) + " " + str(xy_data[i][1]) + "\n")
    
    catalog_file.close()

def write_coord_catalogues(image_file_name, catalog_file_name, \
                           object, object_references):
    """
    This function opens the FITS file that contains the table of x,y 
    coordinates and write these coordinates to a text file that only
    contains this x,y values. This text file will be used later for
    photometry.
    Also generates a text file with the ra, dec coordinates related to
    the x,y coordinates.
    
    """
    
    # Get the names for xyls and rdla files from image file name.
    xyls_file_name = image_file_name.replace("." + FIT_FILE_EXT, INDEX_FILE_PATTERN)
    rdls_file_name = image_file_name.replace("." + FIT_FILE_EXT, "." + RDLS_FILE_EXT)

    # Check if the file containing x,y coordinates exists.
    if os.path.exists(xyls_file_name):

        logging.debug("X,Y coordinates file exists")
        logging.debug("xyls file name: " + xyls_file_name)
        logging.debug("rdls file name: " + rdls_file_name)        
        logging.debug("Catalog file name: " + catalog_file_name)
        
        # Get only the file name.
        catalog_only_file_name = os.path.split(catalog_file_name)[-1]
        object_name = catalog_only_file_name[:catalog_only_file_name.find(DATANAME_CHAR_SEP)]
        
        logging.debug("Object name: " + object_name)

        # Read x,y and ra,dec data from fit table.
        xy_data = get_fit_table_data(xyls_file_name)
        rd_data = get_fit_table_data(rdls_file_name)
        
        # Get the indexes for x,y and ra,dec data related to the
        # objects received.
        indexes = get_indexes_for_obj_cood(rd_data, object, object_references)

        # Write catalog file with the x,y coordinate to do the
        # photometry.
        write_catalog_file(catalog_file_name, indexes, xy_data)

    else:
        logging.debug("X,Y coordinates file '" + xyls_file_name + \
                      "' does not exists so catalog file could not be created.")
        
def read_objects_references(objects):
    """
    
    Read the ra, dec coordinates of the object references for
    the objects received.
    
    """        
    
    objects_references = []
    
    for obj in objects:
        objects_references.append(read_references_for_object(obj[OBJ_NAME_COL]))
    
    return objects_references    
        
def do_astrometry(progargs):
    """
        
    This function searches directories that contains files of data images.
    When a directory with data images is found the astrometry is calculated
    for each data image calling an external program from 'astrometry.net'.
    The x,y positions calculated are stored to a file that contains only 
    those x and y position to be used later in photometry.
    
    """
    
    logging.info("Doing astrometry ...")

    number_of_images = 0
    number_of_successfull_images = 0
    
    # Read the list of objects of interest.
    objects = read_objects_of_interest(progargs.interest_object_file_name)
    
    objects_references = read_objects_references(objects)

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                logging.debug("Found a directory for data: " + full_dir)

                # Get the list of files ignoring hidden files.
                files_to_catalog = \
                    [fn for fn in glob.glob(os.path.join(full_dir, "*" + DATA_FINAL_PATTERN)) \
                    if not os.path.basename(fn).startswith('.')]
                    
                logging.debug("Found " + str(len(files_to_catalog)) + \
                              " files to catalog: " + str(files_to_catalog))

                # Get the astrometry for each file.
                for fl in files_to_catalog:
                    
                    # Try to get RA and DEC for the object to solve the field only around
                    # these coordinates.
                    ra_dec_param = ""
                    
                    try:
                        obj, obj_idx = get_object(objects, fl)
                        
                        ra = str(obj[OBJ_RA_COL])
                        dec = str(obj[OBJ_DEC_COL])
                        
                        ra_dec_param =" --ra " + ra + " --dec " + dec + " --radius " + str(SOLVE_FIELD_RADIUS)
                        
                        catalog_file_name = fl.replace(DATA_FINAL_PATTERN, "." + CATALOG_FILE_EXT)

                        # Check if the catalog file already exists.
                        if os.path.exists(catalog_file_name) == False :
    
                            command = ASTROMETRY_COMMAND + " " + ASTROMETRY_PARAMS + \
                            str(progargs.number_of_objects_for_astrometry) + " " + \
                            ra_dec_param + " " + fl
                            logging.debug("Executing: " + command)
    
                            # Executes astrometry.net to get the astrometry of the image.
                            return_code = subprocess.call(command, \
                                shell=True, stdout=subprocess.PIPE, \
                                stderr=subprocess.PIPE)
    
                            logging.debug("Astrometry execution return code: " + str(return_code))
    
                            number_of_images += 1
    
                            if return_code == 0:
                                number_of_successfull_images = number_of_successfull_images + 1
    
                                # Generates catalog files with x,y and ra,dec values.
                                write_coord_catalogues(fl, catalog_file_name, \
                                                       obj, objects_references[obj_idx])
                        else:
                            logging.debug("Catalog file already exists: " + catalog_file_name)
                    except ObjectNotFound as onf:
                        logging.debug("Object not found related to file: " + onf.filename)

    logging.info("Astrometry results:")
    logging.info("- Number of images processed: " + str(number_of_images))
    logging.info("- Images processed successfully: " + str(number_of_successfull_images))
