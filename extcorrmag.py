#!/usr/bin/env python
# -*- coding: utf-8 -*-
from astropy.time.core import MJD_ZERO
from matplotlib.testing.jpl_units import day

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

""" This module calculates the magnitudes applying the atmospheric extinction
correction when possible, this is, when there are enough standard stars.

"""

import logging
import numpy as np
from scipy import stats
from constants import *
from textfiles import *

class ExtinctionCoefficient(object):
    """The extinction coefficient values calculated for a day and a filter.
    
    """
    
    def __init__(self, day, filter, slope, intercept):
        
        self._day = day
        self._filter = filter
        self._slope = slope
        self._intercept = intercept
        
    @property
    def day(self):
        return self._day
    
    @property
    def filter(self):
        return self._filter
    
    @property
    def slope(self):
        return self._slope
    
    @property
    def intercept(self):
        return self._intercept
    
class ExtinctionCoefficientNotFound(Exception):
    """To raise when a extinction coefficient does not exist for a day 
    and filter.
    
    """
    
    def __init__(self, day, filter):
        self._day = day
        self._filter = filter
        
    def __str__(self):
        return 'No extinction coefficient for day {day} and filter {filter}'. \
            format(day=str(self._day), filter=str(self._filter)) 
            
class CorrectedMagnitude(object):
    """ Class to store the values of a corrected magnitude. """
    
    def __init__(self, mjd):
        self._mjd = mjd
        self._day = day
        self._filter = filter
        self._corr_mag = corr_mag
        self._inst_mag = inst_mag
        self._error = error
            
    @property
    def mjd(self):
        return self._mjd
    
    @property
    def day(self):
        return self._day
    
    @property
    def filter(self):
        return self._filter
    
    @property
    def corr_mag(self):
        return self._corr_mag
    
    @property
    def inst_mag(self):
        return self._inst_mag
    
    @property
    def error(self):
        return self._error                    
        
