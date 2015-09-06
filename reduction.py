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
WORK1_FILE_SUFFIX = "_work1.fit"
WORK2_FILE_SUFFIX = "_work2.fit"
NORM_FILE_SUFFIX = "_norm.fit"
WILDCARD_FIT_FILE = "*.fit"

# Imstat operations.
IMSTAT_MEAN = "mean"

# Imarith operations.
IMARITH_SUBTRACT = "-"
IMARITH_DIVIDE = "/"

def is_light_directory(current_dir, light_dir_name):
    """Determines if the directory has a name identified as containing images
    with data.
    
    Args:
        current_dir: The directory to analyze. It must have the full path.    
        light_dir_name: Name used for data directories.
        
    Returns:
        True if the directory is for light images, False otherwise.
        
    """
    
    split_path = current_dir.split(os.sep)
    
    return split_path[-2] == light_dir_name

def get_masterdark_file_name(data_path, dark_dir_name):
    """Get the masterdark file name related to the data_path containing the 
    data images.
    
    Args:
        data_path: Path of the directory with the data images.
        dark_dir_name: Name of the directories containing dark images.
    
    """
    
    # Get the masterbias file name using the data_path where it should
    # exists after organizing the files.
    masterdark_name = os.path.join(data_path, 
                                   os.path.join("..", "..", dark_dir_name), 
                                   MASTERDARK_FILENAME)
    
    # Check if bias really exists.
    if not os.path.exists(masterdark_name):
        logging.warning("Masterdark '%s' does not exists" % (masterdark_name))
        
        masterdark_name = ""
        
    return masterdark_name

def get_masterbias_file_name(data_path, bias_dir_name):
    """Get the masterbias file name related to the data_path containing the 
    data images.
    
    Args:
        data_path: Path of the directory with the data images.
        bias_dir_name: Name of the directories containing bias images.
    
    """
    
    # Get the masterbias file name using the data_path where it should
    # exists after organizing the files.
    masterbias_name = os.path.join(data_path, 
                                   os.path.join("..", "..", bias_dir_name), 
                                   MASTERBIAS_FILENAME)
    
    # Check if bias really exists.
    if not os.path.exists(masterbias_name):
        logging.warning("Masterbias '%s' does not exists" % (masterbias_name))
        
        masterbias_name = ""
        
    return masterbias_name

