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

"""Generate plots with different types of light curves that could be done from
the magnitudes calculated.

"""

import sys
import os
import csv
import logging
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
import magnitude
from constants import *

TSV_FILE_DELIM = '\t'

MAG_MARGIN_MULT = 0.5
MJD_MARGIN_MULT = 0.05

def read_all_mag(star_name, file_name):
    """Read the contents of a file with all the magnitudes related to a star
    and the rest of star of its field.
    
    Args:
        star_name: Name of the star.
        file_name: Name of the file to read.
    
    Returns:  
        The data read in the files.  
        
    """
    
    all_mags = []
    
    try:            
        with open(file_name, 'rb') as fr:
            reader = csv.reader(fr, delimiter=TSV_FILE_DELIM)
            
            # Process all the instrumental magnitudes in the file.
            for row in reader: 
                all_mags.append(row)                                                          
                                
    except IOError as ioe:
        logging.error("Reading magnitudes file: '%s'" % (file_name))  

    return all_mags  


def compose_data_to_plot(all_mags):
    """From the data received compose a data structure in a format easy to plot.
    
    Args:
        all_mags: All the composed_values of magnitudes for a star and its 
        field's stars.
        
    Returns:
        Values composed and the filters found in the data.
    """
    
    composed_values = []
    
    filters = set()
    
    # Compose the values to plot.
    for m in all_mags:
        
        mjd = float(m[0])
        
        filter = m[1]
        filters.add(filter)
        
        if m[2] != INDEF_VALUE and m[3] != INDEF_VALUE:
            
            # Magnitude and error for the star.
            mag = float(m[2])
            err = float(m[3])
            
            # Sum of the magnitudes and errors for the rest of stars in the 
            # field.
            sum_other_mag = 0.0
            err_other_mag = 0.0
            
            # sum the values for the rest of magnitudes and their errors.
            count = 0
            for i in range(4, len(m), 2):                
                if m[i] != INDEF_VALUE and m[i + 1] != INDEF_VALUE:
                    sum_other_mag += float(m[i])
                    err_other_mag += float(m[i + 1])
                    count += 1
            
            # If there isn't any value for other star in the field the 
            # difference is not calculated for this value.
            if count > 0:
                # Get a mean value for the sum of the rest of magnitudes and 
                # errors.
                sum_other_mag /= count
                err_other_mag /= count
                composed_values.append([filter, mjd, mag - sum_other_mag, 
                                        err + err_other_mag])
                
    return composed_values, filters

def plot_star_diff_curve(star_name, values, filters):
    """Plot a curve of differential magnitudes. 
    
    Args:
        star_name: Name of the star.
        values: Values to plot.
        filters: Filters of the values.
    """
    
    # Plot by filter.
    for f in filters:      
        values_filter = [v[1:] for v in values if v[0] == f]
        
        # Sort by MDJ.
        values_ord = sorted(values_filter, key=lambda a_entry: a_entry[0])

        # Create a matrix to get the values by columns.        
        mat = np.matrix(values_ord)
        
        mjd = list(np.array(mat[:,0]).reshape(-1,))
        mag = list(np.array(mat[:,1]).reshape(-1,))
        err = list(np.array(mat[:,2]).reshape(-1,))             
        
        # Plot.
        plt.figure()
        plt.errorbar(mjd, mag, yerr=err, c='k',
                     fmt='.', ecolor='k', capthick=2, ls='-')

        # MJD axis.
        mjd_min_val = np.min(mjd)
        mjd_max_val = np.max(mjd)        
        mjd_dif_val = mjd_max_val - mjd_min_val       
        
        mjd_margin = MJD_MARGIN_MULT * mjd_dif_val
        
        # Magnitude axis.
        mag_min_val = np.min(mag)
        mag_max_val = np.max(mag)        
        mag_dif_val = mag_max_val - mag_min_val     
        
        mag_margin = MAG_MARGIN_MULT * mag_dif_val
        
        # The y axis is inverted to, greater magnitude is less brighter.
        plt.axis([mjd_min_val - mjd_margin,
                  mjd_max_val + mjd_margin,
                  mag_max_val + mag_margin, 
                  mag_min_val - mag_margin])
        
        plt.title("%s - %s filter" % (star_name, f))
        plt.xlabel("MJD")
        plt.ylabel("%s mag. - mean(ref. stars mag.)" % star_name)         
        
        plt.show()     
        
def plot_diff_magnitude(stars, target_dir):
    """Read the magnitudes of the stars from files and plot a differential 
    light curve.
    
    Args:
        stars: List of stars.
        target_dir: Directory of the files to read and where to write the plots.
        
    """
    
    # Get the list of file with magnitudes ignoring hidden files.
    mag_files_full_path = \
                    [f for f in glob.glob(os.path.join(target_dir, "*%s.%s" %
                                                       (ALL_INST_MAG_SUFFIX,
                                                        TSV_FILE_EXT))) \
                    if not os.path.basename(f).startswith('.')]
                    
    # For each file with magnitudes plot the difference.
    for f in mag_files_full_path:
        
        file_name = os.path.basename(f)
        star_name = file_name[:file_name.find(ALL_INST_MAG_SUFFIX)]
        
        # Check that the star of this file is in the list of stars.
        if stars.has_star(star_name):
            all_mags = read_all_mag(star_name, f)
            
            values, filters = compose_data_to_plot(all_mags)
            
            if len(values) > 1:
                plot_star_diff_curve(star_name, values, filters)

def generate_curves(stars, target_dir):
    """Generate curves from the magnitudes files of the stars received.
    
    Args:
        stars: List of stars.
        target_dir: Directory of the files to read and where to write the plots.
        
    """    
        
    plot_diff_magnitude(stars, target_dir)
