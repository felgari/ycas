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

"""Obtains the calibrated magnitude of objects using the atmospheric extinction
corrected magnitudes calculated previously.

The magnitude values are stored in different files for each object.
"""

import logging
import numpy as np
from scipy import stats
from constants import *
from textfiles import *

def calculate_transforming_coefficients(B_V_observed_mag, \
                                        V_observed_mag, 
                                        B_V_std_mag, 
                                        V_std_mag):
    """Calculate the transforming coefficients.
    
    Keyword arguments:
    B_V_observed_mag -- List of B-V values for object.
    V_observed_mag -- List of V magnitudes for object.
    B_V_std_mag -- List of B-V values for standard object.
    V_std_mag -- List of V magnitudes for standard object.
                                        
    Returns:        
    The two slopes and two intercepts to transform the magnitudes.
    """   
    
    print B_V_observed_mag
    print V_observed_mag
    print B_V_std_mag
    print V_std_mag
    
    # First calculation is:
    # Vstd - V0 = slope * (B-V)std + intercept
    y = np.array(V_std_mag).astype(np.float) - \
        np.array(V_observed_mag).astype(np.float)
    
    slope1, intercept1, r_value1, p_value1, std_err1 = \
        stats.linregress(np.array(B_V_std_mag), y)
        
    # Second calculation is:
    # (B-V)std = slope * (B-V)obs + intercept
    
    slope2, intercept2, r_value2, p_value2, std_err2 = \
        stats.linregress(B_V_observed_mag, B_V_std_mag)      
    
    return slope1, intercept1, slope2, intercept2

def get_transforming_coefficients(objects, \
                                  std_obj_idxs, \
                                  ext_corr_mags, days, filters):
    """Get the transforming coefficients to calculate the calibrated magnitudes.
    
    From the extinction corrected magnitudes of standard object 
    get the transforming coefficients used to calculate the
    calibrated magnitudes.
    
    Keyword arguments:
    objects -- List of objects.
    std_obj_idxs -- Indexes of the standard objects.
    ext_corr_mags -- The magnitudes with the extinction corrected.
    days -- List of days.
    filters -- List of filters.
    
    Returns:        
    The transforming coefficients to calculate the calibrated magnitudes    
    """  
    
    trans_coef = []
    
    # Calculate the coefficients by day.
    for d in days:
        
        # To store the magnitudes for a day.
        B_V_mags_of_day = []
        V_mags_of_day = []
        
        B_V_std_mags_of_objects = []
        V_std_mags_of_objects = []        
        
        # Get filter magnitudes for each object.
        for i in range(len(std_obj_idxs)):
            
            object_index = std_obj_idxs[i]
            
            # Get the list of corrected magnitudes for this object. 
            obj_mags = ext_corr_mags[i]
            
            # To store the magnitudes for this object in each filter.
            mags_of_B_filter = [m for m in obj_mags \
                       if m[DAY_CEM_COL] == d and \
                       m[FILTER_CEM_COL] == B_FILTER_NAME]
            
            mags_of_V_filter = [m for m in obj_mags \
                       if m[DAY_CEM_COL] == d and \
                       m[FILTER_CEM_COL] == V_FILTER_NAME] 
            
            # If this object has measurements for all the filters.
            # Is is assumed that measurements for each filter are well paired.
            if len(mags_of_B_filter) > 0 and len(mags_of_V_filter) > 0 and \
                len(mags_of_B_filter) == len(mags_of_V_filter):
                
                B_mags_of_obj = np.array(mags_of_B_filter)[:,CE_MAG_CEM_COL]
                V_mags_of_obj = np.array(mags_of_V_filter)[:,CE_MAG_CEM_COL] 
                
                B_mags = B_mags_of_obj.astype(np.float)
                V_mags = V_mags_of_obj.astype(np.float)
            
                # Compute the mean for the magnitudes of this object
                # in each filter. 
                B_mean = np.mean(B_mags)
                V_mean = np.mean(V_mags)

                # Store the mean values of the magnitude observed for
                # these objects to compute the transforming coefficients 
                # of this day.
                B_V_mags_of_day.extend([B_mean - V_mean])
                V_mags_of_day.extend([V_mean])
                
                # Add the standard magnitudes of the object.
                B_std_mag_object = float(objects[object_index][OBJ_B_MAG_COL])
                V_std_mag_object = float(objects[object_index][OBJ_V_MAG_COL])
                
                B_V_std_mags_of_objects.extend([B_std_mag_object - \
                                                V_std_mag_object])
                
                V_std_mags_of_objects.extend([V_std_mag_object])
            else:
                logging.warning("There is not measurements in all filters " + \
                                "for object: " + \
                                objects[object_index][OBJ_NAME_COL] + \
                                " at day " + str(d))

        # The coefficients are calculated only if there is enough values,
        # (any list could be used for this check).
        if len(V_mags_of_day) > 0:
            # Calculate the transforming coefficients of this day using the
            # magnitudes found for this day.   
            c1, c2, c3, c4 = \
                calculate_transforming_coefficients(B_V_mags_of_day, \
                                                    V_mags_of_day, \
                                                    B_V_std_mags_of_objects, \
                                                    V_std_mags_of_objects)
                
            trans_coef.append([d, c1, c2, c3, c4])          
        else:
            logging.warning("No transforming coefficients could be " + 
                            "calculated for day (there is only one " +
                            "standard object) " + str(d))
            
    return trans_coef
    