def get_masterflat_file_name(data_path, flat_dir_name):
    """Get the masterflat file name related to the data_path containing the 
    data images.
    
    Args:
        data_path: Path of the directory with the data images.
        flat_dir_name: Name of the directories containing bias images.
    
    """    
    
    split_path = data_path.split(os.sep)
    
    # Get the masterflat file name using the data_path where it should
    # exists after organizing the files.
    masterflat_name = os.path.join(data_path, 
                                   os.path.join("..", "..", flat_dir_name),
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

def generate_all_masterbias(target_dir, bias_dir_name):
    """ Calculation of all the masterbias files.
    
    This function search for bias files from current directory.
    The bias images are located in specific directories that only
    contains bias images and have a specific denomination, so searching
    for bias files is searching these directories.
    Once a directory for bias had been found a masterbias is calculated
    with an average operation using all the bias files.
    
    Args:
        target_dir: Directory of the files.
        bias_dir_name: Name of the directories that contain bias images.     
    
    """

    logging.info("Generating all masterbias files from %s ..." % target_dir)
    
    # Walk from current directory.
    for path, dirs, files in os.walk(target_dir):
    	
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
                    list_of_files = ",".join(files)
                    
                    #show_bias_files_statistics(list_of_files)
                        	
                    # Combine all the bias files.
                    try:
                        logging.debug("Creating bias file: %s" % 
                                    masterbias_name)
                                    
                        iraf.imcombine(list_of_files, masterbias_name, Stdout=1)
                                                
                    except iraf.IrafError as exc:
                        logging.error("Error executing imcombine combining " + \
                                      "bias with: %s" %
                                      (list_of_files))  
                        logging.error("Iraf error is: %s" % (exc))                        

def generate_masterdark(logging, dark_files, masterdark_name, dark_dir_name):
    """Generates a masterdark from the dark files received.
    
    Args:
        path: Full source path of the flat files.
        dark_files: List of dark files.
        masterdark_name: The name of the masterdark file.
        dark_dir_name: Name of the directories that contain dark images
        
    """
    
    # Check that there is not any work file in the list, it could exists if a
    # previous execution was terminated just before removing a work file.
    work_files_to_remove = \
        [f for f in dark_files if f.find(WORK_FILE_SUFFIX) > 0 ]
    
    # The files to use are those that are not previous work files.    
    files = [f for f in dark_files if f.find(WORK_FILE_SUFFIX) < 0 ]   
    
    # Create list of names of the work flat files.
    work_files = [s.replace("." + FIT_FILE_EXT, WORK_FILE_SUFFIX) for s in files]
    
    # Put the work files list in a string to be used with imarith.
    string_of_work_dark_files = ",".join(work_files)
    
    # Put the dark files list in a string to be used with imarith.
    string_of_dark_files = ",".join(files)  
    
    # Get the masterbias file name.
    masterbias_name = os.path.join(path, 
                                   os.path.join("..", bias_dir_name),
                                   MASTERBIAS_FILENAME)
    
    try:
        # Check if masterbias exists.
        if os.path.exists(masterbias_name):
            
            # Create the work files subtracting bias from dark.
            iraf.imarith(string_of_dark_files, IMARITH_SUBTRACT, masterbias_name,
                         string_of_work_dark_files)
        else:
            for i in range(len(files)):
                # If there is not a masterbias create the work files as a 
                # copy of dark files.
                shutil.copyfile(files[i], work_files[i])
        
        logging.debug("Creating masterdark file: %s" % (masterdark_name))    
        
        # Put the work dark files list in a string to be used with imcombine.
        string_of_work_dark_files = ",".join(work_files)
        
        try:
            iraf.imcombine(string_of_work_dark_files, masterdark_name, Stdout=1)
            
            # After calculating the masterdark, remove the work files
            # to save storage space.
            for wf in work_files:
                os.remove(wf)
                
            # If there was any previous work file in the directory.
            for wf in work_files_to_remove:
                os.remove(wf)
                
        except OSError as oe:            
            logging.error("OSError removing file while creating masterdark: %s" 
                          % (oe))
        
        except iraf.IrafError as exc:
            logging.error("Error executing imcombine combining darks with: %s" %
                          (string_of_work_dark_files))
            
            logging.error("Iraf error is: %s" % (exc))
            
    except iraf.IrafError as exc:
        logging.error("Error in imarith. Subtracting masterbias %s to %s" %
                      (masterbias_name, string_of_dark_files))
        
        logging.error("Iraf error is: %s" % (exc))

def generate_all_masterdark(target_dir, dark_dir_name, bias_dir_name):
    """ Calculation of all the masterdark files.
    
    This function search for bias files from current directory.
    The dark images are located in specific directories that only
    contains bias images and have a specific denomination, so searching
    for dark files is searching these directories.
    Once a directory for dark had been found a masterdark is calculated,
    first subtracting the masterbias if ir exists, and secong generating the
    masterdark with an average operation using all the dark files.
    
    Args:
        target_dir: Directory of the files.
        dark_dir_name: Name of the directories that contain dark images.
        bias_dir_name: Name of the directories that contain bias images.     
    
    """

    logging.info("Generating all masterdark files from %s ..." % target_dir)
    
    # Walk from current directory.
    for path, dirs, files in os.walk(target_dir):
        
        # Check if current directory is for bias fits.
        for dr in dirs:
            if dr == dark_dir_name:
                    
                # Get the full path of the directory.                
                full_dir = os.path.join(path, dr)
                logging.debug("Found a directory for 'dark': %s" % (full_dir))
                
                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, WILDCARD_FIT_FILE))
                logging.debug("Found %d dark files" % (len(files)))
                
                # Build the masterdark file name.
                masterdark_name = os.path.join(full_dir, MASTERDARK_FILENAME) 
                
                # Check if masterdark already exists.
                if os.path.exists(masterdark_name) == True:
                    logging.debug("Masterdark file exists '%s', so resume to next directory." % 
                                  (masterdark_name))
                else:
                    generate_masterdark(path, files, masterdark_name,
                                        bias_dir_name)                        
                        
