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
turn, the objects in the images are identified using sextractor.
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

# Positions for the values of the objects coordinates. 
RA_POS = 0
DEC_POS = 1
ID_POS = 2
    
class ObjectNotFound(StandardError):
    """Raised if object is not found from file name. """
    
    def __init__(self, filename):
        self.filename = filename

def get_object(objects, filename):
    """Returns the object indicated by the file name received.
    
    The filename should corresponds to an object and the name of this objects
    should be part of the name. The name of the object is extracted from this
    file name and searched in the list of objects received.
    The object found and its position in the list are returned.
    
    Keyword arguments:
    objects -- List of objects of interest.
    filename -- Filename related to an object to search in the set of objects.
    
    Returns:
    object -- The object found.
    index -- The index of the object in the list.
    
    Raises:
    ObjectNotFound -- If the object corresponding to the file name is nor found.
    
    """
    
    # Default values for the variables returned.
    object = None
    index = -1
    
    # Split file name from path.
    path, file = os.path.split(filename)
    
    # Get the object name from the filename, the name is at the beginning
    # and separated by a special character.
    obj_name = file.split(DATANAME_CHAR_SEP)[0]
    
    logging.debug("In astrometry, searching coordinates for object: " + \
                  obj_name)
    
    # Look for an object of the list whose name matches that of the filename.
    for i in range(len(objects)):
        obj = objects[i]
        # If an object with the same name is found, assign the values to the
        # returned variables. 
        if obj[OBJ_NAME_COL] == obj_name:
            object = obj
            index = i
    
    # If the object is not found raise an exception,
    if object is None:
        raise ObjectNotFound(filename)
    
    return object, index

def get_fit_table_data(fit_table_file_name):
    """Get the data of a the first table contained in the fit file indicated.
    
    Keyword arguments:
    fit_table_file_name -- File name of the fit file that contains the table.
    
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
    
    Keyword arguments:
    rd_data -- List of ra, dec values. The closest pair of this list to the
    ra,dec values are returned.
    ra -- RA value to search.
    dec -- DEC value to search.
    
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
        # object in this row and the object received.  
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
            # row is chosen as candidate for the object.
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
        logging.debug("No match for object coordinates, min. diff. are: " + \
                      str(ra_min_diff) + " " + str(dec_min_diff))
        
    return index

def get_indexes_for_obj_cood(rd_data, object, object_references):
    """ Get the indexes of the ra,dec coordinates nearest to those of the 
    objects received.
    
    Keyword arguments:
    rd_data --  List of ra, dec values. The closest pair of this list to the
    ra,dec values are returned.
    object -- Object of interest whose coordinates are searched.
    object_references -- List of other object whose coordinates are also 
    searched.
    
    Returns:
    List of the indexes of coordinates of the list nearest to those of the
    objects received. 
    
    """
    
    # Indexes of the objects found.
    indexes = []
    # Identifiers of the objects found.
    identifiers = []
    
    # Get the index for the object.
    new_index = get_rd_index(rd_data, float(object[OBJ_RA_COL]), \
                             float(object[OBJ_DEC_COL]))
    
    # If the object has been found.
    if new_index >= 0:
        logging.debug("Index for object '" + object[OBJ_NAME_COL] + \
                      "' is " +  str(new_index))
        
        # Get the indexes for the objects references.
        for obj_ref in object_references:
            new_index = get_rd_index(rd_data, 
                                     float(obj_ref[RA_POS]), \
                                     float(obj_ref[DEC_POS]))
            
            # Check that an index has been found for this object.
            if new_index >= 0:
                logging.debug("Index for references " + str(obj_ref[RA_POS]) + \
                              "," + str(obj_ref[DEC_POS]) + " with id " +
                              obj_ref[ID_POS]+ " is " + str(new_index))        
                                         
                indexes.extend([new_index])  
                
                identifiers.extend([obj_ref[ID_POS]])    
            else:
                logging.debug("Index for references " + str(obj_ref[RA_POS]) + \
                              "," + str(obj_ref[DEC_POS]) + " with id " + \
                              obj_ref[ID_POS]+ " not found")
    else:
        logging.debug("Index for object " + object[OBJ_NAME_COL] + \
                      " not found")

    return indexes, identifiers

def write_catalog_file(catalog_file_name, indexes, xy_data, identifiers):
    """Write text files with the x,y and ra,dec coordinates.
    
    The coordinates written are related to the x,y data and indexes set 
    received.
    
    Keyword arguments:
    catalog_file_name -- File name o
    indexes -- List of indexes corresponding to the coordinates to write.
    xy_data -- List of the X, Y coordinates that are referenced by X, Y
    coordinates.    
    identifiers -- Identifiers of the objects found.    
    
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
    
