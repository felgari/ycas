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

"""This module get some summaries from a directory structure containing fit
images processed by ycas.

This module could be used as an independent program but also is used from ycas
to generate a final summary of the steps performed by the pipeline.
"""

import sys
import os
import logging
import glob
import argparse
import numpy as np
from scipy.stats import mode
from constants import *

PATH_COL = 0
FILE_NAME_COL = 1

FITS_FILE_PATTERN = "*." + FIT_FILE_EXT

class SummaryTasks(object):
    """ Encapsulates the summary tasks to perform.
    """
    
    ORG_SUM_NAME = "Organization"
    RED_SUM_NAME = "Reduction"
    ASTRO_SUM_NAME = "Astrometry"
    PHOT_SUM_NAME = "Photometry"
    MAG_SUM_NAME = "Magnitude"

    SUMMARY_TASKS = [ORG_SUM_NAME, RED_SUM_NAME, ASTRO_SUM_NAME, 
                     PHOT_SUM_NAME, MAG_SUM_NAME]
        
    __SUM_PRO_NAME_COL = 0
    __SUM_PRO_REQ_PROP_COL = 1
    __SUM_PRO_BUILD_FUN_COL = 2    
    
    def __init__(self):
        
        self._tasks_to_do = {
                SummaryTasks.ORG_SUM_NAME : False,
                SummaryTasks.RED_SUM_NAME : False,
                SummaryTasks.ASTRO_SUM_NAME : False,
                SummaryTasks.PHOT_SUM_NAME : False,
                SummaryTasks.MAG_SUM_NAME : False }
        
    # List of methods to use to get the summary of each task.       
        self.__SUMMARY_METHODS = {
               SummaryTasks.ORG_SUM_NAME : self.summary_organization,
               SummaryTasks.RED_SUM_NAME : self.summary_reduction,
               SummaryTasks.ASTRO_SUM_NAME : self.summary_astrometry,
               SummaryTasks.PHOT_SUM_NAME : self.summary_photometry,
               SummaryTasks.MAG_SUM_NAME : self.summary_magnitude }  
       
    @property 
    def enable_organization_summary(self):
        self._tasks_to_do[SummaryTasks.ORG_SUM_NAME] = True
        
    @property 
    def enable_reduction_summary(self):
        self._tasks_to_do[SummaryTasks.RED_SUM_NAME] = True    
        
    @property 
    def enable_astrometry_summary(self):
        self._tasks_to_do[SummaryTasks.ASTRO_SUM_NAME] = True
        
    @property 
    def enable_photometry_summary(self):
        self._tasks_to_do[SummaryTasks.PHOT_SUM_NAME] = True               
        
    @property 
    def enable_magnitude_summary(self):
        self._tasks_to_do[SummaryTasks.MAG_SUM_NAME] = True                 
        
    def enable_all_summary_task(self):
        """Enable the calculation of all sumaries.
        
        """
        
        # Walk the possible summaries to perform to enable them all.
        for std in SummaryTasks.SUMMARY_TASKS:        
            self._tasks_to_do[std] = True
        
    def enable_summary_task(self, summary_task):
        """Enables the summary for a given task.
        
        Args:
            summary_task. The task to enable.
        """
        
        try:
            self._tasks_to_do[summary_task] = True
        except KeyError as ke:
            logging.error("Value '%s' is invalid to reference a summary." %
                          summary_task)
            
    def generate_summary(self):
        """
        
        """         

        # Walk the possible summaries to perform.
        for std in SummaryTasks.SUMMARY_TASKS:
             
             # Check if this summary has been requested.
             if self._tasks_to_do[std]:
                 self.__SUMMARY_METHODS[std]()
             
            
    def is_summary_task_enabled(self, summary_option):
        """Indicates if the summary for a given task is enabled.
        
        Args:
            summary_task. The task to enable.
            
        Return:
            True if enabled, False otherwise.
        """        
                
        enabled = False
        
        try:
            enabled = self._tasks_to_do[summary_task]
        except KeyError as ke:
            logging.error("Option '%s' invalid for summary." %
                          summary_task)  
            
        return enabled   
    
    @property
    def is_any_summary_task_enabled(self):  
        
        any_enabled = False
        
        for std in SummaryTasks.SUMMARY_TASKS:
            if self._tasks_to_do[std]:
                any_enabled = True
                break 
        
        return any_enabled  
    
    def print_and_log_info(self, log_msg):
        """ Print the string received to sdtout and to logging with info level. 
        """     
        
        print log_msg
        logging.info(log_msg)        
            
    def print_summary(self, sum_name, msg_list):
        """ Print the strings of the list received as a summary. """
        
        self.print_and_log_info("* Summary for: %s" % (sum_name))
        
        for l in msg_list:
            self.print_and_log_info("- " + l[0])            
            
    def walk_directories(self, root_dir, file_pattern, dir_name = None,
                         dir_for_images = False):
        """Walk the directories from the root directory indicated searching
        for directories and files that match the patterns received and
        return the files matching these criteria.
        
        Args: 
            root_dir: Root directory to search files.
            file_pattern: Pattern of the file to search. 
            dir_name: Name of the directory to look for, if any.
            dir_for_images: Indicates it it is a directory with images.
        
        Returns:        
        
        """
        
        directories_found = []
        files_found = []
        
        # Subdirectories into root directory, all are supposed to be
        # directories with fits images.
        directories_from_root = os.walk(root_dir).next()[1]
        
        # Walk all the directories searching for directories and files that
        # matches the patterns received.
        for path, dirs, files in os.walk(root_dir):
    
            # Split the string with the path to get the names of the
            # parent directories.
            split_path = path.split(os.sep)
    
            # Check if current directory matches any of the directory criteria.
            # Matches the directory name received or it is a directory whose
            # images are by filters so has one additional directory level.
            if ( dir_name <> None and split_path[-1] == dir_name ) or \
                ( dir_for_images and len(split_path) > 2 and \
                  split_path[-2] == dir_name ):
    
                # Get the list of files of current directory matching 
                # the pattern received and ignoring the hidden files.
                dir_contents = \
                    [f for f in glob.glob(os.path.join(path, file_pattern)) \
                    if not os.path.basename(f).startswith('.')]
                    
                # For all the contents of current directory check if it is
                # a directory or a file and include it in the appropriate list.
                for dc in dir_contents:
                    if os.path.isdir(dc):
                        directories_found.extend([dc])
                    else:
                        files_found.extend([dc])
            
        # Get the files found with the path and file name splitted.
        directories_found
        files_found_path_splited = [ os.path.split(ff) for ff in files_found ]
        
        return directories_found, files_found_path_splited, \
            directories_from_root
    
    
    def sum_org_images_of_type(self, messages, has_filters, type_name, 
                                     dir_name, master_file_name = None):
        """Generates a summary for the images.
        
        Args:    
            messages: List where the messages are added.
            has_filters: Indicates if the directories are organized by filters.
            type_name: Name of the type of image analyzed.
            dir_name: Directory to walk to search for images.
            master_file_name: Name of the master file, if any.
                    
        """
        
        messages.append(["> Summary for %s files." % (type_name)])
        
        subdirectories, files, directories_from_root = \
            self.walk_directories(".", "*", dir_name, True)
            
        # Number of directories with data (from root).        
        number_of_directories = len(directories_from_root)          
        
        if has_filters:
            # Store a list of unique filters. Take all the paths and split them
            # to get the filter component, and add all to a set, that is converted
            # to a list.
            filters = list(set([s.split(os.sep)[-1] for s in subdirectories]))
            
            messages.append(["Number of filters with %s files is: %d" %
                             (type_name, len(filters))])
            
            messages.append(["Filters used by %s: %s" %
                             (type_name, str(filters))])
    
        # Get the list of directories found containing files.
        unique_paths = set([ff[PATH_COL] for ff in files])
    
        # Summary: Number of unique directories.
        messages.append(["Number of %s directories: %d" %
                         (type_name, len(unique_paths))])
    
        # The number of files in each directory is stored here.
        num_files_by_dir = []
        
        # Number of mater files found in each directory, it is calculated only
        # 
        num_master = 0
    
        # Apply the following statistics if these files are used to create a mater
        # file (i.e. bias or flats).
        if master_file_name is not None:
            # Summary: Number of master files created.
            master = [fb for fb in files if fb[FILE_NAME_COL] == \
                      master_file_name]
            num_master = len(master)
            messages.append(["Number of master %s: %d" % 
                             (type_name, num_master)])
        
            # Number of directories with files and without master Important!).
            dir_without_master = []
            
            for ubp in unique_paths:
                # Get the files of each directory.
                files_of_dir = [bf for bf in files if bf[PATH_COL] == ubp]
                
                # Get the master file of this directory if any.
                master_file = [bf for bf in files_of_dir \
                                 if bf[FILE_NAME_COL] == master_file_name]
                
                # If this directory has not master.
                if len(master_file) == 0:
                    dir_without_master.extend([ubp])
                    
                # The number of files in this directory is the total number
                # of files minus the master fits found.
                num_of_files = len(files_of_dir) - len(master_file)
                num_files_by_dir.extend([num_of_files])
                
                messages.append(["Directory: '%s' Number of files: %d" %
                                 (ubp, num_of_files)])             
        
            # Summary: Number of directories with files and no master.
            messages.append(["Number of directories with %s and no master %s: %d" %
                             (type_name, type_name, len(dir_without_master))])
            
            # If any directory has no master, show its path.
            if len(dir_without_master) > 0:
                messages.append(["Directories without master %s : %s" %
                                 (type_name, str(dir_without_master))])
           
        else:               
            # Count the number of files in each directory. Now taking into
            # account names of files and its number instead of master files. 
            for ubp in unique_paths:
                
                # Objects in the directory whose path matched those of unique set.            
                all_objects_of_dir = [ f[FILE_NAME_COL] for f in files \
                                      if f[PATH_COL] == ubp ]          
                
                # Take as objects names those of FIT images, not final, and only
                # the part name that identifies the object.
                objects_of_dir = [ o[:o.find(DATANAME_CHAR_SEP)] 
                                  for o in all_objects_of_dir \
                                  if o.find("." + FIT_FILE_EXT) > 0 and
                                  o.find(DATA_FINAL_SUFFIX) < 0 ]
                
                # The number of files in this directory is the total number
                # of files minus the master fits found.
                num_files_by_dir.extend([len(objects_of_dir)])
                
                messages.append(["Directory: '%s' Number of files: %d" % 
                                 (ubp, len(objects_of_dir))]) 
                
                unique_objects_of_dir = set(objects_of_dir)
                
                for uo in unique_objects_of_dir:
                    num_objs = len([ o for o in objects_of_dir if o == uo ])  
                    
                    messages.append(["Object: '%s' Number of files: %d" %
                                     (uo, num_objs)])          
                
        # Create a set containing the root directories that contains files.
        # The source set contains a directory for each filter, so it may
        # contain several directories for each root directory.
        unique_root_dir_with_files = set([x.split(os.sep)[1] for x in unique_paths])
    
        # Summary: Number of directories without files.
        # The total number of minus the number of directories without files.
        num_dir_without_files = \
            number_of_directories - len(unique_root_dir_with_files)
        messages.append(["Number of directories without %s files: %d" %
                          (type_name, num_dir_without_files)])
            
        # Summary: Number of files.
        num_files = sum(num_files_by_dir)
        messages.append(["Number of %s files is: %d" % (type_name, num_files)])
            
        if len(num_files_by_dir) > 0: 
            max_files_by_dir = max(num_files_by_dir)
            min_files_by_dir = min(num_files_by_dir)
            avg_files_by_dir = sum(num_files_by_dir) / len(num_files_by_dir)
            std_files_by_dir = np.std(num_files_by_dir)
            med_files_by_dir = np.median(num_files_by_dir)
            mode_files_by_dir = mode(num_files_by_dir)[0][0]
        else:
            max_files_by_dir = 0
            min_files_by_dir = 0
            avg_files_by_dir = 0
            std_files_by_dir = 0
            med_files_by_dir = 0
            mode_files_by_dir = 0
            
        # Summary: Maximum number of files in directories.
        messages.append(["Maximum number of %s files in directories: %d" %
                         (type_name, max_files_by_dir)])
        
        # Summary: Minimum number of files in directories.
        messages.append(["Minimum number of %s files in directories: %d" % 
                         (type_name, min_files_by_dir)])    
    
        # Summary: Average of number of files in directories.
        messages.append(["Average of number of %s files in directories: %.10g" %
                         (type_name, avg_files_by_dir)])
        
        # Summary: Standard deviation of number of files in directories.
        messages.append(["Standard deviation of number of %s files in directories: %.10g" %
                         (type_name, std_files_by_dir)])
    
        # Summary: Median of number of files in directories.
        messages.append(["Median of number of %s files in directories: %.10g" %
                         (type_name, med_files_by_dir)])
        
        # Summary: Mode of number of files in directories.
        messages.append(["Mode of number of %s files in directories: %.10g" %
                         (type_name, mode_files_by_dir)])
    
    def summary_organization(self):
        """ Get the summary for: Organization. """
        
        messages = []   
            
        # Summary for bias.        
        self.sum_org_images_of_type(messages, False, "bias", BIAS_DIRECTORY,
                               MASTERBIAS_FILENAME)         
            
        # Summary for flats.        
        self.sum_org_images_of_type(messages, True, "flat", FLAT_DIRECTORY,
                               MASTERFLAT_FILENAME)  
        
        # Summary for data files.
        self.sum_org_images_of_type(messages, True, "image", DATA_DIRECTORY)    
        
        # Statistics for all the set, for each object of interest and for each
        # standard star and taking into account the filters.
        
        self.print_summary(SummaryTasks.ORG_SUM_NAME, messages)
    
    def summary_reduction(self):
        """Get the summary for: Reduction. """
        
        messages = []      
        
        # Get all the files related to data images.
        subdirectories, files, directories_from_root = \
            self.walk_directories(".", "*." + FIT_FILE_EXT, DATA_DIRECTORY, 
                                  True)
            
        # All the final images with its full path.
        final_images = [os.path.join(f[PATH_COL], f[FILE_NAME_COL]) \
                        for f in files \
                        if f[FILE_NAME_COL].find(DATA_FINAL_SUFFIX) > 0]    
        
        # Original images, those not final.
        image_files_no_final = [os.path.join(f[PATH_COL], f[FILE_NAME_COL]) \
                                for f in files \
                                if f[FILE_NAME_COL].find(DATA_FINAL_SUFFIX) < 0]
        
        images_reduced = 0
        images_not_reduced = []    
    
        # Check if each image has a final one.
        for i in range(len(image_files_no_final)):
            inf = image_files_no_final[i]
            
            final_image = inf.replace("." + FIT_FILE_EXT, \
                                      DATA_FINAL_SUFFIX + "." + FIT_FILE_EXT)
             
            # Check if the final image related to current one exists.       
            if final_image in final_images:
                images_reduced += 1
            else:
                images_not_reduced.extend([final_image])
          
        # Print the summary.      
        messages.append(["Total number of images: %d" % 
                         len(image_files_no_final)])
        
        messages.append(["Number of images not reduced: %d" %
                         len(images_not_reduced)])
          
        if len(images_not_reduced) > 0:
            messages.append(["Images not reduced: %s" % 
                             (str(images_not_reduced))])
        
        self.print_summary(SummaryTasks.RED_SUM_NAME, messages)        
    
    def summary_astrometry(self):
        """Get the summary for: Astrometry. """
        
        messages = []      
        
        # Get all the files related to catalog images.
        subdirectories, files, directories_from_root = \
            self.walk_directories(".", "*." + FIT_FILE_EXT, DATA_DIRECTORY, 
                                  True)   
        
        # Original images, those not final.
        image_files_no_final = [os.path.join(f[PATH_COL], f[FILE_NAME_COL]) \
                                for f in files \
                                if f[FILE_NAME_COL].find(DATA_FINAL_SUFFIX) < 0]
        
        images_catalogued = 0
        images_not_catalogued = []    
    
        # Check if each image has a final one.
        for i in range(len(image_files_no_final)):
            image = image_files_no_final[i]
            
            catalog_file = image.replace("." + FIT_FILE_EXT, \
                                         "." + CATALOG_FILE_EXT)
             
            # Check if the final image related to current one exists.       
            if os.path.exists(catalog_file):
                images_catalogued += 1
            else:
                images_not_catalogued.extend([image])
          
        # Print the summary.      
        messages.append(["Total number of images: %d" %
                         (len(image_files_no_final))])
        
        messages.append(["Number of images not catalogued: %d" %
                         (len(images_not_catalogued))])
          
        if len(images_not_catalogued) > 0:
            messages.append(["Images not catalogued:\n %s" %
                             str(images_not_catalogued)])
        
        self.print_summary(SummaryTasks.ASTRO_SUM_NAME, messages)
    
    def summary_photometry(self):
        """ Get the summary for: Photometry. """
        
        messages = []      
        
        # Get all the original files related to images.
        subdirectories, files, directories_from_root = \
            self.walk_directories(".", "*." + FIT_FILE_EXT, DATA_DIRECTORY, 
                                  True)   
        
        # Original images, those not final.
        image_files_no_final = [os.path.join(f[PATH_COL], f[FILE_NAME_COL]) \
                                for f in files \
                                if f[FILE_NAME_COL].find(DATA_FINAL_SUFFIX) < 0]
        
        images_with_photometry = 0
        images_without_photometry = []    
    
        # Check if each image has a final one.
        for i in range(len(image_files_no_final)):
            image = image_files_no_final[i]
            
            photometry_file = image.replace("." + FIT_FILE_EXT, \
                                            DATA_FINAL_SUFFIX + \
                                            FILE_NAME_PARTS_DELIM + \
                                            MAGNITUDE_FILE_EXT + "." + CSV_FILE_EXT)
             
            # Check if the final image related to current one exists.       
            if os.path.exists(photometry_file):
                images_with_photometry += 1
            else:
                images_without_photometry.extend([image])
          
        # Print the summary.      
        messages.append(["Total number of images: %d" %
                         len(image_files_no_final)])
        
        messages.append(["Number of images without photometry: %d" %
                         len(images_without_photometry)])
          
        if len(images_without_photometry) > 0:
            messages.append(["Images without photometry:\n %s" %
                             str(images_without_photometry)])
        
        self.print_summary(SummaryTasks.PHOT_SUM_NAME, messages)
    
    def summary_magnitude(self):
        """Get the summary for: Magnitude. """
        
        messages = []
        
        messages.append(["Not implemented yet!"])
        
        self.print_summary(SummaryTasks.MAG_SUM_NAME, messages)

