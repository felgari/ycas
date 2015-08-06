#!/usr/bin/env python
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

""" This module calculates the magnitudes applying the atmospheric extinction
correction when possible, this is, when there are enough standard stars.
"""

import logging
import locale
import numpy as np
from scipy import stats
from astropy.time.core import MJD_ZERO
from matplotlib.testing.jpl_units import day
import starsset
from constants import *
from textfiles import *
from utility import get_day_from_mjd

class ExtinctionCoefficient(object):
    """The extinction coefficient values calculated for a day and a filter."""
    
    # Minimum number of measures of standard objects to calculate extinction 
    # coefficients.
    MIN_NUM_STD_MEASURES = 4    
    
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
    
class ExtinctionCoefficientNotCalculated(Exception):
    """To raise when a extinction coefficient could not be calculated."""
    
    def __init__(self, star_name, filter):
        self._star_name = star_name
        self._filter = filter
        
    def __str__(self):
        return "No extinction coefficient calculated for star %s and filter %s"\
                % (self._star_name, self._filter)      
    
class ExtinctionCoefficientNotFound(Exception):
    """To raise when a extinction coefficient does not exist for a day 
    and filter.    
    """
    
    def __init__(self, day, filter):
        self._day = day
        self._filter = filter
        
    def __str__(self):
        return "No extinction coefficient for day %d and filter %s" % \
                (self._day, self._filter)                
        
