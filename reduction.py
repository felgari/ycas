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

"""This module performs the reduction of astronomical images. 

It walks the directories looking for bias, flat and data images.

For bias images calculates the average bias.

For flats images, subtract the bias, normalize the result and calculates the 
average flat for each filter.

Finally for each data image subtract bias and divide it by the flat 
corresponding to its filter.

"""

import sys
import os
import logging
import glob
import shutil
from pyraf import iraf
from constants import *

# File patterns.
WORK_FILE_SUFFIX = "_work.fit"
NORM_FILE_SUFFIX = "_norm.fit"
WILDCARD_FIT_FILE = "*.fit"

# Imstat operations.
IMSTAT_MEAN = "mean"

# Imarith operations.
IMARITH_SUBTRACT = "-"
IMARITH_DIVIDE = "/"

# Directory paths.
PATH_FROM_FLAT_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_FLAT = os.path.join("..", "..", FLAT_DIRECTORY)

def is_data_directory(current_dir, data_dir_name):
    """Determines if the directory has a name identified as containing images
    with data.
    
    Args:
        current_dir: The directory to analyze. It must have the full path.    
        data_dir_name: Name used for data directories.
        
    Returns:
        True if the directory is for data, False otherwise.
        
    """
    
    split_path = current_dir.split(os.sep)
    
    return split_path[-2] == data_dir_name

def get_masterbias_file_name(data_path):
    """Get the masterbias file name related to the data_path containing the 
    data images.
    
    Args:
        data_path: Path of the directory with the data images.
    
    """
    
    # Get the masterbias file name using the data_path where it should
    # exists after organizing the files.
    masterbias_name = os.path.join(data_path, PATH_FROM_DATA_TO_BIAS, 
                                   MASTERBIAS_FILENAME)
    
    # Check if bias really exists.
    if not os.path.exists(masterbias_name):
        logging.warning("Masterbias '%s' does not exists" % (masterbias_name))
        
        masterbias_name = ""
        
    return masterbias_name

def get_masterflat_file_name(data_path):
    """Get the masterflat file name related to the data_path containing the 
    data images.
    
    Args:
        data_path: Path of the directory with the data images.
    
    """    
    
    split_path = data_path.split(os.sep)
    
    # Get the masterflat file name using the data_path where it should
    # exists after organizing the files.
    masterflat_name = os.path.join(data_path, PATH_FROM_DATA_TO_FLAT,
                                   split_path[-1], MASTERFLAT_FILENAME)
    
    # Check if bias really exists.
    if not os.path.exists(masterflat_name):
        logging.warning("Masterflat '%s' does not exists" % (masterflat_name))
        
        masterflat_name = ""
        
    return masterflat_name

def show_bias_files_statistics(list_of_files):
    """ Show the statistics for the bias files received.
    
    This function applies imstat to the files received and print the results.
    
    Args: 
        list_of_files: List of files to get their statistics.   
    
    """
    
    # Control pyraf exception.
    try:
        # Get statistics for the list of bias files using imstat.
    	means = iraf.imstat(list_of_files, fields='mean', Stdout=1)
    	means = means[IMSTAT_FIRST_VALUE:]
    	mean_strings = [str(m).translate(None, ",\ ") for m in means]
    	mean_values = [float(m) for m in mean_strings]
    	
        # Print the stats results.
    	logging.debug("Bias images stats: Max. mean: %d Min. mean: %d" %
                      (max(mean_values), min(mean_values)))	
        
    except iraf.IrafError as exc:
    	logging.error("Error executing imstat: Stats for bias images: %s" %
                      (list_of_files))
    	logging.error("Iraf error is: %s" % (exc))  
        
    except ValueError as ve: 	
        logging.error("Error calculating mean values: %s" % (mean_strings))
        logging.error("Error is: %s" % (ve))          	