def normalize_flats(files):
    """ Normalize a set of flat files. 
    
    This function receives a list of flat files and returns a list of
    files of the flat files after normalize them.
    The normalization is performed dividing the flat image by the mean
    value of the flat image. This mean is the result of applying imstat
    to each image.
    
    Args: 
        files: The names of the files corresponding to the flat images.
    
    """
    	
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

def reduce_flats(flat_files, masterbias_name):
    """Reduce the flat files received subtracting the masterbias indicated.
    
    Args:
        flat_files: The flat files to reduce
        
    """
    
    for ff in flat_files: 
        
        work_file = ff.replace(".fit", WORK_FILE_SUFFIX)
    
        try:
            # Create the work file subtracting the masterbias from the flat.
            iraf.imarith(ff, IMARITH_SUBTRACT, masterbias_name, work_file)
                
        except iraf.IrafError as exc:
            logging.error("Error in imarith. Subtracting masterbias to %s" % ff)

def remove_temporary_files(path):
    """Remove the work files in the path indicated.
    
    Args:
        path: Path where to look for work files to remove.
        
    """
    
    for file in os.listdir(path):
        
        if file.endswith(WORK_FILE_SUFFIX) or file.endswith(NORM_FILE_SUFFIX):
            
            try:
                full_file_name = os.path.join(path, file)
                os.remove(full_file_name)            
                                
            except OSError as oe:            
                logging.error("OSError removing temporary file: %s" % 
                              (full_file_name)) 
    
def generate_masterflat(path, flat_files, masterflat_name, masterbias_name):
    """Generates a master flat from the flat files_to_flat received.
    
    Args:
        path: Full source path of the flat files_to_flat.
        files_to_flat: List of flat files_to_flat.
        masterflat_name: The name of the masterflat file.
        masterbias_name: The name of the masterbias file.
        
    """
    
    logging.debug("Creating masterflat: %s" % (masterflat_name))   
    
    # Check that there is not any previous temporary file in the path, 
    # it could exists if a previous execution was terminated just before 
    # removing them.
    remove_temporary_files(path) 
    
    # Get the fit files in the directory, those should be only the flat ones.
    flat_files = glob.glob(os.path.join(path, "*." + FIT_FILE_EXT))
    
    reduce_flats(flat_files, masterbias_name)
    
    # Normalize the flats passing the list of flat files, 
    normalize_flats(flat_files) 
    
    norm_files = [os.path.join(path,f) for f in os.listdir(path) if f.endswith(NORM_FILE_SUFFIX)]

    # Put the normalized flat files list in a string to be used with 
    # imcombine. 
    string_of_norm_files = ",".join(norm_files)
    
    try:
        iraf.imcombine(string_of_norm_files, masterflat_name, Stdout=1)
    
    except iraf.IrafError as exc:
        logging.error("Error executing imcombine combining flats with: %s" %
                      (string_of_norm_files))
        
    finally:                
        remove_temporary_files(path)