class ExtCorrMagnitudes(object):
    """Calculates the extinction coefficients from a set of measures and
    applies them to a set of magnitudes.    
    """ 
    
    def __init__(self, inst_mag):
        self._inst_mag = inst_mag
        
        self._star_names = []     
        
        self._ec = []     

        for s in inst_mag.stars:            
            self._star_names.append(s.name)       
        
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
    
    def calc_one_ext_coeff(self, ins_mag_for_std):
        """Calculates the extinction coefficient using the data received.
        
        Args:
            ins_mag_for_std: Instrumental magnitudes of standard stars used
            to calculate the linear regression for the extinction coefficient.
        
        Returns:        
            The extinction coefficient calculated.
        
        """
        
        star_name = None
        filter = None
        
        # Get the standard standard magnitudes for this instrumental ones.
        for m in ins_mag_for_std:
            
            # These values are the same for all the iterations.
            star_name = m.star_name
            filter = m.filter
                                
            try:
                m.std_mag = self._inst_mag.get_std_mag(star_name, filter)
            except starsset.NoStdStarException as nsse:
                logging.error(nsse)
            except starsset.NoFilterFoundForStdStarException as nffse:         
                logging.error(nffse)
    
        # Create a numpy array with the data received.
        a = np.array([[locale.atof(m.mjd), \
                       locale.atof(m.mag), \
                       locale.atof(m.airmass), \
                       m.std_mag] \
                      for m in ins_mag_for_std \
                      if m.mag != INDEF_VALUE])
        
        # Sort the data by MJD time.
        na = a[a[:,0].argsort()]        
        
        # Extract the columns necessary to calculate the linear regression.
        inst_mag = na[:,1]
        airmass = na[:,2]        
        std_mag = na[:,3]
        
        # The calculation is:
        # Minst = m + K * airmass
        # Where K is the regression coefficient    
        
        # So, subtract these columns to get the y.
        y = inst_mag.astype(np.float) - std_mag.astype(np.float)
    
        # Calculate a linear regression.
        slope, intercept, r_value, p_value, std_err = \
            stats.linregress(airmass.astype(np.float), y)
            
        # Check if the calculation returns invalid values.
        if np.isnan(slope) or np.isnan(intercept) or \
            np.isnan(r_value) or np.isnan(p_value): 
               
            raise ExtinctionCoefficientNotCalculated(star_name, filter)
        else:                    
            logging.info("Linear regression for day: %.10g star: %s with filter: %s slope: %.10g intercept %.10g r-value: %.10g p-value: %.10g std_err: %.10g air mass min: %.10g air mass max: %.10g using %d values" %
                         (a[0][0], star_name, filter, 
                          slope, intercept, r_value, p_value, std_err, 
                          np.min(na[:,2]), np.max(na[:,2]), na.size))       
            
        return slope, intercept
    
    def collect_mag_to_calc_ext_coef(self):
        """Collect the data necessary to calculate extinction coefficients,
        this is, the magnitudes for the standard stars.
        
        """
        
        # To store all the data necessary to calculate extinction coefficients.
        magnitudes_collected = []
        
        # Process each standard star.
        for star in self._inst_mag.std_stars:  
                        
            # Retrieve the instrumental magnitudes of current star.
            mag_of_star = self._inst_mag.get_mags_of_star(star.name)
                
            # Add the magnitudes to the set.
            magnitudes_collected.extend(mag_of_star)
        
        return magnitudes_collected

    def calculate_extinction_coefficients(self):
        """Get the extinction coefficient using the standard objects.
        
        Args:
            stars: The list of all the stars.
        
        Returns:        
            The extinction coefficient calculated, the days of each 
            calculation and the filters. 
        """
        
        mag_to_calc_ext_coef = self.collect_mag_to_calc_ext_coef()
    
        # If there is any data to calculate extinction coefficient.
        if len(mag_to_calc_ext_coef) > 0:
            
            for d in self._inst_mag.days:
                logging.debug("Calculating extinction coefficient for day %d with %d magnitudes."
                              % (d, len(mag_to_calc_ext_coef)))
                
                for f in self._inst_mag.filters:
                    mag = [m for m in mag_to_calc_ext_coef \
                           if m.day == d and  m.filter == f]
                    
                    # Check there is enough data for calculation.
                    if len(mag) > ExtinctionCoefficient.MIN_NUM_STD_MEASURES:
                        try:
                            slope, intercept = self.calc_one_ext_coeff(mag)
                            
                            # Check that relation between magnitude and air 
                            # mass is direct, otherwise the calculation has 
                            # not any sense.
                            if slope > 0.0:   
                                new_ec = ExtinctionCoefficient(d, f, slope, \
                                                               intercept)             
                                self._ec.append(new_ec)
                            else:
                                logging.warning("Data to calculate extinction coefficient discarded for day %d."
                                                % (d))

                        except ExtinctionCoefficientNotCalculated as ecnc:
                            logging.error(ecnc)         
                            print ecnc         
                    else:
                        logging.warning("There is not enough  data to calculate extinction coefficient on day %s for filter "
                                        % (f))
        else:
            logging.warning("There is not enough data to " +
                            "calculate extinction coefficients")      
    
    def correct_magnitudes(self):
        """Apply the extinction coefficients calculated to the stars to 
        calculate its corrected magnitudes.      
        
        Returns:
            The magnitudes that could be corrected for extinction using the 
            coefficients previously calculated.        
        
        """   
        
        # Process the instrumental magnitudes measured for each star.
        for star in self._inst_mag.stars:
            
            # Walk instrumental magnitudes of current star.
            for im in self._inst_mag.get_mags_of_star(star.name):
                
                star_index = self._star_names.index(star.name)
                
                # Check if the instrumental magnitude is defined.
                if im.mag != INDEF_VALUE :
                
                    # Find the coefficients by day and filter.
                    day = get_day_from_mjd(im.mjd)
                    filter = im.filter
                    
                    try:
                        slope, intercept = \
                            self.extinction_coefficient(day, filter)

                        # Calculate the extinction corrected magnitude.
                        # Mo = Minst - intercept - slope * airmass
                        ext_corr_mag = (float(im.mag) - 
                                        intercept - 
                                        slope * float(im.airmass))
                        
                        im.ext_cor_mag = ext_corr_mag
                        
                    except ExtinctionCoefficientNotFound as e:
                        logging.debug(e)
                        
                else:
                    logging.debug("Found an instrumental magnitude undefined for star %s"
                                  % (star.name))       