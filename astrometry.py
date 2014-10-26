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
import subprocess32 as subprocess
from constants import *

def write_xy_catalog(table_file_name, catalogue_file_name):
    """
    This function opens the FITS file that contains the table of x,y 
    coordinates and write these coordinates to a text file that only
    contains this x,y values. this text file will be used later for
    photometry.
    
    """

    # Check if the file containing x,y coordinates exists.
    if os.path.exists(table_file_name):

        logging.info("X,Y coordinates file exists")
        logging.info("Table file name: " + table_file_name)
        logging.info("Catalog file name: " + catalogue_file_name)

        # Open the FITS file received.
        fits_file = pyfits.open(table_file_name) 

        # Assume the first extension is a table.
        tbdata = fits_file[ASTROMETRY_WCS_TABLE_INDEX].data  

        # Write x,y coordinates to a text file.
        text_file = open(catalogue_file_name, "w")

        for i in range(len(tbdata)):
            text_file.write(str(tbdata[i][0]) + " " + str(tbdata[i][1]) + "\n")

        text_file.close()
        
        fits_file.close()

    else:
        logging.info("X,Y coordinates file does not exists so no catalog file is created.")
        
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

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                logging.info("Found a directory for data: " + full_dir)

                # Get the list of files ignoring hidden files.
                files_full_path = \
                    [fn for fn in glob.glob(os.path.join(full_dir, "*" + DATA_FINAL_PATTERN)) \
                    if not os.path.basename(fn).startswith('.')]
                    
                logging.info("Found " + str(len(files)) + " data files")

                # Get the list of unique data names.
                data_names = [ os.path.basename(f[0:f.find(DATANAME_CHAR_SEP)]) \
                                for f in files_full_path ]

                # Remove duplicates.
                unique_data_names = list(set(data_names))

                # The name of the directory that contains the image matches
                # the name of the filter.
                filter_name = split_path[-1]

                # Complete the name of all files.
                files_to_catalog = \
                    [ os.path.join(full_dir, udn + DATANAME_CHAR_SEP + FIRST_DATA_IMG + \
                        filter_name + DATA_FINAL_PATTERN) \
                        for udn in unique_data_names ]

                logging.info("Files to catalog: " + str(files_to_catalog))

                # Get the astrometry for each file.
                for fl in files_to_catalog:

                    catalog_name = fl.replace(DATA_FINAL_PATTERN, "." + CATALOG_FILE_EXT)

                    # Check if the catalog file already exists.
                    if os.path.exists(catalog_name) == False :

                        command = ASTROMETRY_COMMAND + " " + ASTROMETRY_PARAMS + \
                        str(progargs.number_of_objects_for_astrometry) + " " + fl
                        logging.info("Executing: " + command)

                        # Executes astrometry.net to get the astrometry of the image.
                        return_code = subprocess.call(command, \
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        logging.info("Astrometry execution return code: " + str(return_code))

                        number_of_images += 1

                        if return_code == 0:
                            number_of_successfull_images = number_of_successfull_images + 1

                            # From wcs file generates a text file with x,y values.
                            write_xy_catalog( \
                                fl.replace("." + FIT_FILE_EXT, INDEX_FILE_PATTERN), \
                                catalog_name)
                    else:
                        logging.info("Catalog file already exists: " + catalog_name)

    logging.info("Astrometry results:")
    logging.info("- Number of images processed: " + str(number_of_images))
    logging.info("- Images processed successfully: " + str(number_of_successfull_images))