class SummaryArguments(object):
    """ Encapsulates the definition and processing of program arguments for
        summaries as an independent program.
        
    """
    
    MIN_NUM_ARGVS = 1
    DEFAULT_DESTINY_FILE = "ycas_sum.txt"    
    DEFAULT_LOG_FILE_NAME = "sum_log.txt"
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object
        with the definition of arguments to use.

        """                
            
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-d", metavar="destiny file name", \
                                   dest="d", help="Name of the output file")       
        
        self.__parser.add_argument("-all", dest="all", action="store_true", \
                                   help="Get all the summaries available.")   
           
        self.__parser.add_argument("-o", dest="o", action="store_true", \
                                   help="Get summaries for organization.") 
        
        self.__parser.add_argument("-r", dest="r", action="store_true", \
                                   help="Get summaries for reduction.") 
        
        self.__parser.add_argument("-s", dest="s", action="store_true", \
                                   help="Get summaries for astrometry.")   
        
        self.__parser.add_argument("-p", dest="p", action="store_true", \
                                   help="Get summaries for photometry.") 
        
        self.__parser.add_argument("-m", dest="m", action="store_true", \
                                   help="Get summaries for magnitudes.") 
        
        self.__parser.add_argument("-l", metavar="log file name", dest="l", \
                                   help="File to save the log messages")         
         
    @property
    def destiny_file_name(self):
        return self.__args.d  
    
    @property
    def log_file_name(self):
        return self.__args.l      
    
    @property
    def summary_all(self):
        return self.__args.all 
    
    @property
    def summary_organization(self):
        return self.__args.o 
    
    @property
    def summary_reduction(self):
        return self.__args.r    
    
    @property
    def summary_astrometry(self):
        return self.__args.s 
    
    @property
    def summary_photometry(self):
        return self.__args.p     
    
    @property
    def summary_magnitude(self):
        return self.__args.m               
    
    def parse(self):
        """ 
        
        Initialize properties and performs the parsing 
        of program arguments.
        
        """
        
        # Parse program arguments.
        self.__args = self.__parser.parse_args()
            
        if self.__args.d is None:
            self.__args.d = SummaryArguments.DEFAULT_DESTINY_FILE 
            
        if self.__args.l is None:
            self.__args.l = SummaryArguments.DEFAULT_LOG_FILE_NAME  
            
    def args_summary(self):
        """ Print a brief summary of the arguments received. """
        
        print "Using the following parameters:"
        print "- Destiny file: " + self.__args.d 
        print "- Log file: " + self.__args.l
        print ""   
                    
    def print_usage(self):
        """ Print arguments options """
        
        self.__parser.print_usage()    
        
    def print_help(self):
        """ Print help for arguments options """
                
        self.__parser.print_help()
        
def init_log(progargs):
    """ Initializes the file log and messages format. 
    
    Args: 
        progargs: Program arguments.
    
    """    
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=progargs.log_file_name, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging.DEBUG)
    
    logging.debug("Logging initialized.")       
            
def main(progargss):
    """ Determines the summaries to generate and call to generate them.
    
    Args: 
        progargs - Program arguments.
        
    """
    
    # Process program arguments.
    progargs.parse()           
        
    # Initializes logging.
    init_log(progargs)  
    
    # Object that generates the summary.     
    sum_task = SummaryTasks()
    
    # Set the summaries to generate.
    if progargs.summary_all:
        sum_task.enable_all_summary_task()

    else:
        if progargs.summary_organization:
            sum_task.enable_organization_summary
            
        if progargs.summary_reduction:
            sum_task.enable_reduction_summary
            
        if progargs.summary_astrometry:
            sum_task.enable_astrometry_summary   
            
        if progargs.summary_photometry:
            sum_task.enable_photometry_summary
            
        if progargs.summary_magnitude:
            sum_task.enable_magnitude_summary

    sum_task.generate_summary()
        
    if not sum_task.is_any_summary_task_enabled:
        progargs.print_help()                
    
    return 0
        
# Where all begins ...
if __name__ == "__main__":
    
    # Create object to process program arguments.
    progargs = SummaryArguments()    
    
    # Process program arguments.
    progargs.parse()      
    
    # Show a summary of the arguments received.
    progargs.args_summary()    
    
    # If no enough arguments are provided, show help and exit.
    if len(sys.argv) <= SummaryArguments.MIN_NUM_ARGVS:
        print "The number of program arguments are not enough."
        progargs.print_help()
        sys.exit(1)
    else: 
        sys.exit(main(progargs))        