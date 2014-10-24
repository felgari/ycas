#!/usr/bin/python
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

"""
This module performs the reduction of images. Walk the directories looking for
bias, flat and data images.
For bias images calculates the average bias.
For flats images, subtract the bias and calculates the average flat for each filter.
Finally, to each data image subtract bias and divide by the flat corresponding to
its filter.
"""

import sys
import os
import glob
from pyraf import iraf
from constants import *

def show_files_statistics(list_of_files):
    """ Show the statistics for the files received.
    
    This function applies imstat to the files received and
    print the results.
    
    """
    
    # Getting statistics for bias files.
    try:
    	means = iraf.imstat(list_of_files, fields='mean', Stdout=1)
    	means = means[1:]
    	mean_strings = [str(m).translate(None, ",\ ") for m in means]
    	mean_values = [float(m) for m in mean_strings]
    	
    	print "Bias images - Max. mean: " + str(max(mean_values)) + \
    			" Min. mean: " + str(min(mean_values))
    			
    	print "Creating bias file: " + masterbias_name	
    except iraf.IrafError as exc:
    	print "Error executing imstat: Stats for bias images: " + list_of_files
    	print "Iraf error is: " + str(exc)   		

def do_masterbias():
    """ Calculation of all the masterbias files.
    
    This function search for bias files from current directory.
    The bias images are located in specific directories that only
    contains bias images and have a specific denomination, so searching
    for bias files is searching these directories.
    Once a directory for bias had been found a masterbias is calculated
    with an average operation using all the bias files.
    
    """

    print "Doing masterbias ..."
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
    	
        # Check if current directory is for bias fits.
        for dr in dirs:
            if dr == BIAS_DIRECTORY:
    				
                # Get the full path of the directory.                
                full_dir = os.path.join(path, dr)
                print "Found a directory for 'bias': " + full_dir
                
                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*." + FIT_FILE_EXT))
                print "Found " + str(len(files)) + " bias files"
                
                # Build the masterbias file name.
                masterbias_name = os.path.join(full_dir, MASTERBIAS_FILENAME) 
                
                # Check if masterbias already exists.
                if os.path.exists(masterbias_name) == True:
                    print "Masterbias file exists, " + masterbias_name + \
                        " so resume to next directory."
                else:
                    # Put the files list in a string.
                    list_of_files = str(files).translate(None, "[]\'")
                    
                    show_bias_statistics(list_of_files)
                        	
                    # Combine all the bias files.
                    try:
                        iraf.imcombine(list_of_files, masterbias_name, Stdout=1)
                    except iraf.IrafError as exc:
                        print "Error executing imcombine: Combining bias with: " + list_of_files  
                        print "Iraf error is: " + str(exc)      
                        
def normalize_flats(files):
    """ Normalize a set of flat files. 
    
    This function receives a list of flat files and returns a list of
    files of the flat files after normalize them.
    The normalization is performed dividing the flat image by the mean
    value of the flat image. This mean is the result of applying imstat
    to each image.
    
    """
    
    # The output list of normalized files is created.
    list_of_norm_flat_files = []
    	
    for fl in files:
        # Get the 'work' and 'normalized' names for the flat files to process.
        work_file = fl.replace("." + FIT_FILE_EXT, \
                               WORK_FILE_SUFFIX + "." + FIT_FILE_EXT)
        
        norm_file = fl.replace("." + FIT_FILE_EXT, \
                               NORM_FILE_SUFFIX + "." + FIT_FILE_EXT)
        
        # Getting statistics for flat file.
        try:
            flat_stats = iraf.imstat(work_file, fields='mean', Stdout=1)
            flat_stats = flat_stats[1]    
            mean_value = float(flat_stats)
            
            try:
                # Normalize flat dividing flat by its mean value.
                iraf.imarith(work_file, '/', mean_value, norm_file)
                
                # If success, add the file to the list of normalized flats.
                list_of_norm_flat_files.extend([norm_file])
    			
            except iraf.IrafError as exc:
                print "Error executing imarith: normalizing flat image: " + fl
                print "Iraf error is: " + str(exc)
    	
        except iraf.IrafError as exc:
            print "Error executing imstat: getting stats for flat image: " + fl
            print "Iraf error is: " + str(exc)       
    
    return list_of_norm_flat_files

