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

if sys.version_info < (3, 3):
    import subprocess32 as subprocess
else:
    import subprocess
    
XY_PERCENT_DEV_FROM_CENTER = 0.7

# Positions for the values of the stars coordinates. 
RA_POS = 0
DEC_POS = 1
ID_POS = 2
    
class StarNotFound(Exception):
    """Raised if star is not found from file name. """
    
    def __init__(self, filename):
        self.filename = filename

def get_star_of_filename(stars, filename):
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
    for s in stars:
        if s.name == star_name:
            star = s
            break
    
    # If the star is not found raise an exception,
    if star is None:
        raise StarNotFound(filename)
    
    return star

def get_fit_table_data(fit_table_file_name):
    """Get the data of a the first table contained in the fit file indicated.
    
    Args:
        fit_table_file_name: File name of the fit file that contains the table.
    
    Returns:
        The table contained in the fit file.
        
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
    
    # Read the table data and save it in a list.
    for row in table_data:
        ldata.append([row[0], row[1]])
        n += 1
    
    return ldata  

def get_rd_index(rd_data, ra, dec): 
    """ Get the index of the RA, DEC pair whose values are more
    close to those received.
    
    Args:
        rd_data: List of ra, dec values. The closest pair of this list to the
        ra,dec values are returned.
        ra: RA value to search.
        dec: DEC value to search.
    
    Returns:
        A pair RA,DEC of the list received with the nearest values to those
        RA, DEC parameters received.
        
    """
    
    # Default values for the data to return.
    index = -1    
    ra_diff = 1000.0
    dec_diff = 1000.0
    ra_min_diff = 1000.0
    dec_min_diff = 1000.0    
    
    # Iterate over the whole list to search for the nearest values to those
    # received.
    i = 0
    for rd in rd_data:
        # Compute the difference between the coordinates of the
        # star in this row and the star received.  
        temp_ra_diff = abs(float(rd[RD_DATA_RA_COL]) - ra)
        
        # If RA is close to 360 or 0, the differences could be close
        # to 360 but actually should be considered close to 0. 
        if temp_ra_diff > 355.0:
            temp_ra_diff = abs(360.0 - temp_ra_diff)
        
        # DEC (up to 90 difference is multiplied by 4 to equate 
        # the differences with RA (up to 360).
        temp_dec_diff = abs(float(rd[RD_DATA_DEC_COL]) - dec) * 4.0   
        
        # If the differences are into the margin.
        if temp_ra_diff < ASTROMETRY_COORD_RANGE and \
            temp_dec_diff < ASTROMETRY_COORD_RANGE:
            # If current row coordinates are smaller than previous this
            # row is chosen as candidate for the star.
            if temp_ra_diff + temp_dec_diff < ra_diff + dec_diff:
                ra_diff = temp_ra_diff
                dec_diff = temp_dec_diff
                index = i
                
        # Collect the minimum difference found to debug the process in case
        # of no matching.
        if temp_ra_diff + temp_dec_diff < ra_min_diff + dec_min_diff:
            ra_min_diff = temp_ra_diff
            dec_min_diff = temp_dec_diff
    
        i += 1
        
    if index == -1:
        logging.debug("No match for star coordinates, min. diff. are: " + \
                      str(ra_min_diff) + " " + str(dec_min_diff))
        
    return index

def get_indexes_for_star_cood(rd_data, star):
    """ Get the indexes of the ra,dec coordinates nearest to those of the 
    stars received.
    
    Args:
        rd_data: List of ra, dec values. The closest pair of this list to the
        ra,dec values are returned.
        star: The star.
    
    Returns:
        List of the indexes of coordinates of the list nearest to those of the
        stars received. 
    
    """
    
    # Indexes of the stars found.
    indexes = []
    # Identifiers of the stars found.
    identifiers = []
    
    # Get the index for the star.
    new_index = get_rd_index(rd_data, star.ra, star.dec)
    
    # If the star has been found.
    if new_index >= 0:
        logging.debug("Index for star '%s' is %d" % (star.name, new_index))
        
        # Get the indexes for the stars references.
        for star_of_field in star.field_stars:
            new_index = get_rd_index(rd_data, star_of_field.ra, \
                                     star_of_field.dec)
            
            # Check that an index has been found for this star.
            if new_index >= 0:
                logging.debug("Index for reference %.10g,%.10g with id %d is %d" %
                              (star_of_field.ra, star_of_field.dec,
                              star_of_field.id, new_index))        
                                         
                indexes.extend([new_index])  
                
                identifiers.extend([star_of_field.id])    
            else:
                logging.debug("Index for reference %.10g,%.10g with id %d not found" %
                              (star_of_field.ra, star_of_field.dec, 
                               star_of_field.id))
    else:
        logging.debug("Index for star %s not found" % star.name)

    return indexes, identifiers

def write_catalog_file(catalog_file_name, indexes, xy_data, identifiers):
    """Write text files with the x,y and ra,dec coordinates.
    
    The coordinates written are related to the x,y data and indexes set 
    received.
    
    Args:
        catalog_file_name: File name o
        indexes: List of indexes corresponding to the coordinates to write.
        xy_data: List of the X, Y coordinates that are referenced by X, Y
        coordinates.    
        identifiers: Identifiers of the stars found.    
    
    """
    
    logging.debug("Writing catalog file: " + catalog_file_name)
    
    # Open the destiny file.
    catalog_file = open(catalog_file_name, "w")
        
    # Iterate over the indexes to write them to the file.
    for i in range(len(indexes)):
        # The indexes corresponds to items in the XY data list.
        ind = indexes[i]
        
        catalog_file.write(str(xy_data[ind][XY_DATA_X_COL]) + " " + \
                           str(xy_data[ind][XY_DATA_Y_COL]) + " " + \
                           identifiers[i] + "\n")
    
    catalog_file.close()
    
def check_celestial_coordinates(image_file_name, star, indexes, \
                                identifiers, rd_data, xy_data):
    """Check if ra,dec coordinates complies the validation criteria.
    
    These validations are performed to ensure the astrometry coordinates are
    consistent with the expected values.
    - Checks that the RA,DEC coordinates for the star of interest are 
    contained in the field recognized by the astrometry.
    - Checks that the X,Y coordinates for the star of interest are into a 
    distance from the center of the image.
    
    Args:
        image_file_name: Name of the file to the image whose coordinates are 
        checked.
        star: Data of the star whose image is analyzed to get the astrometry.
        indexes: Indexes to the coordinates of the stars found in this image.
        rd_data: List of RA, DEC coordinates calculated by the astrometry.
        xy_data: list of X, Y coordinates calculated by the astrometry.
    
    Returns:    
        True if checks are ok, False otherwise.
    
    """
    
    success = True
    
    # Default values.
    min_ra = 1000.0
    max_ra = -1000.0
    min_dec = 1000.0
    max_dec = -1000.0
    
    # Iterate over the RA, DEC list of coordinates to get the minimum and 
    # maximum values of RA and DEC.
    for rd in rd_data:
        ra = float(rd[RD_DATA_RA_COL])
        dec = float(rd[RD_DATA_DEC_COL])
        
        if ra < min_ra:
            min_ra = ra
            
        if ra > max_ra:
            max_ra = ra   
            
        if dec < min_dec:
            min_dec = dec
            
        if dec > max_dec:
            max_dec = dec       
            
    # Check that the RA,DEC coordinates for the star of interest
    # are contained in the field recognized by the astrometry.
    if (star.ra > min_ra) and (star.ra < max_ra) and \
         (star.dec > min_dec) and (star.dec < max_dec):
        
        header_fields = get_fit_fields(image_file_name, \
                                       XY_CENTER_FIT_HEADER_FIELDS)
        
        try:
            x_center = int(header_fields[CRPIX1])
            y_center = int(header_fields[CRPIX2])
            
            # Retrieve the index in the astrometry list saved as first index.
            # This index corresponds to the star of interest.
            first_star = xy_data[indexes[0]] 
            
            star_x = int(first_star[XY_DATA_X_COL])
            star_y = int(first_star[XY_DATA_Y_COL])
            
            # Check that the X,Y coordinates for the star of interest are
            # into a distance from the center of the image.
            if (star_x < x_center - x_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (star_x > x_center + x_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (star_y < y_center - y_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (star_y > y_center + y_center * XY_PERCENT_DEV_FROM_CENTER):
            
                success = False             
                
                logging.error("X,Y coordinates for star to far from " + \
                              "center in " + image_file_name)
        except KeyError as ke:
            logging.warning("Header field 'for XY center not found in file " + \
                            image_file_name)  
        
    else:
        logging.error("RA DEC coordinates given by astrometry does not " + \
                      "contain star in image: " + \
                      image_file_name)
        
        success = False
        
    if len(set(identifiers)) < len(identifiers):
        logging.error("Duplicated coordinates for some star in: " + \
                      image_file_name)
        
    if len([x for x in identifiers if x == '0']) == 0:
        logging.error("No coordinates identified for star of interest in: " + \
                      image_file_name)        
    
    return success    

def write_coord_catalogues(image_file_name, catalog_full_file_name, star):
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

    # Check if the file containing x,y coordinates exists.
    if os.path.exists(xyls_file_name):

        logging.debug("X,Y coordinates file exists")
        logging.debug("xyls file name: %s" % (xyls_file_name))
        logging.debug("rdls file name: %s" % (rdls_file_name))      
        logging.debug("Catalog file name: $s" % (catalog_full_file_name))
        
        logging.debug("Star name: %s" % star.name)

        # Read x,y and ra,dec data from fit table.
        xy_data = get_fit_table_data(xyls_file_name)
        rd_data = get_fit_table_data(rdls_file_name)
        
        # Get the indexes for x,y and ra,dec data related to the
        # stars received.
        indexes, identifiers = get_indexes_for_star_cood(rd_data, star)  
            
        # Check if any star has been found in the image.
        if len(indexes) > 0:              
            # Check if the coordinates complies with the 
            # coordinates validation criteria.
            if check_celestial_coordinates(image_file_name, star, indexes, \
                                           identifiers, rd_data, xy_data):
    
                # Write catalog file with the x,y coordinate to do the
                # photometry.
                write_catalog_file(catalog_full_file_name, indexes, xy_data, \
                                   identifiers)        
                
                success = True
            else:
                logging.debug("Catalog file not saved, " + \
                              "coordinates do not pass validation criteria.")
        else:
            logging.debug("Catalog file not saved, no stars found by astrometry")
    else:
        logging.debug("X,Y coordinates file '%s' does not exists, so catalog file could not be created." %
                      (xyls_file_name))
        
    return success  
        
def do_astrometry(progargs, stars):
    """ Get the astrometry for all the images found from the current directory.
        
    This function searches directories that contains files of data images.
    When a directory with data images is found the astrometry is calculated
    for each data image calling an external program from 'astrometry.net'.
    The x,y positions calculated are stored to a file that contains only 
    those x and y position to be used later in photometry.
    
    Args:
        progargs: Program arguments. 
        stars: Stars of interest.
        
    """
    
    logging.info("Doing astrometry ...")

    # Initializes images that store summary information of the whole process.
    number_of_images = 0
    number_of_successful_images = 0    
    images_without_astrometry = []

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == progargs.data_directory:             
                logging.info("Found a directory for data: %s" % (path))

                # Get the list of files ignoring hidden files.
                files_to_catalog = \
                    [fn for fn in glob.glob(os.path.join(path, "*" + \
                                                         DATA_FINAL_PATTERN)) \
                    if not os.path.basename(fn).startswith('.')]
                    
                logging.debug("Found %d files to catalog: %s " % \
                              (len(files_to_catalog), 
                               str(files_to_catalog)))

                # Get the astrometry for each file found.
                for file in files_to_catalog:
                    
                    number_of_images += 1
                    
                    try:                        
                        # Get the catalog name where the coordinates are
                        # written.
                        catalog_file_name = file.replace(DATA_FINAL_PATTERN, \
                                                       "." + CATALOG_FILE_EXT)

                        # Check if the catalog file already exists.
                        # If it already exists the astrometry is not calculated.
                        if os.path.exists(catalog_file_name) == False :
                            
                            star = get_star_of_filename(stars, file)
    
                            use_sextractor = ""
                            
                            if progargs.use_sextractor_for_astrometry:
                                use_sextractor = "%s %s" % \
                                    (ASTROMETRY_OPT_USE_SEXTRACTOR,
                                    progargs.sextractor_cfg_path)                              
    
                            command = "%s %s %d %s %s --ra %.10g --dec %.10g --radius %.10g %s" % \
                                (ASTROMETRY_COMMAND, ASTROMETRY_PARAMS,
                                progargs.number_of_objects_for_astrometry,
                                use_sextractor, ra_dec_param, 
                                star.ra, star.dec,
                                SOLVE_FIELD_RADIUS, file)
                                
                            logging.debug("Executing: %s" % (command))
    
                            # Executes astrometry.net solver to get the 
                            # astrometry of the image.
                            return_code = subprocess.call(command,
                                shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    
                            logging.debug("Astrometry execution return code: %d" %
                                          (return_code))                            
                        else:
                            logging.debug("Catalog file already exists: %s" %
                                          (catalog_file_name))
                            
                            return_code = 0
                            
                        if return_code == 0:
                            # Generates catalog files with x,y and ra,dec values 
                            # and if it successfully count it. 
                            if write_coord_catalogues(file, catalog_file_name, \
                                                      star):
                                number_of_successful_images = \
                                    number_of_successful_images + 1
                            else:
                                images_without_astrometry.extend([file])
                            
                    except StarNotFound as onf:
                        logging.debug("Object not found related to file: %s" % \
                                      (onf.filename))

    logging.info("Astrometry results:")
    logging.info("- Number of images processed: %d" % (number_of_images))
    logging.info("- Images processed successfully: %d" % \
                 (number_of_successful_images))
    logging.info("- Number of images without astrometry: %d" % \
                 (len(images_without_astrometry)))    
    logging.info("- List of images without astrometry: %s" % \
                 (str(images_without_astrometry)))