def check_celestial_coordinates(image_file_name, object, indexes, \
                                identifiers, rd_data, xy_data):
    """Check if ra,dec coordinates complies the validation criteria.
    
    These validations are performed to ensure the astrometry coordinates are
    consistent with the expected values.
    - Checks that the RA,DEC coordinates for the object of interest are 
    contained in the field recognized by the astrometry.
    - Checks that the X,Y coordinates for the object of interest are into a 
    distance from the center of the image.
    
    Keyword arguments:
    image_file_name -- Name of the file to the image whose coordinates are 
    checked.
    object -- Data of the object whose image has been analyzed to get the 
    astrometry.
    indexes -- Indexes to the coordinates of the objects found in this image.
    rd_data -- List of RA, DEC coordinates calculated by the astrometry.
    xy_data -- list of X, Y coordinates calculated by the astrometry.
    
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
            
    # Get RA and DEC values of the object.
    obj_ra = float(object[OBJ_RA_COL])
    obj_dec = float(object[OBJ_DEC_COL])
            
    # Check that the RA,DEC coordinates for the object of interest
    # are contained in the field recognized by the astrometry.
    if (obj_ra > min_ra) & (obj_ra < max_ra) & \
         (obj_dec > min_dec) & (obj_dec < max_dec):
        
        header_fields = get_fit_fields(image_file_name, \
                                       XY_CENTER_FIT_HEADER_FIELDS)
        
        try:
            x_center = int(header_fields[CRPIX1])
            y_center = int(header_fields[CRPIX2])
            
            # Retrieve the index in the astrometry list saved as first index.
            # This index corresponds to the object of interest.
            first_object = xy_data[indexes[0]] 
            
            obj_x = int(first_object[XY_DATA_X_COL])
            obj_y = int(first_object[XY_DATA_Y_COL])
            
            # Check that the X,Y coordinates for the object of interest are
            # into a distance from the center of the image.
            if (obj_x < x_center - x_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (obj_x > x_center + x_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (obj_y < y_center - y_center * XY_PERCENT_DEV_FROM_CENTER) | \
                (obj_y > y_center + y_center * XY_PERCENT_DEV_FROM_CENTER):
            
                success = False             
                
                logging.error("X,Y coordinates for object to far from " + \
                              "center in " + image_file_name)
        except KeyError as ke:
            logging.warning("Header field 'for XY center not found in file " + \
                            image_file_name)  
        
    else:
        logging.error("RA DEC coordinates given by astrometry does not " + \
                      "contain object in image: " + \
                      image_file_name)
        
        success = False
        
    if len(set(identifiers)) < len(identifiers):
        logging.error("Duplicated coordinates for some object in: " + \
                      image_file_name)
        
    if len([x for x in identifiers if x == '0']) == 0:
        logging.error("No coordinates identified for object of interest in: " + \
                      image_file_name)        
    
    return success    

def write_coord_catalogues(image_file_name, catalog_full_file_name, \
                           object, object_references):
    """Writes the x,y coordinates of a FITS file to a text file.    
    
    This function opens the FITS file that contains the table of x,y 
    coordinates and write these coordinates to a text file that only
    contains this x,y values. This text file will be used later to calculate
    the photometry of the objects on these coordinates.
    
    Keyword arguments:
    image_file_name -- Name of the file of the image.
    catalog_full_file_name -- Name of the catalog to write
    object -- Data of the object corresponding to the image.
    object_references -- Coordinates for other objects in the field of the 
        object of interest.
                           
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
        logging.debug("xyls file name: " + xyls_file_name)
        logging.debug("rdls file name: " + rdls_file_name)        
        logging.debug("Catalog file name: " + catalog_full_file_name)
        
        # Get only the file name.
        catalog_file_name = os.path.split(catalog_full_file_name)[-1]
        object_name = \
            catalog_file_name[:catalog_file_name.find(DATANAME_CHAR_SEP)]
        
        logging.debug("Object name: " + object_name)

        # Read x,y and ra,dec data from fit table.
        xy_data = get_fit_table_data(xyls_file_name)
        rd_data = get_fit_table_data(rdls_file_name)
        
        # Get the indexes for x,y and ra,dec data related to the
        # objects received.
        indexes, identifiers = \
            get_indexes_for_obj_cood(rd_data, object, object_references)  
            
        # Check if any object has been found in the image.
        if len(indexes) > 0:              
            # Check if the coordinates complies with the 
            # coordinates validation criteria.
            if check_celestial_coordinates(image_file_name, object, indexes, \
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
            logging.debug("Catalog file not saved, " + \
                          "no objects found by astrometry")
    else:
        logging.debug("X,Y coordinates file '" + xyls_file_name + \
                      "' does not exists so catalog file could not be created.")
        
    return success
        
def read_objects_references(objects):
    """Get RA, DEC coordinates for the reference objects of those received.
    
    For each object of interest received there are several objects (reference
    objects) in the field used to calculate differential photometry.
    This function received a set of objects of interest and for each object 
    returns the coordinates of all the reference objects it has.
    
    Keyword arguments:
    objects -- Objects for which the coordinates of its reference objects are
    returned.
    
    Returns:    
    List of sublists. Each sublist contains the coordinates of the reference 
    objects for an object received. These sublists follow the same order that
    the objects received.    
    """        
    
    objects_references = []
    
    # For each object get the coordinates of its reference objects.
    for obj in objects:
        objects_references.append(read_references_for_object(obj[OBJ_NAME_COL]))
    
    return objects_references    
        
def do_astrometry(progargs):
    """ Get the astrometry for all the images found from the current directory.
        
    This function searches directories that contains files of data images.
    When a directory with data images is found the astrometry is calculated
    for each data image calling an external program from 'astrometry.net'.
    The x,y positions calculated are stored to a file that contains only 
    those x and y position to be used later in photometry.
    
    Keyword arguments:
    progargs -- Program arguments. 
        
    """
    
    logging.info("Doing astrometry ...")

    # Initializes images that store summary information of the whole process.
    number_of_images = 0
    number_of_successfull_images = 0    
    images_without_astrometry = []
    
    # Read the list of objects of interest.
    objects = read_objects_of_interest(progargs.interest_object_file_name)
    
    # Read the coordinates of the reference objects that has each object of
    # interest.
    objects_references = read_objects_references(objects)

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:             
                logging.debug("Found a directory for data: " + path)

                # Get the list of files ignoring hidden files.
                files_to_catalog = \
                    [fn for fn in glob.glob(os.path.join(path, "*" + \
                                                         DATA_FINAL_PATTERN)) \
                    if not os.path.basename(fn).startswith('.')]
                    
                logging.debug("Found " + str(len(files_to_catalog)) + \
                              " files to catalog: " + str(files_to_catalog))

                # Get the astrometry for each file found.
                for fl in files_to_catalog:
                    
                    number_of_images += 1
                    
                    # Try to get RA and DEC for the object to solve the 
                    # field only around these coordinates.
                    ra_dec_param = ""
                    
                    try:
                        obj, obj_idx = get_object(objects, fl)
                        
                        # Get the RA, DEC coordinates where to center the
                        # astrometry.
                        ra = str(obj[OBJ_RA_COL])
                        dec = str(obj[OBJ_DEC_COL])
                        
                        ra_dec_param =" --ra " + ra + " --dec " + dec + \
                            " --radius " + str(SOLVE_FIELD_RADIUS)
                        
                        # Get the catalog name where the coordinates are
                        # written.
                        catalog_file_name = fl.replace(DATA_FINAL_PATTERN, \
                                                       "." + CATALOG_FILE_EXT)

                        # Check if the catalog file already exists.
                        # If it already exists the astrometry is not calculated.
                        if os.path.exists(catalog_file_name) == False :
    
                            use_sextractor = ""
                            
                            if progargs.use_sextractor_for_astrometry:
                                use_sextractor = ASTROMETRY_OPT_USE_SEXTRACTOR
    
                            command = ASTROMETRY_COMMAND + " " + \
                                ASTROMETRY_PARAMS + \
                                str(progargs.number_of_objects_for_astrometry) + \
                                " " + use_sextractor + ra_dec_param + " " + fl
                                
                            logging.debug("Executing: " + command)
    
                            # Executes astrometry.net solver to get the 
                            # astrometry of the image.
                            return_code = subprocess.call(command, \
                                shell=True, stdout=subprocess.PIPE, \
                                stderr=subprocess.PIPE)
    
                            logging.debug("Astrometry execution return code: " \
                                          + str(return_code))                            
                        else:
                            logging.debug("Catalog file already exists: " + \
                                          catalog_file_name)
                            return_code = 0
                            
                        if return_code == 0:
                            # Generates catalog files with x,y and ra,dec values 
                            # and if it successfully count it. 
                            if write_coord_catalogues(fl, catalog_file_name, \
                                                      obj, \
                                                      objects_references[obj_idx]):
                                number_of_successfull_images = \
                                    number_of_successfull_images + 1
                            else:
                                images_without_astrometry.extend([fl])
                            
                    except ObjectNotFound as onf:
                        logging.debug("Object not found related to file: " + \
                                      onf.filename)

    logging.info("Astrometry results:")
    logging.info("- Number of images processed: " + str(number_of_images))
    logging.info("- Images processed successfully: " + \
                 str(number_of_successfull_images))
    logging.info("- Number of images without astrometry: " + \
                 str(len(images_without_astrometry)))    
    logging.info("- List of images without astrometry: " + \
                 str(images_without_astrometry))