def do_masterflat():
    """ Calculation of all the masterflat files.
    
    This function search for flat files from current directory.
    The flat images are located in specific directories that only
    contains flat images and have a specific denomination, so searching
    for flat files is searching these directories.
    Usually data images are taken using differente filters, so flat images
    are taken using the same filters, and into each flat directory the flat
    images are divides in different directories, one for each filter.
    Once a directory for flat had been found, a bias subtraction is performed
    with each flat image. Finally a masterflat is calculated for each flat 
    directory with an average operation using all the bias files.
    
    """
    
    print "Doing masterflat ..."

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == FLAT_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for 'flat': " + full_dir

                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*." + FIT_FILE_EXT))
                print "Found " + str(len(files)) + " flat files"
                
                # Buid the masterflat file name.
                masterflat_name = os.path.join(full_dir, MASTERFLAT_FILENAME) 
                
                # Check if masterflat already exists.
                if os.path.exists(masterflat_name) == True:
                    print "Masterflat file exists, " + masterflat_name + \
                        " so resume to next directory."
                else:
                    # Put the files list in a string.
                    list_of_flat_files = str(files).translate(None, "[]\'")

                    # Create list of names of the work flat files.
                    work_files = \
                        [s.replace("." + FIT_FILE_EXT, WORK_FILE_SUFFIX + "." + FIT_FILE_EXT) for s in files ]

                    list_of_work_flat_files = str(work_files).translate(None, "[]\'")

                    masterbias_name = os.path.join(full_dir, PATH_FROM_FLAT_TO_BIAS, MASTERBIAS_FILENAME)

                    try:
                        # Create the work files subtracting bias from flat.
                        iraf.imarith(list_of_flat_files, '-', masterbias_name, list_of_work_flat_files)
                        
                        print "Normalizing flat files for: " + masterflat_name    
                        
                        norm_flat_files = normalize_flats(files)

                        print "Creating flat files for: " + masterflat_name  
                        
                        # Create list of names of the normalized flat files.
                        list_of_norm_flat_files = str(norm_flat_files).translate(None, "[]\'")                    
                            
                        try:
                            # Combine all the flat files.
                            iraf.imcombine(list_of_norm_flat_files, masterflat_name, Stdout=1)
                        except iraf.IrafError as exc:
                            print "Error executing imcombine. Combining flats with: " + list_of_work_flat_files    
                            print "Iraf error is: " + str(exc)                    
                        
                    except iraf.IrafError as exc:
                        print "Error executing imarith. Subtracting masterbias to: " + list_of_flat_files
                        print "Iraf error is: " + str(exc)
                        
def reduce_data():
    """ Reduction of all data images.
    
    This function search data images to reduce then. The data images are 
    located in specific directories that only contains data images.
    Once a data images directory has been found, the directory that contains
    the bias and flats images that are related to that data images are located
    These directories of bias and flats are located in specific locations after
    the directory of data images.
    For each data image a bias subtraction and a subsequent division by the 
    flat is performed.
    The resulting image is saved in the same directory but with a different
    name to keep the original file.
    
    """
    
    print "Reducing data ..."

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of files.
                data_files = glob.glob(os.path.join(full_dir, "*." + FIT_FILE_EXT))
                print "Found " + str(len(data_files)) + " data files"
                
                # The masterbias file name.
                masterbias_name = \
                    os.path.join(full_dir, PATH_FROM_DATA_TO_BIAS, \
                                 MASTERBIAS_FILENAME)      
                
                # The masterflat file name.
                masterflat_name = \
                    os.path.join(full_dir, PATH_FROM_DATA_TO_FLAT, \
                                 split_path[-1], MASTERFLAT_FILENAME)

                # Reduce each data file one by one.
                for dfile in data_files:                 

                    # Get the work file between bias and flatted result.
                    work_file = dfile.replace("." + FIT_FILE_EXT, \
                                              WORK_FILE_SUFFIX + "." + FIT_FILE_EXT)
                       
                    try: 
                        # Create the work files subtracting bias from flat.
                        iraf.imarith(dfile, '-', masterbias_name, work_file)     
                        
                        # Get the name of the final file.
                        final_file = dfile.replace("." + FIT_FILE_EXT, \
                                                   DATA_FINAL_SUFFIX + "." + \
                                                   FIT_FILE_EXT)   

                        try:
                            # Create the final data dividing by master flat.
                            iraf.imarith(work_file, "/", masterflat_name, final_file)
                            
                            # Remove work file to save storage space.
                            os.remove(work_file)
                                                                
                        except iraf.IrafError as exc:
                            print "Error executing imarith: " + work_file + \
                                    " / " + masterflat_name + " to " + final_file      
                            print "Iraf error is: " + str(exc)                  
                        
                    except iraf.IrafError as exc:
                        print "Error executing imarith: " + dfile + \
                            " - " + masterbias_name + " to " + work_file
                        print "Iraf error is: " + str(exc)
                        
def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv

    # Load the images package and does not show any output of the tasks.
    iraf.images(_doprint=0)

    # Process bias files to obtain the average bias.
    do_masterbias()

    # Process flat files to subtract bias from then and calculate the average flat.
    do_masterflat()

    # Reduce data images applying bias and flats.
    reduce_data()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())