def generate_all_masterbias(bias_dir_name):
    """ Calculation of all the masterbias files.
    
    This function search for bias files from current directory.
    The bias images are located in specific directories that only
    contains bias images and have a specific denomination, so searching
    for bias files is searching these directories.
    Once a directory for bias had been found a masterbias is calculated
    with an average operation using all the bias files.
    
    Args:
        bias_dir_name: Name of the directories that contain bias images.     
    
    """

    logging.info("Generating all masterbias files ...")
    
    # Walk from current directory.
    for path, dirs, files in os.walk('.'):
    	
        # Check if current directory is for bias fits.
        for dr in dirs:
            if dr == bias_dir_name:
    				
                # Get the full path of the directory.                
                full_dir = os.path.join(path, dr)
                logging.debug("Found a directory for 'bias': %s" % (full_dir))
                
                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, WILDCARD_FIT_FILE))
                logging.debug("Found %d bias files" % (len(files)))
                
                # Build the masterbias file name.
                masterbias_name = os.path.join(full_dir, MASTERBIAS_FILENAME) 
                
                # Check if masterbias already exists.
                if os.path.exists(masterbias_name) == True:
                    logging.debug("Masterbias file exists '%s', so resume to next directory." % 
                                  (masterbias_name))
                else:
                    # Put the files list in a string.
                    list_of_files = str(files).translate(None, "[]\'")
                    
                    #show_bias_files_statistics(list_of_files)
                        	
                    # Combine all the bias files.
                    try:
                        logging.debug("Creating bias file: %s" %
                                      (MASTERBIAS_FILENAME))
                        iraf.imcombine(list_of_files, masterbias_name, Stdout=1)
                        
                    except iraf.IrafError as exc:
                        logging.error("Error executing imcombine combining " + \
                                      "bias with: %s" %
                                      (list_of_files))  
                        logging.error("Iraf error is: %s" % (exc))    
                        
def normalize_flats(files):
    """ Normalize a set of flat files. 
    
    This function receives a list of flat files and returns a list of
    files of the flat files after normalize them.
    The normalization is performed dividing the flat image by the mean
    value of the flat image. This mean is the result of applying imstat
    to each image.
    
    Args: 
        files: The names of the files corresponding to the flat images.
    
    Returns:    
        The list of file names related to the normalized images.
    
    """
    
    # The output list of normalized files is created.
    list_of_norm_flat_files = []
    	
    for fl in files:
        # Get the 'work' and 'normalized' names for the flat files to process.
        work_file = fl.replace("." + FIT_FILE_EXT, WORK_FILE_SUFFIX)
        
        norm_file = fl.replace("." + FIT_FILE_EXT, NORM_FILE_SUFFIX)
        
        # Getting statistics for flat file.
        try:
            flat_stats = iraf.imstat(work_file, fields=IMSTAT_MEAN, Stdout=1)
            flat_stats = flat_stats[IMSTAT_FIRST_VALUE]    
            
            try:
                mean_value = float(flat_stats)
                                
                # Normalize flat dividing flat by its mean value.
                iraf.imarith(work_file, '/', mean_value, norm_file)
                
                # If success, add the file to the list of normalized flats.
                list_of_norm_flat_files.extend([norm_file])
    			
            except iraf.IrafError as exc:
                logging.error("Error executing imarith: normalizing flat image: %s" %
                              (fl))
                logging.error("Iraf error is: %s" % (exc))
                
            except ValueError as ve:     
                logging.error("Error calculating mean value for: %s" % 
                              (flat_stats))
                logging.error("Error is: %s" % (ve))                      
    	
        except iraf.IrafError as exc:
            logging.error("Error executing imstat: getting stats for flat image: %s" %
                          (fl))
            logging.error("Iraf error is: %s" % (exc))       
    
    return list_of_norm_flat_files


