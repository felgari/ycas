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

"""Obtains the calibrated magnitude of stars using the atmospheric extinction
corrected magnitudes calculated previously.

The magnitude values are stored in different files for each star.
"""

import numpy as np
from scipy import stats
import logging
from constants import *
from textfiles import *

MIN_VALUE_TO_CALC_COEF = 0.01

class TransformingCoefficient(object):   
    """Stores a set of transforming coefficient used to calibrate magnitudes in
    a concrete day.
    """
    
    def __init__(self, day, B_V_observed_mag, V_observed_mag, \
                 B_V_std_mag, V_std_mag):
        
        self._day = day
        
        self._c1, self._c2, self._c3, self._c4 = \
            self.calculate_transforming_coefficients(B_V_observed_mag, 
                                                     V_observed_mag, 
                                                     B_V_std_mag, 
                                                     V_std_mag)
            
    def __str__(self):
        return "C1: %.5g C2: %.5g C3: %.5g C4: %.5g" % \
            (self._c1, self._c2, self._c3, self._c4)
            
    @property
    def day(self):
        return self._day
            
    @property 
    def c1(self):
        return self._c1       
    
    @property 
    def c2(self):
        return self._c2       
    
    @property 
    def c3(self):
        return self._c3       
    
    @property 
    def c4(self):
        return self._c4                    
        
    def calculate_transforming_coefficients(self, \
                                                B_V_observed_mag, \
                                                V_observed_mag, \
                                                B_V_std_mag, \
                                                V_std_mag):
        """Calculate the transforming coefficients.
        
        Args:
            B_V_observed_mag: List of B-V values for a star.
            V_observed_mag: List of V magnitudes for a star.
            B_V_std_mag: List of B-V values for standard a star.
            V_std_mag: List of V magnitudes for standard a star.
                                            
        Returns:        
            The two slopes and two intercepts to transform the magnitudes.
            
        """   
        
        # Default values.
        slope1 = 1.0
        intercept1 = 0.0  
        slope2 = 1.0
        intercept2 = 0.0      
        
        # First calculation is:
        # Vstd - V0 = slope * (B-V)std + intercept
        y = np.array(V_std_mag).astype(np.float) - \
            np.array(V_observed_mag).astype(np.float)
            
        # Only if the difference between the standard magnitude and the 
        # observed one is greater than a given value calculate the 
        # transforming coefficients.
        if np.mean(y) > MIN_VALUE_TO_CALC_COEF: 
            
            print np.array(B_V_std_mag)
            print y
            
            slope1, intercept1, r_value1, p_value1, std_err1 = \
                stats.linregress(np.array(B_V_std_mag), y)
                
            # Second calculation is:
            # (B-V)std = slope * (B-V)obs + intercept
            
            print B_V_observed_mag
            print B_V_std_mag
            
            slope2, intercept2, r_value2, p_value2, std_err2 = \
                stats.linregress(B_V_observed_mag, B_V_std_mag)            
        
        return slope1, intercept1, slope2, intercept2        

def get_transforming_coefficients(magnitudes):
    """Get the transforming coefficients to calculate the calibrated magnitudes.
    
    From the extinction corrected magnitudes of standard star 
    get the transforming coefficients used to calculate the
    calibrated magnitudes.
    
    Args:
        magnitudes: Magnitudes of the stars.
    
    Returns:        
        The transforming coefficients to calculate the calibrated magnitudes.  
    """  
    
    trans_coef = []
    
    # Calculate the coefficients by day.
    for d in magnitudes.days:
        
        # To store the magnitudes for a day.
        B_V_mags_of_day = []
        V_mags_of_day = []
        
        B_V_std_mags_of_stars = []
        V_std_mags_of_stars = []        
        
        # Use only standard stars.
        for mag in magnitudes.std_stars:
            
            # Get the magnitudes of current star.
            star_mags = magnitudes.get_mags_of_star(mag.name)
            
            # Get the stars with measures in the current day.
            stars_of_B_filter = [m for m in star_mags \
                       if m.day == d and m.filter == B_FILTER_NAME]
            
            stars_of_V_filter = [m for m in star_mags \
                       if m.day == d and m.filter == V_FILTER_NAME] 
            
            # Check there is at least two measures and the number matches both
            # sets.
            # Is is assumed that measurements for each filter are well paired.
            if len(stars_of_B_filter) > 1 and len(stars_of_V_filter) > 1 and \
                len(stars_of_B_filter) == len(stars_of_V_filter):
                
                B_mags_of_star = np.array([mag.ext_cor_mag \
                                          for mag in stars_of_B_filter])
                V_mags_of_star = np.array([mag.ext_cor_mag \
                                          for mag in stars_of_V_filter]) 
                
                B_mags = B_mags_of_star.astype(np.float)
                V_mags = V_mags_of_star.astype(np.float)
            
                # Compute the mean for the magnitudes of this star
                # in each filter. 
                B_mean = np.mean(B_mags)
                V_mean = np.mean(V_mags)

                # Store the mean values of the magnitude observed for
                # these stars to compute the transforming coefficients 
                # of this day.
                B_V_mags_of_day.extend([B_mags - V_mags])
                V_mags_of_day.extend([V_mags])
                
                # Add the standard magnitudes of the star.
                B_std_mag_star = \
                    np.array([float(magnitudes.get_std_mag(mag.star_name, \
                                                           B_FILTER_NAME))] * \
                             len(B_mags))
                    
                V_std_mag_star = \
                    np.array([float(magnitudes.get_std_mag(mag.star_name, \
                                                           V_FILTER_NAME))] * \
                             len(V_mags))
                
                B_V_std_mags_of_stars.extend([B_std_mag_star - \
                                                V_std_mag_star])
                
                V_std_mags_of_stars.extend(V_std_mag_star)
            else:
                logging.debug("There is not enough measurements in all " +
                              "filters for star %s at day %d." % 
                              (mag.name, d))

            # The coefficients are calculated only if there is enough values,
            # (any list could be used for this check).
            if len(V_mags_of_day) > 0:
    
                # Calculate the transforming coefficients of this day using the
                # magnitudes found for this day.  
                tc = TransformingCoefficient(d,
                                             B_V_mags_of_day, \
                                             V_mags_of_day, \
                                             B_V_std_mags_of_stars, \
                                             V_std_mags_of_stars)
                    
                trans_coef.append(tc)          
            else:
                logging.debug("No transforming coefficients could be " + 
                              "calculated for day (there is only one " +
                              "standard star) %d " % (d))
            
    return trans_coef
    
