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

"""This module contains classes that generates a summary report describing the
results of the steps performed by the pipeline.

"""

import sys
import os
import glob
import time
import logging
import numpy as np
from scipy.stats import mode
from constants import *

PATH_COL = 0
FILE_NAME_COL = 1

class SummaryException(Exception):
    """Raised for different errors that could arise generating the report."""
    
    def __init__(self, msg):
        self._msg
        
    def __str__(self):
        return self._msg

class SummaryReport(object):
    """Encapsulates the summary report to generate."""
    
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
    
    def __init__(self, progargs, report_file_name, stars, stars_mag):
        """Constructor.
        
        Args:
            progargs: Program arguments.
            target_dir: Directory that contains the files to process.
            report_file_name: Name of the file where the report is saved.
            stars: List of stars.
            stars_mag: The magnitudes calculated, if any.
            
        """
        
        self._target_dir = progargs.target_dir
        self._report_file_name = report_file_name
        self._light_dir_name = progargs.light_directory
        self._bias_dir_name = progargs.bias_directory
        self._flat_dir_name = progargs.flat_directory
        self._stars = stars
        self._stars_mag = stars_mag
        self._all_messages = []
        
        self._tasks_to_do = {
                SummaryReport.ORG_SUM_NAME : False,
                SummaryReport.RED_SUM_NAME : False,
                SummaryReport.ASTRO_SUM_NAME : False,
                SummaryReport.PHOT_SUM_NAME : False,
                SummaryReport.MAG_SUM_NAME : False }
        
        # List of methods to use to get the summary of each task.       
        self.__SUMMARY_METHODS = {
               SummaryReport.ORG_SUM_NAME : self.summary_organization,
               SummaryReport.RED_SUM_NAME : self.summary_reduction,
               SummaryReport.ASTRO_SUM_NAME : self.summary_astrometry,
               SummaryReport.PHOT_SUM_NAME : self.summary_photometry,
               SummaryReport.MAG_SUM_NAME : self.summary_magnitude }  
       
    @property
    def report_file_name(self):
        # The name of the report includes the day and time so ii could be
        # different in each invocation.
        return "%s_%s" % \
            (time.strftime("%Y%m%d_%H%M%S", time.gmtime()), 
             self._report_file_name)
       
    @property 
    def enable_organization_summary(self):
        self._tasks_to_do[SummaryReport.ORG_SUM_NAME] = True
        
    @property 
    def enable_reduction_summary(self):
        self._tasks_to_do[SummaryReport.RED_SUM_NAME] = True    
        
    @property 
    def enable_astrometry_summary(self):
        self._tasks_to_do[SummaryReport.ASTRO_SUM_NAME] = True
        
    @property 
    def enable_photometry_summary(self):
        self._tasks_to_do[SummaryReport.PHOT_SUM_NAME] = True               
        
    @property 
    def enable_magnitude_summary(self):
        self._tasks_to_do[SummaryReport.MAG_SUM_NAME] = True                 
        
    def enable_all_summary_task(self):
        """Enable the calculation of all sumaries.
        
        """
        
        # Walk the possible summaries to perform to enable them all.
        for std in SummaryReport.SUMMARY_TASKS:        
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
        """Generate the summary. Check all the steps to determine those whose
        report has been requested. Finally a report is saved to a file.
        
        """         

        # Walk the possible summaries to perform.
        for std in SummaryReport.SUMMARY_TASKS:
             
             # Check if this summary has been requested.
             if self._tasks_to_do[std]:
                 self.__SUMMARY_METHODS[std]()
                 
        self.save_complete_report()             
            
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
        """Returns True if the report has been requested at least for a task.
        """   
        
        any_enabled = False
        
        for std in SummaryReport.SUMMARY_TASKS:
            if self._tasks_to_do[std]:
                any_enabled = True
                break 
        
        return any_enabled  
    
    def print_and_log_info(self, log_msg):
        """ Print the string received to stdout and to logging with info level. 
        """     
        
        print log_msg
        logging.info(log_msg)        
            
    def print_summary(self, sum_name, msg_list):
        """ Print the strings of the list received as a summary. """
        
        report_title = "* Summary for: %s" % (sum_name)
        
        self.print_and_log_info(report_title)        
        
        # Store it to write the file to the end.
        self._all_messages.append([report_title])        
        
        for l in msg_list:
            msg_text = "- " + l[0]
            self.print_and_log_info(msg_text)
            self._all_messages.append([msg_text])  
            
    def save_complete_report(self):
        """Save all the summary messages to a file. """
        
        try:
            with open(self.report_file_name, 'a') as fw:
                
                for m in self._all_messages:
                    fw.write("%s\n" % (m))
                    
        except IOError as ioe:
            logging.error("Writing report file: '%s'" % (self.report_file_name))                        
            
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
            The directories and files found that matches the patterns received.
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
            self.walk_directories(self._target_dir, "*", dir_name, True)
            
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
        self.sum_org_images_of_type(messages, False, "bias", 
                                    self._bias_dir_name,
                                    MASTERBIAS_FILENAME)         
            
        # Summary for flats.        
        self.sum_org_images_of_type(messages, True, "flat", self._flat_dir_name,
                                    MASTERFLAT_FILENAME)  
        
        # Summary for data files.
        self.sum_org_images_of_type(messages, True, "image", self._light_dir_name)    
        
        # Statistics for all the set, for each object of interest and for each
        # standard star and taking into account the filters.
        
        self.print_summary(SummaryReport.ORG_SUM_NAME, messages)
    
    def summary_reduction(self):
        """Get the summary for: Reduction. """
        
        messages = []
        all_light_files = []      
        all_files = []
        all_dirs = []
        
        # Compile all the images and directories. 
        for path, dirs, files in os.walk(self._target_dir):
            all_files.extend(files)
            all_dirs.extend(dirs)   
            
            path_split_head = os.path.split(path)[0]
            
            if os.path.split(path_split_head)[1] == self._light_dir_name:
                
                all_light_files.extend([ f for f in files \
                                        if f.endswith(FIT_FILE_EXT) ])
            
        # Count the number of masterdark files.
        masterdark_files = [ f for f in all_files \
                                if f == MASTERDARK_FILENAME]
        
        # Count the number of masterbias files.
        masterbias_files = [ f for f in all_files \
                                if f == MASTERBIAS_FILENAME]     
        
        # Count the number of masterflat files.
        masterflat_files = [ f for f in all_files \
                                if f == MASTERFLAT_FILENAME]
        
        final_images = [ f for f in all_light_files \
                        if f.find(DATA_FINAL_SUFFIX) > 0 ]     
        
        messages.append(["Total number of masterdark files: %d" % 
                         len(masterdark_files)])  
        
        messages.append(["Total number of masterbias files: %d" % 
                         len(masterbias_files)])  
        
        messages.append(["Total number of masterflat files: %d" % 
                         len(masterflat_files)])                              
        
        messages.append(["Images reduced: %d" % (len(final_images))])
        
        messages.append(["Images not reduced: %d" % \
                         (len(all_light_files) - 2 * len(final_images))])                
        
        self.print_summary(SummaryReport.RED_SUM_NAME, messages)        
    
    def summary_astrometry(self):
        """Get the summary for: Astrometry. """
        
        messages = []      
        
        # Get all the files related to catalog images.
        subdirectories, files, directories_from_root = \
            self.walk_directories(self._target_dir, "*." + FIT_FILE_EXT, 
                                  self._light_dir_name, True)   
        
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
        
        messages.append(["Number of images not cataloged: %d" %
                         (len(images_not_catalogued))])
          
        if len(images_not_catalogued) > 0:
            messages.append(["Images not cataloged:\n %s" %
                             str(images_not_catalogued)])
        
        self.print_summary(SummaryReport.ASTRO_SUM_NAME, messages)
    
    def summary_photometry(self):
        """ Get the summary for: Photometry. """
        
        messages = []      
        
        # Get all the original files related to images.
        subdirectories, files, directories_from_root = \
            self.walk_directories(self._target_dir, "*." + FIT_FILE_EXT,
                                  self._light_dir_name, True)   
        
        # Original images, those not final.
        image_files_no_final = [os.path.join(f[PATH_COL], f[FILE_NAME_COL]) \
                                for f in files \
                                if f[FILE_NAME_COL].find(DATA_FINAL_SUFFIX) < 0]
        
        images_with_photometry = 0
        images_without_photometry = []    
    
        # Check if each image has a final one.
        for i in range(len(image_files_no_final)):
            image = image_files_no_final[i]
            
            photometry_file = image.replace(".%s" % (FIT_FILE_EXT),
                                            "%s%s%s" %
                                            (DATA_FINAL_SUFFIX,
                                            FILE_NAME_PARTS_DELIM,
                                            MAG_CSV_PATTERN))
             
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
        
        self.print_summary(SummaryReport.PHOT_SUM_NAME, messages)
    
    def summary_magnitude(self):
        """Get the summary for: Magnitude. """
        
        messages = []
        
        # Check if the magnitudes have been received
        if self._stars:
            if self._stars_mag is None:                
                self._stars_mag = StarMagnitudes(self._stars)
                
                self._stars_mag.read_magnitudes(self._target_dir)
        else:
            raise SummaryException("A file with information about " + \
                                   "stars must be specified to " + \
                                   "generate a summary of magnitudes")
        
        # Process the magnitudes of each no standard star. 
        for s in self._stars_mag.stars:            
            if not s.is_std:                
                mags = self._stars_mag.get_mags_of_star(s.name)
                
                inst_mag = 0
                ext_cor_mag = 0
                calib_mag = 0
                
                # Count the number of magnitudes of each type for current star.
                for m in mags:
                    inst_mag += 1
                    
                    if not m.ext_cor_mag is None:
                        ext_cor_mag += 1
                        
                    if not m.calib_mag is None:
                        calib_mag += 1
                        
                messages.append(["Star %s has: " % s.name])
                messages.append(["%d instrumental magnitudes." %
                                 inst_mag])
                messages.append(["%d extinction corrected magnitudes." %
                                 ext_cor_mag])
                messages.append(["%d calibrated magnitudes." %
                                 calib_mag])                 
        
        # Print the summary.
        self.print_summary(SummaryReport.MAG_SUM_NAME, messages)