def generate_masterflat(path, files, masterflat_name):
    """Generates a master flat from the flat files received.
    
    Args:
        path: Full source path of the flat files.
        files: List of flat files.
        masterflat_name: The name of the masterflat file.
        
    """
    
    # Put the files list in a string.
    list_of_flat_files = str(files).translate(None, "[]\'")
    
    # Create list of names of the work flat files.
    work_files = [s.replace("." + FIT_FILE_EXT, WORK_FILE_SUFFIX) for s in files]
    
    # Remove braces and quotes from the string.
    list_of_work_flat_files = str(work_files).translate(None, "[]\'")
    
    # Get the masterflat file name.
    masterbias_name = os.path.join(path, PATH_FROM_FLAT_TO_BIAS,
                                   MASTERBIAS_FILENAME)
    
    try:
        # Check if masterbias exists.
        if os.path.exists(masterbias_name):
            # Create the work files subtracting bias from flat.
            iraf.imarith(list_of_flat_files, IMARITH_SUBTRACT, masterbias_name,
                         list_of_work_flat_files)
        else:
            for i in range(len(files)):
                # Create the work files as a copy of original files.
                shutil.copyfile(files[i], work_files[i])
        
        logging.debug("Normalizing flat files for: %s" % (masterflat_name))
        norm_flat_files = normalize_flats(files)
        
        # After creating the normalized files, remove the work files to save 
        # storage.
        try:
            for wf in work_files:
                os.remove(wf)
                
        except OSError as oe:            
            logging.error("OSError removing work flat is: %s" % (oe))
            
        logging.debug("Creating flat files for: %s" % (masterflat_name))
        
        # Create list of names of the normalized flat files.
        list_of_norm_flat_files = str(norm_flat_files).translate(None, "[]\'")
        
        try:
            iraf.imcombine(list_of_norm_flat_files, masterflat_name, Stdout=1)
            # After calculating the masterflat, remove the normalized files
            # to save storage space.
            for nff in norm_flat_files:
                os.remove(nff) # Combine all the flat files.
        
        except iraf.IrafError as exc:
            logging.error("Error executing imcombine combining flats with: %s" %
                          (list_of_work_flat_files))
            
            logging.error("Iraf error is: %s" % (exc))
            
        except OSError as oe:
            logging.error("OSError removing normalized flat is: %s" % (oe))
            
    except iraf.IrafError as exc:
        logging.error("Error in imarith. Subtracting masterbias %s to %s" %
                      (masterbias_name, list_of_flat_files))
        
        logging.error("Iraf error is: %s" % (exc))

def generate_all_masterflats(flat_dir_name):
    """Calculation of all the masterflat files.
    
    This function search for flat files from current directory.
    Usually data images are taken using different filters, so flat images
    are taken using the same filters, and into each flat directory the flat
    images are divides in different directories, one for each filter.
    Once a directory for flat had been found, a bias subtraction is performed
    with each flat image. Finally a masterflat is calculated for each flat 
    directory with an average operation using all the bias files.    
    
    Args:
        flat_dir_name: Name of the directories containing flat images.      
        
    """
    
    logging.info("Generating all masterflats files ...")

    # Walk from current directory.
    for path, dirs, files in os.walk('.'):

        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == flat_dir_name:
                logging.debug("Found a directory for 'flat': %s" % (path))

                # Get the list of files.
                files = glob.glob(os.path.join(path, WILDCARD_FIT_FILE))
                
                logging.debug("Found %d flat files" % (len(files)))
                
                # Buid the masterflat file name.
                masterflat_name = os.path.join(path, MASTERFLAT_FILENAME) 
                
                # Check if masterflat already exists.
                if os.path.exists(masterflat_name) == True:
                    logging.warning("Masterflat file exists, %s so resume to next directory." %
                                    (masterflat_name))
                else:
                    generate_masterflat(path, files, masterflat_name)                        