class ExtCorrMagnitudes(object):
    """Calculates the extinction coefficients from a set of measures and
    applies them to a set of magnitudes.
    
    """ 
    
    def __init__(self, stars, inst_mag):
        self._stars = stars
        self._inst_mag = inst_mag
        
        # The list of extinction coefficients calculated.
        self._ec = []
        
        # Sets of filters and days with any calculated coefficient.
        # These values could also be retrieved from the extinction coefficients
        # calculated.
        self._filter = set()
        self._day = set() 
        
    @property
    def extinction_coefficient(self, day, filter):
        """Returns parameters of the extinction coefficient for a day 
        and filter.
        
        Args:
        day: The day of interest.
        filter: The filter of interest.
        
        Returns:        
        The slope and intercept value calculated for a day and filer given.
            
        """
        
        # Default values that don't change the returns the instrumental
        # magnitude for the extinction corrected magnitude.
        slope = 1.0
        intercept = 0.0
        
        ec = [e for e in self._ec \
                       if e.day == day and e.filter == filter]
                       
        # Maybe for the filter indicated has not been calculated an
        # extinction coefficient, so check it before assign the values.
        if ec:
            slope = ec[0].slope
            intercept = ec[0].intercept
            
            found = True
        else:
            raise ExtinctionCoefficientNotFound(day, filter)
        
        return slope, intercept  
    
    def calc_one_ext_coeff(self, mag_data):
        """Calculates the extinction coefficient using the data received.
        
        Args:
        mag_data: The data with all the magnitude values needed to calculate
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
        
        # The calculation is:
        # Minst = m + K * airmass
        # Where K is the regression coefficient    
        
        # So, subtract these columns to get the y.
        y = inst_mag.astype(np.float) - std_mag.astype(np.float)
    
        # Calculate a linear regression.
        slope, intercept, r_value, p_value, std_err = \
            stats.linregress(airmass.astype(np.float), y)
    
        logging.debug("Linear regression for day: " + str(a[0][DAY_CE_CALC_DATA]) +
                      " slope: " + str(slope) + " intercept: " + str(intercept) + \
                      " r-value: " + str(r_value) + " p-value: " + str(p_value) + \
                      " std_err: " + str(std_err))
     
        return slope, intercept
    
    def valid_data_to_calc_ext_cof(self, obj_data_for_ext_coef):
        """Examines the data from a star to ensure is valid to calculate a
        extinction coefficient from it.
        
        I.e., air mass and instrumental magnitude are proportional, greater 
        air mass is also a greater magnitude, otherwise these data is not 
        considered valid. 
        
        Args:
        obj_data_for_ext_coef: Data of magnitude and air mass for a star.
        
        Returns:        
        True if valid, False otherwise.
        
        """
        
        # To know if air mass and magnitude are proportional a linear regression is
        # calculated and the slope inspected. 
        slope, intercept = calculate_extinction_coefficient(obj_data_for_ext_coef)
        
        return slope > 0.0                        

    def collect_data_to_calc_ext_coef(self):
        """Collect the data necessary to calculate extinction coefficients,
        this is, the magnitudes for the standard stars.
        
        """
        
        # To store all the data necessary to calculate extinction coefficients.
        calc_data_for_ext_coef = []
        
        # Process each standard object.
        for i in std_obj_idxs:
            
            # Retrieve the object data and the instrumental magnitudes measured.
            star = self._stars[i]
            star_inst_mags = inst_mag[i]
            
            # Data of current star necessary to calculate extinction
            # coefficients.
            mag_of_star = collect_mag_for_star(star, star_inst_mags)
            
            # The magnitudes collected for this object are evaluated to check 
            # its validity.
            for d in self._days:
                data_subset = [m for m in mag_of_star if 
                    m[DAY_CE_CALC_DATA] == d]
                # Check if there is data of this object for this day.
                if len(data_subset) >= MIN_NUM_STD_MEASURES:
                    # Check of the magnitudes are coherent with the extinction.
                    if self.valid_data_to_calc_ext_cof(data_subset) == True:
                        calc_data_for_ext_coef.extend(data_subset)
                    else:
                        logging.warning("Data to calculate extinction " + \
                                        "coefficient discarded from object " + \
                                        star[OBJ_NAME_COL] + " for day " + str(d))
        
        return calc_data_for_ext_coef

    def calculate_extinction_coefficients(self, stars):
        """Get the extinction coefficient using the standard objects.
        
        Args:
        stars: The list of all the stars.
        
        Returns:        
        The extinction coefficient calculated, the days of each calculation and 
        the filters. 
        """
        
        data_for_ext_coef = self.collect_data_to_calc_ext_coef()
    
        # If there is any data to calculate extinction coefficient.
        if len(data_for_ext_coef) > 0:
            
            for d in self._days:
                logging.debug("Calculating extinction coefficient for day " + \
                              str(d) + " with " + \
                              str(len(data_for_ext_coef)) + " magnitudes.")
                
                for f in self._filters:
                    mag = [m for m in data_for_ext_coef \
                           if m[DAY_CE_CALC_DATA] == d and \
                           m[FILTER_CE_CALC_DATA] == f]
                    
                    # Check if there is data of this object for this day.
                    if len(mag) > 0:
                        slope, intercept = self.calc_one_ext_coeff(mag)
                
                        self._ec.append([d, f, slope, intercept])
                    
                    else:
                        logging.debug("There is no data to calculate " + \
                                      "extinction coefficient on day " + \
                                      str(d) + " for filter " + f)
        else:
            logging.warning("There is not enough data to calculate extinction " + \
                            "coefficients")
    
    def collect_mag_for_star(self, star, star_inst_mags):
        """Collect magnitudes for the standard object received.
        
        Args:
        star: Star whose magnitudes are received.
        star_inst_mags: The magnitude values.
        
        Returns:        
        The extinction coefficient calculated, the days of each calculation and 
        the filters. 
        """
            
        obj_data_for_ext_coef = []
        
        # Find magnitudes for this object.
        for inst_mag in star_inst_mags:
            
            # For each object the magnitudes are grouped in different lists.
            for im in inst_mag:
                
                std_mag = star.get_std_mag(im[FILTER_COL])
                
                # Check that a standard magnitude has been found for
                # this object and filter.
                if std_mag is not None:
                    
                    # Also check that there is a valid
                    # instrumental magnitude value.
                    # It is a different 'if' to log a proper message.
                    if im[INST_MAG_COL] != INDEF_VALUE:
                        
                        # Add the day and the filter of this magnitude.
                        self._days.add(get_day_of_measurement(im[JD_TIME_COL]))
                        self._filters.add(im[FILTER_COL])
                        
                        obj_data_for_ext_coef.append([day, \
                                                      im[JD_TIME_COL], \
                                                      im[INST_MAG_COL], \
                                                      std_mag, \
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
    
    def get_star_ext_corr_mag(self, star_index):
        """Get the magnitude corrected for extinction for the object received.
         
        The extinction coefficients are applied and the magnitudes 
        calculated are saved to a file and returned.
        
        Args:
        star_index: Index of the star whose magnitudes are corrected. 
        
        Returns:        
        The magnitudes corrected.   
            
        """
        
        magnitudes = []
        
         
    
    def get_corrected_magnitudes(self):
        """Apply the extinction coefficients calculated to the stars to 
        calculate its corrected magnitudes.
        
        Returns:
        The magnitudes that could be corrected for extinction using the 
        coefficients previously calculated.        
        
        """   
        
        # To store the corrected magnitudes.
        ec_mags = []
        
        # Process the instrumental magnitudes measured for each star.
        for inst_mag in self._inst_mag[star_index]:
            
            # For each star the magnitudes are grouped in a list.
            for im in inst_mag:
                
                # Check if the instrumental magnitude is defined.
                if im[INST_MAG_COL] != INDEF_VALUE :
                
                    # Find the coefficients by day and filter.
                    day = get_day_of_measurement(im[JD_TIME_COL])
                    filter = im[FILTER_COL]
                    
                    try:
                        slope, intercept = self.extinction_coefficient(day, 
                                                                       filter)

                        # Calculate the extinction corrected magnitude.
                        # Mo = Minst - intercept - slope * airmass
                        ext_corr_mag = (float(im[INST_MAG_COL]) - 
                                        intercept - 
                                        slope * float(im[AIRMASS_COL]))
                            
                        ec_mags.append(CorrectedMagnitude(im[JD_TIME_COL], 
                                                          day, 
                                                          filter, 
                                                          ext_corr_mag,
                                                          im[INST_MAG_COL], 
                                                          im[ERR_COL]))
                        
                    except ExtinctionCoefficientNotFound as e:
                        logging.debug(e)
                        
                else:
                    logging.debug('Found an instrumental magnitude ' +
                                  ' undefined for star {name}'.format(
                                    name={self._stars[i].name}))

        return ec_mags        
            
def get_day_of_measurement(time_jd):
    """Returns the julian day related to the Julian time received.
    
    The day is assigned to that which the night begins.
    So a JD between .0 (0:00:00) and .4 (+8:00:00) belongs to the day before.
    
    Args:
    time_jd: A Julian time value.
    
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