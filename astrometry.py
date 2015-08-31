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
from starcat import *

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
ASTROMETRY_PARAMS = "--overwrite"
    
class StarNotFound(Exception):
    """Raised if star is not found from file name. """
    
    def __init__(self, filename):
        self.filename = filename
        
class Astrometry(object):
    
    NUM_OBJECTS_SECOND_TRY = 40
    
    def __init__(self, progargs, stars, header_fields):
        """Constructor.
    
        Args:
            progargs: Program arguments. 
            stars: Stars of interest.    
            header_fields: Information about the headers.
            
        """

        self._stars = stars
        self._header_fields = header_fields
        
        self._target_dir = progargs.target_dir
        self._data_dir_name = progargs.light_directory
        self._num_of_objects = progargs.number_of_objects_for_astrometry
        
        # Initializes attributes to store summary information of the astrometry.
        self._number_of_images = 0
        self._number_of_successful_images = 0    
        self._images_without_astrometry = []        
        
        # Initialize base command to call external software to do astrometry.
        use_sextractor = ""
        if progargs.use_sextractor_for_astrometry:
            use_sextractor = "%s %s %s" % \
                (ASTROMETRY_OPT_USE_SEXTRACTOR, 
                 ASTROMETRY_OPT_SEXTRACTOR_CONFIG,
                 progargs.sextractor_cfg_path)     
        
        self._base_command = "%s %s %s --radius %s -d" % \
            (ASTROMETRY_COMMAND, ASTROMETRY_PARAMS, 
            use_sextractor, SOLVE_FIELD_RADIUS) 
            
    def astrometry_success(self, image_file_name):
        """Check if astrometry has finished with success looking for the
        files that should exists for the image whose astrometry has been
        requested.
         
        Args:
            image_file_name: Name of the file with image.
            
        """ 
        
        # Get the names for xyls and rdls files from the image file name.
        xyls_file_name = image_file_name.replace("." + FIT_FILE_EXT, \
                                                 INDEX_FILE_PATTERN)
    
        return os.path.exists(xyls_file_name)

    def do_astrometry(self):
        """Get the astrometry for all the images found from the current 
        directory.
        
        This function searches directories that contains files of data images.
        When a directory with data images is found the astrometry is calculated
        for each data image calling an external program from 'astrometry.net'.
        The x,y positions calculated are stored to a file that contains only 
        those x and y position to be used later in photometry.
        
        """
        
        # Walk from target directory.
        for path, dirs, files in os.walk(self._target_dir):
    
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
                        
                    logging.debug("Found %d files to catalog." % \
                                  (len(files_to_catalog)))
    
                    self.do_astrometry_of_images(files_to_catalog)
    
        self.print_summary()
        
    def execute_astrometry_command(self, num_of_objects, image_file, star):
        """Executes a external command to perform the astrometry.
        
        Args:
            num_of_objects: Number of objects to use when identifying the
                field of stars.
            image_file: The name of the file with the image.
            star: The star related to the image.
        """
        
        # Compose the command use the base command and adding the arguments
        # for current image.
        command = "%s %s --ra %.10g --dec %.10g %s" % \
            (self._base_command, num_of_objects, 
             star.ra, star.dec, image_file)
            
        logging.debug("Executing: %s" % (command))
        
        # Executes astrometry.net solver to get the astrometry
        # of the image.
        return_code = subprocess.call(command, shell=True, 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        
        logging.debug("Astrometry execution return code: %d" % (return_code))        
        
        return return_code
        
    def do_astrometry_of_image(self, image_file, star):
        """Get the astrometry of an image. The command is execute a second
        time if the first execution does not generate the astrometry.
        
        Args:
            image_file: The image_file with the image.
            star: The star related to the image.
            
        """
                    
        self.execute_astrometry_command(self._num_of_objects, image_file, star)
        
        success = self.astrometry_success(image_file)
        
        # Check if the astrometry has been successful.
        if success:
            logging.debug("Astrometry first execution successful with %s objects" %
                          (self._num_of_objects))
            
        elif self._num_of_objects < Astrometry.NUM_OBJECTS_SECOND_TRY:
            
            # If the first execution of astrometry has not been successful do a
            # second try incrementing the number of objects to identify.            
            self.execute_astrometry_command(Astrometry.NUM_OBJECTS_SECOND_TRY,
                                            image_file, star)
        
            success = self.astrometry_success(image_file)
            
            if success:
                logging.debug("Astrometry second execution successful with %d objects" %
                              (Astrometry.NUM_OBJECTS_SECOND_TRY))
            else:
                logging.debug("Astrometry second and final execution not " + 
                              "successful with %d objects" %
                              (Astrometry.NUM_OBJECTS_SECOND_TRY))       
                 
        return success
    
    def do_astrometry_of_images(self, files_to_catalog):
        """Perform the astrometry of the files received.
        
        Args:
            files_to_catalog: List of catalog files to generate.
        
        """
        
        # Get the astrometry for each image_file found.
        for image_file in files_to_catalog:
            
            self._number_of_images += 1
            
            cat_file_name = image_file.replace(DATA_FINAL_PATTERN, 
                "." + CATALOG_FILE_EXT)
            
            # Check if the catalog image_file already exists.
            # If it already exists the astrometry is not calculated.
            if os.path.exists(cat_file_name) == False:
                
                try:
                    
                    star = self.get_star_from_file(image_file)

                    # Generate astrometry of the image and check the result.                    
                    if self.do_astrometry_of_image(image_file, star):
                        
                        self._number_of_successful_images += 1
                        
                        # Generates catalog files with x,y and ra,dec values
                        # and if it is successful count it.
                        self.write_coord_catalogues(image_file, cat_file_name, 
                                                    star)
                         
                    else:
                        self._images_without_astrometry.extend([image_file])                     
                    
                except StarNotFound as onf:
                    logging.debug("Star not identified for image file: %s" % 
                                  onf.filename)                      
                    
            else:
                logging.debug("Catalog '%s' already exists." % 
                              (cat_file_name)) 
                
    def write_coord_catalogues(self, image_file_name, catalog_full_file_name, 
                               star):
        """Writes the x,y coordinates of a FITS file to a text file.    
        
        This function opens the FITS file that contains the table of x,y 
        coordinates and write these coordinates to a text file that only
        contains this x,y values. This text file will be used later to calculate
        the photometry of the stars on these coordinates.
        
        Args:
            image_file_name: Name of the file of the image.
            catalog_full_file_name: Name of the catalog to write
            star: The star.
                               
        Returns:    
            True if the file is written successfully.
        
        """
        
        success = False
        
        # Get the names for xyls and rdls files from the image file name.
        xyls_file_name = image_file_name.replace("." + FIT_FILE_EXT, \
                                                 INDEX_FILE_PATTERN)
        
        rdls_file_name = image_file_name.replace("." + FIT_FILE_EXT, \
                                                 "." + RDLS_FILE_EXT)
    
        logging.debug("xyls file name: %s" % (xyls_file_name))
        logging.debug("rdls file name: %s" % (rdls_file_name))      
        logging.debug("Catalog file name: %s" % (catalog_full_file_name))
        
        logging.debug("Star name: %s" % star.name)

        # Read x,y and ra,dec data from fit table.
        xy_data = get_fit_table_data(xyls_file_name)
        rd_data = get_fit_table_data(rdls_file_name)
               
        # Get the indexes for x,y and ra,dec data related to the
        # stars received.
        indexes, identifiers = get_indexes_for_star_coor(rd_data, star)  
            
        # Check if any star has been found in the image.
        if len(indexes) > 0:              
            # Check if the coordinates complies with the 
            # coordinates validation criteria.
            if check_celestial_coordinates(image_file_name, star, indexes, \
                                           identifiers, rd_data, xy_data):
                
                try:
                    star_catalog = StarCatalog(catalog_full_file_name)
            
                    star_catalog.write(indexes, identifiers, xy_data)     
                
                    success = True
                    
                except StarCatalogException as sce:
                    logging.error(sce)
            else:
                logging.warning("Catalog file not saved, coordinates " + \
                                "do not pass validation criteria.")
        else:
            logging.warning("Catalog file not saved, no stars found by astrometry")
            
        return success                       
        
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

    def get_star_from_file(self, filename):
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
        
        # Get the star name from the filename, the name is at the beginning
        # and separated by a special character.
        star_name = get_header_value(filename, self._header_fields.object)
        
        # If the name is not in the header try to get it from the file name.
        if star_name == fitsheader.DEFAULT_OBJECT_NAME or not star_name:
            
            # Get the star name from the filename..
            star_name = get_star_name_from_file_name(filename)          
        
        # Look for an star of the list whose name matches that of the filename.
        star = self._stars.get_star(star_name)
        
        # If the star is not found raise an exception,
        if star is None:
            raise StarNotFound(filename)
        
        return star 
        
def do_astrometry(progargs, stars, header_fields):
    """Performs the astrometry.
    
    Args:
        progargs: Program arguments. 
        stars: Stars of interest.
        header_fields: Information about the headers.
        
    """
    
    logging.info("Doing astrometry ...")
    
    astrom = Astrometry(progargs, stars, header_fields)

    astrom.do_astrometry()

    logging.info("Astrometry finished.")