def reduce_image(masterbias_name, masterflat_name, source_image, final_image):
    """Reduce an image.
    
    First, if the masterbias exists is subtracted, later the image is
    divided by the flat, if it exists.
    These aritmethic operations on the images are performed with imarith.    
    
    Args:
        masterbias_name: The full name of the masterbias file.
        masterflat_name: The full name of the masterflat file.
        source_image:The name of the source image
        final_image: The name for the image reduced.
    """
    
    # Get the work file name, a temporary file to store the result between bias
    # and flat application.
    work_file = source_image.replace("." + FIT_FILE_EXT, WORK_FILE_SUFFIX)
    
    # Control imarith exception.
    try:
        # If masterbias exists.
        if len(masterbias_name) > 0:
            
            # Create the work files subtracting bias from flat.
            iraf.imarith(source_image, IMARITH_SUBTRACT, masterbias_name, 
                         work_file)
        else:
            
            # Use as work file (the input for flat step) the original file.
            work_file = source_image 
                    
        # Control imarith exception.
        try:
            
            # If masterflat exists.
            if len(masterflat_name) > 0: 
                
                # Create the final data dividing by master flat.
                iraf.imarith(work_file, IMARITH_DIVIDE, masterflat_name, 
                             final_image)
            else:
                # In this case the final file is the file resulting from bias 
                # step. It could be even the original file if the masterbias 
                # does not exist.
                shutil.copyfile(work_file, final_image) 
            
            # If the work file is not the original file, and it is really a 
            # temporary file, remove it to save storage space.
            if len(masterbias_name) > 0: 
                os.remove(work_file)
                
        except iraf.IrafError as exc:
            logging.error("Error in imarith applying flat: %s %s %s for %s" %
                          (work_file, IMARITH_DIVIDE, masterflat_name, 
                           final_image))
            
            logging.error("Iraf error is: %s" % (exc))
            
    except iraf.IrafError as exc:
        logging.error("Error in imarith applying bias: %s %s %s for %s" %
                      (source_image, IMARITH_SUBTRACT, masterbias_name, 
                       work_file))
        
        logging.error("Iraf error is: %s" % (exc))

def reduce_list_of_images(data_files, masterbias_filename, masterflat_filename):
    """Reduce the images contained in the list of files received applying the
    masterbias and masterflat also received.
    
    Args:
        data_files: List of file to reduce.
        masterbias_filename: Full path of the masterbias file.
        masterflat_filename: Full path of the masterflat file.
    
    """
    
    # Walk the list of images to reduce them one by one.
    for source_image in data_files:
                
        final_file_pattern = "%s.%s" % (DATA_FINAL_SUFFIX, FIT_FILE_EXT)
        
        # Check if current file is not a final one.
        if source_image.find(final_file_pattern) < 0:
            
            # Get the name of the final file.
            final_image = source_image.replace(".%s" % (FIT_FILE_EXT), 
                                               final_file_pattern)
            
            # Reduce the image.
            reduce_image(masterbias_filename, masterflat_filename, 
                         source_image, final_image)            
        else:
            # The final image already exists.
            logging.warning("No reduction to get '%s', already exists" %
                            (source_image)) 

def reduce_data_images(data_dir_name):
    """Reduction all data images.
    
    This function search images from the source directory to reduce then. 
    Once a directory with images has been found, the data images that contains
    are processed to reduce them.
    The reduced images are saved in the same directory but with a different
    name to keep the original file. 
    
    Args:
        data_dir_name: Name of the directories containing data images.     
        
    """

    # Walk from current directory.
    for path, dirs, files in os.walk('.'):

        # Inspect only directories without subdirectories. Only these
        # directories should contain files with images.
        if len(dirs) == 0:    
                    
            # Look for directories with data images.
            if is_data_directory(path, data_dir_name):
                
                logging.debug("Found a directory for data: %s" % (path))

                # Get the list of files.
                data_files = glob.glob(os.path.join(path, WILDCARD_FIT_FILE))
                
                logging.debug("Found %d data files" % (len(data_files)))
                
                # Get the names of materbias and masterflat files to use for
                # reduction.
                masterbias_name = get_masterbias_file_name(path)
                    
                masterflat_name = get_masterflat_file_name(path)       

                reduce_list_of_images(data_files, masterbias_name, 
                                      masterflat_name)

                        
def reduce_images(progargs):
    """Top level function to perform the reduction of data images. 
    
    The tasks are performed sequentially: generate all masterbias, 
    generate all masterflats and finally reduce data images.
    
    Args:
        progargs: Program arguments.     
    
    """
    
    logging.info("Starting the reduction of images ...")    

    # Load the images package and does not show any output.
    iraf.images(_doprint=0)

    # Generate all the average bias.
    generate_all_masterbias(progargs.bias_directory)

    # Generate all the average flat.
    generate_all_masterflats(progargs.flat_directory)

    # Reduce all the data images applying the average bias and flats.
    reduce_data_images(progargs.data_directory)
    
    logging.info("Finished the reduction of images.")    
