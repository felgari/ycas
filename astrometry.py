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

"""This module calculates the astrometry for a set of data images.

The astrometry is calculated with a external program from 'astrometry.net', in
turn, the stars in the images are identified using sextractor.
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
from fitfiles import *
from astrocoor import *

if sys.version_info < (3, 3):
    import subprocess32 as subprocess
else:
    import subprocess

# Positions for the values of the stars coordinates. 
RA_POS = 0
DEC_POS = 1
ID_POS = 2

# Radius of the field to solve.
SOLVE_FIELD_RADIUS = 1.0

# External commands
ASTROMETRY_COMMAND = "solve-field"

# Astrometry option to use sextractor.
ASTROMETRY_OPT_USE_SEXTRACTOR = " --use-sextractor "
ASTROMETRY_OPT_SEXTRACTOR_CONFIG = "--sextractor-config "

# Overwrite previous files and limit the number of objects to look at"
ASTROMETRY_PARAMS = "--overwrite "
    
class StarNotFound(Exception):
    """Raised if star is not found from file name. """
    
    def __init__(self, filename):
        self.filename = filename
        
class Astrometry(object):
    
    def __init__(self, progargs, stars):
        """Constructor.
    
        Args:
            progargs: Program arguments. 
            stars: Stars of interest.    
        """

        self._stars = stars
        
        self._data_dir_name = progargs.data_directory
        self._num_of_objects = progargs.number_of_objects_for_astrometry
        
        # Initializes attributes to store summary information of the astrometry.
        self._number_of_images = 0
        self._number_of_successful_images = 0    
        self._images_without_astrometry = []        
        
        # Initialize base command to call external software to do astrometry.
        use_sextractor = ""
        if progargs.use_sextractor_for_astrometry:
            use_sextractor = "%s %s" % \
                (ASTROMETRY_OPT_USE_SEXTRACTOR, progargs.sextractor_cfg_path)     
        
        self._base_command = "%s %s %s --radius %s -d " % \
            (ASTROMETRY_COMMAND, ASTROMETRY_PARAMS, 
            use_sextractor, SOLVE_FIELD_RADIUS)        

    def do_astrometry(self):
        """Get the astrometry for all the images found from the current 
        directory.
        
        This function searches directories that contains files of data images.
        When a directory with data images is found the astrometry is calculated
        for each data image calling an external program from 'astrometry.net'.
        The x,y positions calculated are stored to a file that contains only 
        those x and y position to be used later in photometry.
        
        """
        
        # Walk from current directory.
        for path, dirs, files in os.walk('.'):
    
            # Inspect only directories without subdirectories.
            if len(dirs) == 0:
                split_path = path.split(os.sep)
    
                # Check if current directory is for data.
                if split_path[-2] == self._data_dir_name:             
                    logging.info("Found a directory for data: %s" % (path))
    
                    # Get the list of files ignoring hidden files.
                    files_to_catalog = \
                        [fn for fn in \
                         glob.glob(os.path.join(path, 
                                                "*" + DATA_FINAL_PATTERN)) \
                        if not os.path.basename(fn).startswith('.')]
                        
                    logging.debug("Found %d files to catalog: %s " % \
                                  (len(files_to_catalog), 
                                   files_to_catalog))
    
                    self.do_astrometry_of_images(files_to_catalog)
    
        self.print_summary()
        
    def do_astrometry_of_image(self, image_file):
        """Get the astrometry of an image.
        
        Args:
            image_file: The image_file with the image.
            
        """
        
        star = self.get_star_of_filename(image_file)
            
        # Compose the command use the base command and adding the arguments
        # for current image.
        command = "%s %d --ra %.10g --dec %.10g %s" % \
            (self._base_command, self._num_of_objects, 
             star.ra, star.dec, image_file)
            
        logging.debug("Executing: %s" % (command))
        
        # Executes astrometry.net solver to get the astrometry
        # of the image.
        return_code = subprocess.call(command, shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        
        logging.debug("Astrometry execution return code: %d" % (return_code))
        
        return return_code, star
    
    def do_astrometry_of_images(self, files_to_catalog):
        """Perform the astrometry of the files received.
        
        Args:
            files_to_catalog: List of catalog files to generate.
        
        Returns:
        
        """
        # Get the astrometry for each image_file found.
        for image_file in files_to_catalog:
            
            self._number_of_images += 1
            
            try:
                cat_file_name = image_file.replace(DATA_FINAL_PATTERN, 
                    "." + CATALOG_FILE_EXT)
                
                # Check if the catalog image_file already exists.
                # If it already exists the astrometry is not calculated.
                if os.path.exists(cat_file_name) == False:
    
                    return_code, star = self.do_astrometry_of_image(image_file)
                    
                    if return_code == 0:
                        
                        # Generates catalog files with x,y and ra,dec values
                        # and if it is successful count it.
                        if write_coord_catalogues(image_file, cat_file_name, 
                                                  star):
                            
                            self._number_of_successful_images += 1
                            
                        else:
                            self._images_without_astrometry.extend([image_file])                     
                    
                else:
                    logging.debug("Catalog image_file already exists: %s" % 
                                  (cat_file_name))
                    
                    return_code = 0
                        
            except StarNotFound as onf:
                logging.debug("Object not found related to image_file: %s" % 
                              (onf.filename))        
        
    def print_summary(self):
        """Log a summary of the astrometry.
        
        """
        
        logging.info("Astrometry results:")
        
        logging.info("- Number of images processed: %d" % 
                     (self._number_of_images))
        
        logging.info("- Images processed successfully: %d" % \
                     (self._number_of_successful_images))
        
        logging.info("- Number of images without astrometry: %d" % \
                     (len(self._images_without_astrometry)))   
         
        logging.info("- List of images without astrometry: %s" % \
                     (self._images_without_astrometry))        

    def get_star_of_filename(self, filename):
        """Returns the star indicated by the file name received.
        
        The filename should corresponds to an star and the name of this stars
        should be part of the name. The name of the star is extracted from this
        file name and searched in the list of stars received.
        The star found and its position in the list are returned.
        
        Args:
            stars: List of stars of interest.
            filename: Filename related to an star to search in the set of stars.
        
        Returns:
            The star found.
        
        Raises:
            StarNotFound: If the star corresponding to the file name is nor found.
        
        """
        
        # Default values for the variables returned.
        star = None
        index = -1
        
        # Split file name from path.
        path, file = os.path.split(filename)
        
        # Get the star name from the filename, the name is at the beginning
        # and separated by a special character.
        star_name = file.split(DATANAME_CHAR_SEP)[0]
        
        logging.debug("In astrometry, searching coordinates for star: %s" %
                      (star_name))
        
        # Look for an star of the list whose name matches that of the filename.
        for s in self._stars:
            if s.name == star_name:
                star = s
                break
        
        # If the star is not found raise an exception,
        if star is None:
            raise StarNotFound(filename)
        
        return star 
        
def do_astrometry(progargs, stars):
    """Performs the astrometry.
    
    Args:
        progargs: Program arguments. 
        stars: Stars of interest.
        
    """
    
    logging.info("Doing astrometry ...")
    
    astrom = Astrometry(progargs, stars)

    astrom.do_astrometry()

    logging.info("Astrometry finished.")