def generate_all_masterflats(target_dir, flat_dir_name, dark_dir_name,
                             bias_dir_name):
    """Calculation of all the masterflat files.
    
    This function search for flat files from current directory.
    Usually data images are taken using different filters, so flat images
    are taken using the same filters, and into each flat directory the flat
    images are divides in different directories, one for each filter.
    Once a directory for flat had been found, a bias subtraction is performed
    with each flat image. Finally a masterflat is calculated for each flat 
    directory with an average operation using all the bias files.    
    
    Args:
        target_dir: Directory of the files.    
        flat_dir_name: Name of the directories containing flat images.    
        dark_dir_name: Name of the directories containing dark images.   
        bias_dir_name: Name of the directories containing bias images. 
        
    """
    
    logging.info("Generating all masterflats files from %s ..." % (target_dir))

    # Walk from current directory.
    for path, dirs, files in os.walk(target_dir):

        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == flat_dir_name:
                logging.debug("Found a directory for 'flat': %s" % (path))
                
                # Get the masterbias file name.
                masterbias_name = os.path.join(path,"..", "..", bias_dir_name,
                                               MASTERBIAS_FILENAME)

                # Create the masterflat only if it can be reduced with a bias,
                if os.path.exists(masterbias_name):                   
                    # Buid the masterflat file name.
                    masterflat_name = os.path.join(path, MASTERFLAT_FILENAME) 
                    
                    # Check if masterflat already exists.
                    if os.path.exists(masterflat_name) == True:
                        logging.warning("Masterflat file exists so resume " + 
                                        "to next directory.")
                    else:    
                        # Get the list of files.
                        files = glob.glob(os.path.join(path, WILDCARD_FIT_FILE))
                    
                        logging.debug("Found %d flat files" % (len(files)))
                                            
                        generate_masterflat(path, files, 
                                            masterflat_name,
                                            masterbias_name)  
                else:
                    logging.debug("There isn't a masterbias, " +
                                  "so the masterflat is not created.")                    
                    
def reduce_image(masterdark_name, masterbias_name, masterflat_name,
                 source_file_name, final_image_name):
    """Reduce an image.
    
    First, if the masterdark exists is subtracted, second, if the masterbias 
    exists is subtracted, later the image is divided by the flat if it exists.
    These aritmethic operations on the images are performed with imarith.    
    
    Args:
        masterdark_name: The full name of the masterdark file.
        masterbias_name: The full name of the masterbias file.
        masterflat_name: The full name of the masterflat file.
        source_file_name: Name of the file of the source image.
        final_image_name: The name for file of the image reduced.
    """
    
    # Get the work file name, a temporary file to store the result between bias
    # and flat application.
    work_file_name_1 = \
        source_file_name.replace("." + FIT_FILE_EXT, WORK1_FILE_SUFFIX)
        
    work_file_name_2 = \
        source_file_name.replace("." + FIT_FILE_EXT, WORK2_FILE_SUFFIX)
        
    # To control when ir is necessary the removing od temporary files.
    dark_reduction_success = False
    bias_reduction_success = False
    
    # Control imarith exception.
    try:
        # If masterdark exists.
        if masterdark_name:
            
            # Create the work files subtracting bias from flat.
            iraf.imarith(source_file_name, IMARITH_SUBTRACT, masterdark_name, 
                         work_file_name_1)
            
            dark_reduction_success = True
        else:
            
            # Use as work file (the input for flat step) the original file.
            work_file_name_1 = source_file_name         
        
        # If masterbias exists.
        if masterbias_name:
            
            # Create the work files subtracting bias from flat.
            iraf.imarith(work_file_name_1, IMARITH_SUBTRACT, masterbias_name, 
                         work_file_name_2)
            
            bias_reduction_success = True
        else:
            
            # Use as work file (the input for flat step) the original file.
            work_file_name_2 = work_file_name_1 
        
        # If masterflat exists.
        if masterflat_name: 
            
            # Create the final data dividing by master flat.
            iraf.imarith(work_file_name_2, IMARITH_DIVIDE, masterflat_name, 
                         final_image_name)
        else:
            # In this case the final file is the file resulting from bias 
            # step. It could be even the original file if the masterbias 
            # does not exist.
            shutil.copyfile(work_file_name_2, final_image_name) 
            
    except iraf.IrafError as exc:
        logging.error("Error in imarith reducing: %s" % (source_file_name))
        
        logging.error("Iraf error is: %s" % (exc))
        
    # Remove temporary file to save storage space.
    try:
        if masterdark_name and dark_reduction_success:
            os.remove(work_file_name_1)
            
        if masterbias_name and bias_reduction_success:
            os.remove(work_file_name_2)
    except OSError as oe:
        logging.error("Removing temporary files when reducing: '%s'." %
                      (source_file_name))        