def calibrated_magnitudes(objects, obj_indexes, ext_corr_mags, trans_coef):
    """Calculate the calibrated magnitudes and save them to a file.
    
    Using the transformation coefficients calculate the calibrated
    magnitudes from the extinction corrected magnitudes and save them
    to a file.
    
    Keyword arguments:
    objects -- List of objects.
    obj_indexes -- List of indexes of the objects.
    ext_corr_mags -- Magnitudes with extinction corrected.
    trans_coef -- Transformation coefficients needed to get calibrated
        magnitudes.     
        
    """    
        
    # Calculate for each object.
    for i in obj_indexes:
        
        # Only for those days with coefficients calculated.
        for tc in trans_coef:
            
            # Get the day of current transformation coefficient.
            day = tc[DAY_TRANS_COEF_COL]
            
            # Get also the coefficients.
            c1 = tc[C1_TRANS_COEF_COL]
            c2 = tc[C2_TRANS_COEF_COL]
            c3 = tc[C3_TRANS_COEF_COL]
            c4 = tc[C4_TRANS_COEF_COL]
            
            # Magnitudes of the object
            obj_mags = ext_corr_mags[i]
            
            # Data for this object.
            obj = objects[obj_indexes[i]]
            
            # To store the magnitudes for this object in each filter.
            mags_of_B_filter = [m for m in obj_mags \
                       if m[DAY_CEM_COL] == day and \
                       m[FILTER_CEM_COL] == B_FILTER_NAME]
            
            mags_of_V_filter = [m for m in obj_mags \
                       if m[DAY_CEM_COL] == day and \
                       m[FILTER_CEM_COL] == V_FILTER_NAME]    
            
            cal_magnitudes = []
            
            # If this object has measurements for all the filters.
            # Is is assumed that measurements for each filter are well paired.
            if len(mags_of_B_filter) > 0 and len(mags_of_V_filter) > 0 and \
                len(mags_of_B_filter) == len(mags_of_V_filter):
                
                B_mags_of_obj = np.array(mags_of_B_filter)[:,CE_MAG_CEM_COL]
                V_mags_of_obj = np.array(mags_of_V_filter)[:,CE_MAG_CEM_COL]
                
                B_obs_mags = B_mags_of_obj.astype(np.float)
                V_obs_mags = V_mags_of_obj.astype(np.float) 
                B_V_obs_mags = B_obs_mags - V_obs_mags
                
                # Calculate the calibrated magnitudes.
                B_V_cal_mag = c3 * B_V_obs_mags + c4
                V_cal_mag = V_obs_mags + c1 * B_V_cal_mag + c2
                
                B_cal_mag = B_V_cal_mag + V_cal_mag
                
                # First the B magnitudes of the object.
                for j in range(len(mags_of_B_filter)):
                    om = mags_of_B_filter[j]
                    
                    cal_magnitudes.append([om[JD_TIME_CEM_COL], \
                                          B_cal_mag[j], \
                                          om[CE_MAG_CEM_COL], \
                                          om[INST_MAG_CEM_COL], \
                                          om[FILTER_CEM_COL]])

                for j in range(len(mags_of_V_filter)):
                    om = mags_of_V_filter[j]
                    
                    cal_magnitudes.append([om[JD_TIME_CEM_COL], \
                                          V_cal_mag[j], \
                                          om[CE_MAG_CEM_COL], \
                                          om[INST_MAG_CEM_COL], \
                                          om[FILTER_CEM_COL]])
                
                # Save the calibrated magnitudes to a file.
                save_magnitudes_to_file(obj[OBJ_NAME_COL], CAL_MAG_SUFFIX, \
                                        [cal_magnitudes])
                
                logging.debug("Calibrated magnitudes are calculated " + \
                                "for object: " + obj[OBJ_NAME_COL] + \
                                " at day " + str(day) + ".")
            else:
                logging.warning("Calibrated magnitudes are not calculated " + \
                                "for object: " + obj[OBJ_NAME_COL] + \
                                " at day " + str(day) + \
                                ", object magnitudes not available for " + \
                                "all the filters.")                

def get_calibrated_magnitudes(objects, std_obj_idxs, no_std_obj_idxs, \
                              ext_corr_mags, days, filters):
    """Calculate the calibrated magnitude of the objects.
    
    Calculate the calibrated magnitude of the objects 
    using the extinction coefficient calculated previously and
    calibrating with the standard magnitudes.
    
    Keyword arguments:
    objects -- List of objects.
    std_obj_idxs -- Indexes of standard objects.
    no_std_obj_idxs -- Indexes of no standard objects.
    ext_corr_mags -- List of extinction corrected magnitudes. 
    days -- Days of the magnitudes.
    filters -- Filters used.
        
    """
        
    # Calculate from extinction corrected magnitudes of no standard objects
    # the transformation coefficients to calculate the calibrated magnitudes.
    trans_coef = get_transforming_coefficients(objects, \
                                               std_obj_idxs, \
                                               ext_corr_mags, \
                                               days, filters)
        
    # Build an index that follows the order of the magnitudes inserted.
    obj_indexes = std_obj_idxs
    obj_indexes.extend(no_std_obj_idxs)
        
    # Calculate the calibrated magnitudes for all the objects.
    calibrated_magnitudes(objects, obj_indexes, ext_corr_mags, trans_coef)