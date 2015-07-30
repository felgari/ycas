# -*- coding: utf-8 -*-

# Copyright (c) 2015 Felipe Gallego. All rights reserved.
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

"""This module performs some calculations with coordinates used in astrometry.

"""

import logging
import starsset
from fitfiles import get_fit_fields
from constants import *

# Error margin when assigning astrometry coordinates.
ASTROMETRY_COORD_RANGE = 0.08    
XY_PERCENT_DEV_FROM_CENTER = 0.7

# Columns in celestial coordinates table.
RD_DATA_RA_COL = 0
RD_DATA_DEC_COL = 1

CRPIX1 = "CRPIX1"
CRPIX2 = "CRPIX2"

XY_CENTER_FIT_HEADER_FIELDS = [CRPIX1, CRPIX2]

def get_rd_index(rd_data, ra, dec): 
    """ Get the index of the RA, DEC pair whose values are more close to 
    those received.
    
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
        logging.debug("No match for star coordinates, min. diff. are: %.10g %.10g" %
                      (ra_min_diff, dec_min_diff))
        
    return index

def get_indexes_for_star_coor(rd_data, star):
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
        # Get the indexes for the stars references.
        for star_of_field in star.field_stars:
            new_index = get_rd_index(rd_data, star_of_field.ra, \
                                     star_of_field.dec)
            
            # Check that an index has been found for this star.
            if new_index >= 0:
                logging.debug("Index for reference %.10g, %.10g with id %d is %d" %
                              (star_of_field.ra, star_of_field.dec,
                              star_of_field.id, new_index))        
                                         
                indexes.extend([new_index])  
                
                identifiers.extend([star_of_field.id])    
            else:
                logging.debug("Index for reference %.10g, %.10g with id %d not found" %
                              (star_of_field.ra, star_of_field.dec, 
                               star_of_field.id))
    else:
        logging.warning("Index for star %s not found" % star.name)

    return indexes, identifiers
    
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
                
                logging.error("X,Y coordinates for star to far from %s center in " %
                              (image_file_name))
        except KeyError as ke:
            logging.warning("Header field 'for XY center not found in file %s" %
                            (image_file_name))  
        
    else:
        logging.error("RA DEC coordinates given by astrometry does not contain star in image: %s" %
                      (image_file_name))
        
        success = False
        
    if len(set(identifiers)) < len(identifiers):
        logging.error("Duplicated coordinates for some star in: %s" %
                      (image_file_name))
        
    if len([x for x in identifiers if x == '0']) == 0:
        logging.error("No coordinates identified for star of interest in: %s" %
                      (image_file_name))        
    
    return success