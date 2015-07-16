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

""" This module calculates the magnitudes applying the atmospheric extinction
correction when possible, this is, when there are enough standard stars.

"""

import logging
import numpy as np
from scipy import stats
from constants import *
from textfiles import *

def get_ra_dec_for_object(objects, object_name):
    """Returns the coordinates for an object from a list of objects.
    
    Receives the name of an object and a set of objects with the coordinates
    of these objects.  
    
    Keyword arguments:
    objects -- List of objects. 
    object_name -- The name of the object whose coordinates are requested.
    
    Returns:
    The coordinates of the object indicated.    
    
    """
    
    ra = 0.0
    dec = 0.0
    
    # Iterate over the list of object.s
    for obj in objects:
        # Check current object by name.
        if obj[OBJ_NAME_COL] == object_name:
            ra = float(obj[OBJ_RA_COL])
            dec = float(obj[OBJ_DEC_COL])
    
    return ra, dec  

def get_object_references(rdls_file, objects):
    """Search the indexes in a RDLS that corresponds to a set of objects.
    
    From the RDLS file and the list of objects returns the index in the RDLS 
    file whose coordinates get the better match for those of the object and 
    also the name of the object.
    
    Keyword arguments:
    rdls_file -- RDLS file where to look for the coordinates.
    objects -- Objects to look for in the RDLS file using its coordinates.
    
    Returns:    
    The list of indexes related to a RDLS file whose coordinates corresponds
    to the objects received.
    
    """
    
    index = -1
    
    # Get the name of the object related to this RDLS file.
    object_name = get_object_name_from_rdls(rdls_file)
    
    # Get coordinates for the object related to the RDLS file.
    ra, dec = get_ra_dec_for_object(objects, object_name)    
    
    # Get RDLS data.
    rdls_data = get_rdls_data(rdls_file) 
    
    ra_diff = 1000.0
    dec_diff = 1000.0 
    
    i = 0
    for rd in rdls_data:
        # Compute the difference between the coordinates of the
        # object in this row and the object received.  
        temp_ra_diff = abs(float(rd[RDLS_RA_COL_NUMBER]) - ra)
        temp_dec_diff = abs(float(rd[RDLS_DEC_COL_NUMBER]) - dec)   
        
        # If current row coordinates are smaller than previous this
        # row is chosen as candidate for the object.
        if temp_ra_diff < ra_diff and temp_dec_diff < dec_diff:
            ra_diff = temp_ra_diff
            dec_diff = temp_dec_diff
            index = i        
    
        i += 1
        
    logging.debug("Found index for object " + object_name + " at " + str(index))
        
    return index, object_name
            
def get_day_of_measurement(time_jd):
    """Returns the julian day related to the Julian time received.
    
    The day is assigned to that which the night begins.
    So a JD between .0 (0:00:00) and .4 (+8:00:00) belongs to the day before.
    
    Keyword arguments:
    time_jd -- A Julian time value.
    
    Returns:        
    The Julian day related to the Julian time received. 
    
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
    """Get the standard magnitude of an object in the filter indicated.
    
    Keyword arguments:
    object_data -- All the data for an object.
    filter -- The filter to use.
    
    Returns:        
    The magnitude of this object for the filter indicated taken from the data
    of the object.
        
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
    """Calculates the extinction coefficient using the data received.
    
    Keyword arguments:
    mag_data -- The data with all the magnitude values needed to calculate
    the linear regression for the extinction coefficient.
    
    Returns:        
    The extinction coefficient calculated.
    
    """
    
    # Create a numpy array with the data received.
    a = np.array(mag_data)
    
    # Sort the data only by JD time.
    na = a[a[:,JD_TIME_CE_CALC_DATA].argsort()]
    
    # Extract the columns necessary to calculate the linear regression.
    inst_mag = na[:,INST_MAG_CE_CALC_DATA]
    std_mag = na[:,STD_MAG_CE_CALC_DATA]
    airmass = na[:,AIRMASS_CE_CALC_DATA]
    
    # Subtract these columns to get the y.
    y = inst_mag.astype(np.float) - std_mag.astype(np.float)
    
    # The calculation is:
    # Minst = m + K * airmass
    # Where K is the regression coefficient
    slope, intercept, r_value, p_value, std_err = \
        stats.linregress(airmass.astype(np.float), y)
    
    logging.debug("Linear regression for day: " + str(a[0][DAY_CE_CALC_DATA]) +
                  " slope: " + str(slope) + " intercept: " + str(intercept) + \
                  " r-value: " + str(r_value) + " p-value: " + str(p_value) + \
                  " std_err: " + str(std_err))
    
    return slope, intercept