def reduce_list_of_images(data_files, masterdark_filename, 
                          masterbias_filename, masterflat_filename):
    """Reduce the images contained in the list of files received applying the
    masterbias and masterflat also received.
    
    Args:
        data_files: List of file to reduce.
        masterdark_filename: Full path of the masterdark file.
        masterbias_filename: Full path of the masterbias file.
        masterflat_filename: Full path of the masterflat file.
    
    """
    
    # Walk the list of images to reduce them one by one.
    for source_image in data_files:
                
        final_file_pattern = "%s.%s" % (DATA_FINAL_SUFFIX, FIT_FILE_EXT)
        
        # Get the name of the final file.
        final_image = source_image.replace(".%s" % (FIT_FILE_EXT), 
                                           final_file_pattern)        
        
        if os.path.exists(final_image) or \
            source_image.endswith(final_file_pattern):
            logging.debug("Final image %s already exists, not reduced." %
                          final_image)
        elif masterbias_filename and masterflat_filename:
            # Reduce the image if there is a masterbias and a masterflat.
            reduce_image(masterdark_filename, masterbias_filename, 
                         masterflat_filename, source_image, final_image)
        else:
            logging.warning("Image %s not reduced, it lacks masterbias or masterflat."
                            % source_image)            


def reduce_data_images(target_dir, light_dir_name, dark_dir_name,
                       bias_dir_name, flat_dir_name):
    """Reduction all data images.
    
    This function search images from the source directory to reduce then. 
    Once a directory with images has been found, the data images that contains
    are processed to reduce them.
    The reduced images are saved in the same directory but with a different
    name to keep the original file. 
    
    Args:
        target_dir: Directory of the files.
        light_dir_name: Name of the directories containing data images.
        dark_dir_name: Name of the directories containing dark images.  
        bias_dir_name: Name of the directories containing bias images.    
        flat_dir_name:Name of the directories containing flat images.
        
    """

    # Walk from current directory.
    for path, dirs, files in os.walk(target_dir):

        # Inspect only directories without subdirectories. Only these
        # directories should contain files with images.
        if len(dirs) == 0:    
                    
            # Look for directories with data images.
            if is_light_directory(path, light_dir_name):
                
                logging.debug("Found a directory for data: %s" % (path))

                # Get the list of files.
                data_files = glob.glob(os.path.join(path, WILDCARD_FIT_FILE))
                
                logging.debug("Found %d data files" % (len(data_files)))
                
                # Get the names of masterdark, materbias and masterflat files 
                # to use for reduction.
                masterdark_name = get_masterdark_file_name(path, dark_dir_name)
                
                masterbias_name = get_masterbias_file_name(path, bias_dir_name)
                    
                masterflat_name = get_masterflat_file_name(path, flat_dir_name)       

                reduce_list_of_images(data_files, masterdark_name, 
                                      masterbias_name, masterflat_name)

                        
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
    generate_all_masterbias(progargs.target_dir,
                            progargs.bias_directory)

    # Generate all the average dark.
    generate_all_masterdark(progargs.target_dir,
                            progargs.dark_directory,
                            progargs.bias_directory)

    # Generate all the average flat.
    generate_all_masterflats(progargs.target_dir,
                             progargs.flat_directory,
                             progargs.dark_directory,
                             progargs.bias_directory)

    # Reduce all the data images applying the average bias and flats.
    reduce_data_images(progargs.target_dir,
                       progargs.light_directory,
                       progargs.dark_directory,
                       progargs.bias_directory,
                       progargs.flat_directory)
    
    logging.info("Finished the reduction of images.")    
