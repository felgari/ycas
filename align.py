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

"""This module aligns images related to a same object.

The images are searched from a root directory and all the images that
accomplish a criteria for name and directory, located in the same 
directory, and related the same object are aligned.
The set images of the same object are aligned one by one with respect to one 
of the images of the set.

The alignment is performed by the imalign function of pyraf, prior to the
alignment, a set of imalign related parameters are initialized.
"""

import sys
import os
import logging
import glob
from pyraf import iraf
from pyraf.iraf import proto
from constants import *

def set_align_pars():
    """Set the parameters used to perform the alignment with pyraf imalin. """
    
    iraf.imalign.boxsize = 11
    iraf.imalign.bigbox = 25
    iraf.imalign.niterate = 3
    iraf.imalign.shiftimage = "yes"
    iraf.imalign.interp_type = "linear"
    iraf.imalign.boundary_typ = "nearest"
    iraf.imalign.verbose = "no"
  
def align_images():
    """Search directories for data images and align them using pyraf imalin.
    
    The images aligned correspond to the same object.
    One of the images belonging to the set along with the set of x,y 
    coordinates of the images are used to perform the alignment.
    The images aligned are stored in new files to keep the original ones.
    
    """
    
    logging.info("Aligning images ...")
    
    # Set the parameters needed to perform imalign.
    set_align_pars()

    # Variable to count the total number of images and the image aligned
    number_of_images = 0
    number_of_images_aligned = 0

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data images.
            # Only files in these directories are processed.
            if split_path[-2] == DATA_DIRECTORY:
                
                # Get the full path of the directory.                
                full_dir = path
                
                logging.debug("Found a directory for data images: " + full_dir)

                # Get the list of catalog files ignoring hidden files.
                files_full_path = \
                    [f for f in glob.glob(os.path.join(full_dir, "*." + \
                                                       CATALOG_FILE_EXT)) \
                    if not os.path.basename(f).startswith('.')]
                    
                logging.debug("Found " + str(len(files_full_path)) + 
                              " catalog files")
                
                # Get the list of unique catalog names.
                # Each object could have several images, each one with a
                # catalog file, only a catalog file is needed by object,
                # so get a generic catalog name for each object.
                catalog_names = \
                    [ os.path.basename(f[0:f.find(DATANAME_CHAR_SEP)]) \
                     for f in files_full_path ]

                logging.debug("Catalogs: " + str(catalog_names))

                # Align the images corresponding to each catalog.
                for cn in catalog_names:
                    data_images = \
                        [f for f in glob.glob(os.path.join(full_dir, \
                        cn + "*" + DATA_FINAL_PATTERN)) \
                        if not os.path.basename(f).startswith('.')]

                    if len(data_images) > 1:
                        
                        # Count all these images.
                        number_of_images += len(data_images)

                        # Sort the images by name.
                        data_images.sort()

                        # The reference image is the first one.
                        reference_image = data_images[0]
                        
                        # Remove the first image from the list to align.
                        data_images = data_images[1:]

                        # Get the names of the aligned images.
                        align_images = \
                            [s.replace(DATA_FINAL_PATTERN, DATA_ALIGN_PATTERN) \
                             for s in data_images ]

                        catalog = reference_image.replace(DATA_FINAL_PATTERN, \
                                                          "." + \
                                                          CATALOG_FILE_EXT)
                        
                        # Perform imalign on images one by one.
                        for i in range(len(data_images)):
                            
                            image = data_images[i]
                            aligned_image = align_images[i]

                            try:
                                iraf.imalign(image, reference_image, catalog, \
                                             aligned_image, Stdout=1)
                                
                                # Count this image as successfully aligned.
                                number_of_images_aligned += 1
                                
                            except iraf.IrafError as exc:
                                logging.error("Error executing imalign " + \
                                              "on image: " + image)
                                logging.error("Iraf error is: " + str(exc))   
                    else:
                        logging.debug("Only 1 data image, alignment is not " + \
                                      "necessary.")

    logging.info("Align - Total number of images: " + str(number_of_images))
    logging.info("Align - Number of images successfully aligned: " + \
                 str(number_of_images_aligned))