def calibrated_magnitudes(magnitudes, trans_coef):
    """Calculate the calibrated magnitudes and save them to a file.
    
    Using the transformation coefficients calculate the calibrated
    magnitudes from the extinction corrected magnitudes and save them
    to a file.
    
    Args:
        magnitudes: Magnitudes of the stars. 
        
    """    
        
    # Calculate for each star.
    for s in magnitudes.stars:
        
        # Only for those days with coefficients calculated.
        for tc in trans_coef:
            
            # Get the day of current transformation coefficient.
            day = tc.day
            
            # Magnitudes of the star
            star_mags = magnitudes.get_mags_of_star(s.name)
            
            # To store the magnitudes for this star in each filter.
            mags_of_B_filter = [m for m in star_mags \
                       if m.day == day and m.filter == B_FILTER_NAME]
            
            mags_of_V_filter = [m for m in star_mags \
                       if m.day == day and m.filter == V_FILTER_NAME]    
            
            # If this star has measurements for all the filters.
            # Is is assumed that measurements for each filter are well paired.
            if len(mags_of_B_filter) > 0 and len(mags_of_V_filter) > 0 and \
                len(mags_of_B_filter) == len(mags_of_V_filter):
                
                B_mags_of_obj = np.array([m.ext_cor_mag \
                                          for m in mags_of_B_filter])
                
                V_mags_of_obj = np.array([m.ext_cor_mag \
                                          for m in mags_of_V_filter])
                
                B_obs_mags = B_mags_of_obj.astype(np.float)
                V_obs_mags = V_mags_of_obj.astype(np.float) 
                B_V_obs_mags = B_obs_mags - V_obs_mags
                
                # Calculate the calibrated magnitudes.
                B_V_cal_mag = tc.c3 * B_V_obs_mags + tc.c4
                V_cal_mag = V_obs_mags + tc.c1 * B_V_cal_mag + tc.c2
                
                B_cal_mag = B_V_cal_mag + V_cal_mag
                
                # Set the calibrated magnitudes of the star in B filter.
                for j in range(len(mags_of_B_filter)):
                    curr_B_mag = mags_of_B_filter[j]
                    
                    curr_B_mag.calib_mag = B_cal_mag[j]

                # Set the calibrated magnitudes of the star in V filter.
                for j in range(len(mags_of_V_filter)):
                    curr_V_mag = mags_of_V_filter[j]
                    
                    curr_V_mag.calib_mag = V_cal_mag[j]
                
                logging.info("Calibrated magnitudes are calculated " +
                             "for star %s on day %d." % (s.name, day))
                             
            else:
                logging.debug("Calibrated magnitudes are not calculated for star: %s at day %d, magnitudes not available for all the filters." \
                              % (s.name, day))                

def get_calibrated_magnitudes(magnitudes):
    """Calculate the calibrated magnitude of the stars.
    
    Calculate the calibrated magnitude of the stars 
    using the extinction coefficient calculated previously and
    calibrating with the standard magnitudes.
    
    Args:
        magnitudes: Magnitudes of the stars.
        
    """

    # Calculate from extinction corrected magnitudes of no standard stars
    # the transformation coefficients to calculate the calibrated magnitudes.
    trans_coef = get_transforming_coefficients(magnitudes)
        
    # Calculate the calibrated magnitudes for all the stars.
    calibrated_magnitudes(magnitudes, trans_coef)