def valid_data_to_calculate_ext_cof(obj_data_for_ext_coef):
    """Examines the data from an object to ensure are coherent.
    
    I.e., airmass and instrumental magnitude are proportional, greater airmass
    is also a greater magnitude, otherwise these data is not considered valid. 
    
    Keyword arguments:
    obj_data_for_ext_coef -- Data of magnitude and airmass for an object.
    
    Returns:        
    True if coherent, False otherwise.
    
    """
    
    # To know if air mass and magnitude are proportional a linear regression is
    # calculated and the slope inspected. 
    slope, intercept = calculate_extinction_coefficient(obj_data_for_ext_coef)
    
    return slope > 0.0    
    

def collect_mag_for_object(days, filters, obj, object_inst_mags):
    
    obj_data_for_ext_coef = []
    
    # Find magnitudes for this object.
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
                if im[INST_MAG_COL] != INDEF_VALUE:
                    filters.add(im[FILTER_COL])
                    obj_data_for_ext_coef.append([day, im[JD_TIME_COL], \
                                                  im[INST_MAG_COL], std_mag, \
                                                  im[AIRMASS_COL], \
                                                  im[FILTER_COL], \
                                                  obj[OBJ_NAME_COL]])
                else:
                    logging.warning("Standard magnitude undefined for " + \
                                    "object " + obj[OBJ_NAME_COL])
            else:
                logging.warning("Standard magnitude not found for " + \
                                "object " + obj[OBJ_NAME_COL] + \
                                "in filter " + im[FILTER_COL])
                
    return obj_data_for_ext_coef  

def extinction_coefficient(objects, std_obj_idxs, inst_mag):
    """Calculates the extinction coefficient using the standard objects.
    
    Keyword arguments:
    objects -- The list of all the objects.
    std_obj_idxs -- The indexes in the list that correspond to standard 
        objects.
    inst_mag -- The magnitude values.
    
    Returns:        
    The extinction coefficient calculated, the days of each calculation and 
    the filters. 
    """
    
    ext_coef = []
    
    # To store all the data necessary to calculate extinction coefficients.
    calc_data_for_ext_coef = []
    
    # To store the different days and filters.
    days = set()
    filters = set()    
    
    # Process each standard object.
    for i in std_obj_idxs:
                
        # Retrieve the object data and the instrumental magnitudes measured.
        obj = objects[i]   
        object_inst_mags = inst_mag[i]
        
        # Data of current object necessary to calculate extinction coefficients.
        obj_data_for_ext_coef = collect_mag_for_object(days, filters, obj, \
                                                       object_inst_mags)
        
        # The magnitudes collected for this object are evaluated to check its
        # validity to to .
        for d in days:            
            data_subset = [m for m in obj_data_for_ext_coef \
                           if m[DAY_CE_CALC_DATA] == d]
            
            # Check if there is data of this object for this day.
            if len(data_subset) >= MIN_NUM_STD_MEASURES:            
                if valid_data_to_calculate_ext_cof(data_subset) == True:
                    calc_data_for_ext_coef.append(data_subset)
                else:
                    logging.warning("Data to calculate extinction " + \
                                    "coefficient discarded from object " +
                                    obj[OBJ_NAME_COL] + " for day " + str(d))
    
    # If there is any data to calculate extinction coefficient.
    if len(calc_data_for_ext_coef) > 0:
        for d in days:
            logging.debug("Calculating extinction coefficient for day " + \
                          str(d) + " with " + \
                          str(len(calc_data_for_ext_coef)) + " magnitudes.")
            for f in filters:
                mag = [m for m in calc_data_for_ext_coef \
                       if m[DAY_CE_CALC_DATA] == d and \
                       m[FILTER_CE_CALC_DATA] == f]
                
                # Check if there is data of this object for this day.
                if len(mag) > 0:
                    slope, intercept = calculate_extinction_coefficient(mag)
            
                    ext_coef.append([d, f, slope, intercept])
    else:
        logging.warning("There is not enough data to calculate extinction " + \
                        "coefficients")
        
    return ext_coef, days, filters

def get_extinction_coefficient(ext_coef, day, filter):
    """ Returns parameters of the extinction coefficient for a day and filter.
    
    Keyword arguments:
    ext_coef -- All the extinction coefficients calculated.
    day -- The day of interest.
    filter -- The filter of interest.
    
    Returns:        
    The slope and intercept value calculated for a day and filer given.
        
    """
    
    # Default values that don't change the returns the instrumental
    # magnitude for the extinction corrected magnitude.
    slope = 1.0
    intercept = 0.0
    
    ec = [e for e in ext_coef \
                   if e[DAY_CE_DATA] == day and e[FILTER_CE_DATA] == filter]
                   
    # Maybe for the filter indicated has not been calculated an
    # extinction coefficient.
    if ec != None and len(ec) > 0:
        slope = ec[0][SLOPE_CE_DATA]
        intercept = ec[0][INTERCEPT_CE_DATA]
    
    return slope, intercept 

def get_extinction_corrected_mag(obj, \
                                 object_inst_mags, \
                                 ext_coef):
    """Get the magnitude corrected for extinction for the object received.
     
    The extinction coefficients are applied and the magnitudes 
    calculated are saved to a file and returned.
    
    Keyword arguments:
    obj -- The object whose magnitudes are corrected. 
    object_inst_mags -- The magnitudes to correct.
    ext_coef -- The extinction coefficients to apply.
    
    Returns:        
    The magnitudes corrected.   
        
    """
    
    magnitudes = []
    
    # Process the instrumental magnitudes measured for this object.
    for inst_mag in object_inst_mags:
        # For each object the magnitudes are grouped in different lists.
        for im in inst_mag:
            
            # Check if the instrumental magnitude is defined.
            if im[INST_MAG_COL] != INDEF_VALUE :
            
                # Find the coefficients by day and filter.
                day = get_day_of_measurement(im[JD_TIME_COL])
                filter = im[FILTER_COL]
                
                slope, intercept = \
                    get_extinction_coefficient(ext_coef, day, filter)
                
                # Calculate the extinction corrected magnitude.
                # Mo = Minst - intercept - slope * airmass
                calc_mag = float(im[INST_MAG_COL]) - intercept - \
                    slope * float(im[AIRMASS_COL])
                    
                magnitudes.append([im[JD_TIME_COL], day, calc_mag, \
                                   im[INST_MAG_COL], im[ERR_COL], filter])
            else:
                logging.debug("Found an instrumental magnitude undefined " + \
                              "for object " + obj[OBJ_NAME_COL])
            
    # Save extinction corrected magnitude for current object.
    save_magnitudes_to_file(obj[OBJ_NAME_COL], CORR_MAG_SUFFIX, [magnitudes])  
    
    return magnitudes      

def get_extinction_corrected_magnitudes(objects, std_obj_idxs, \
                                        no_std_obj_idxs, \
                                        inst_mag):
    """ Returns the magnitudes corrected taking into account the atmospheric
        extinction, when possible.
    
    Keyword arguments:
    objects -- List of objects to process.
    std_obj_idxs -- Indexes of standard objects.
    no_std_obj_idxs -- Indexes of no standard objects.    
    inst_mag -- Instrumental magnitudes for objects of interest, standard 
        and no standard.
    
    Returns:        
    The magnitudes corrected taking into account the atmospheric extinction.
    
    """                     
            
    ext_coef, days, filters = \
        extinction_coefficient(objects, std_obj_idxs, \
                               inst_mag)   
        
    # To store extinction corrected magnitudes of all objects.
    ext_corr_mags = []
    
    # Calculate the extinction corrected magnitudes of standard objects.
    for i in std_obj_idxs:
        obj_mags = get_extinction_corrected_mag(objects[i], \
                                                inst_mag[i], \
                                                ext_coef)
        ext_corr_mags.append(obj_mags)  
        
    # Calculate the extinction corrected magnitudes of no standard objects.
    for i in no_std_obj_idxs:
        obj_mags = get_extinction_corrected_mag(objects[i], \
                                                inst_mag[i], \
                                                ext_coef)   
        
        ext_corr_mags.append(obj_mags)                   
    
    return ext_corr_mags, days, filters