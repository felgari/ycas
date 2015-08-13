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

"""This module organize the files to process into different directories.

The organization takes into account the session (day) where was taken and 
the type of the image: bias, flat or data.

The module assume that images are initially stored in directories that 
corresponds to the day which were taken.

Into each day the images are organized in a directory for bias, another
for flats and another for data.

Also flats and data images are organized in different subdirectories,
one for each filter. 
"""

import sys
import os
import logging
import yargparser
import shutil
import pyfits
import textfiles
import fitsheader
import fitfiles
from fitfiles import *
from constants import *

class Filters(object):
    """Stores the filters that should be taking into account when processing
    images.
    """
    
    def __init__(self, file_name):
        """Constructor.
        
        Args:
            file_name: The name of the file that contains the filters.            
        """
        
        self.__iter_idx = 0
        
        self._filters = set()
        
        self._filters_list = []
        
        self.read_filters(file_name)
        
    def __str__(self):
        return str(self._filters)
    
    def __iter__(self):
        self.__iter_idx = 0
        
        return self       
        
    # Python 3 compatibility
    def __next__(self):
        return self.next()
    
    def next(self):
        if self.__iter_idx < len(self._filters_list):
            cur, self.__iter_idx = \
                self._filters_list[self.__iter_idx], self.__iter_idx + 1
            return cur
        else:
            raise StopIteration()
        
    def read_filters(self, file_name):
        """Read the filters to use from a file.
        
        Each filter must be indicated in a line.
        
        Args:
            file_name: The name of the file that contains the filters.        
        """
        
        logging.debug("Reading filters from file: %s" % (file_name))
        
        try:
            # Read the file that contains the filters.
            with open(file_name, "r") as f:
                for line in f:
                    filter_name = line.strip()
                    if len(filter_name) > 0 \
                        and filter_name[0] != COMMENT_CHARACTER:
                        self._filters.add(filter_name)  
                    
            logging.debug("Read the following filters: %s" % (self._filters))
            
            self._filters_list = list(self._filters)
            
        except TypeError as te:
            logging.debug("%s. Reading file: '%s'" % (te, file_name))
            
        except IOError as ioe:
            logging.error("Reading filters file: '%s'" % (file_name))            
        
    def exists(self, filter_name):
        """Search for a filter with the name received.
        
        Args:
            filter_name: The name of the filter to search.
            
        Returns:
            True if the filter is found, False otherwise.
        """
        
        return filter_name in self._filters

class OrganizeFIT(object):
    """A class to organize the FIT files in a directory structure depending on
    the day of the observations and the type of file.
    
    This structure is used by all the pipeline steps.
    
    """
    
    def __init__(self, progargs, stars, header_fields, filters):
        
        self._progargs = progargs
        self._stars = stars
        self._header_fields = header_fields
        self._filters = filters
                
    def create_directory(self, dir_name):
        """ Create a directory with the given name. 
        
        This function creates a directory with the given name located in the
        path received.
        
        Args: 
            dir_name: Directory to create.
            
        Raises:
            OSError if the directory can not be created.
        
        """
    
        # Check if the directory exists.
        if not os.path.exists(dir_name):
            
            try: 
                logging.debug("Creating directory: %s" % (dir_name))
                os.makedirs(dir_name)
                
            except OSError:
                if not os.path.isdir(dir_name):
                    raise                
                
    def get_star_name(self, full_file_name, file_header):
        """Returns the name of the star, from the header if possible, otherwise
        is extracted from the name of the file. In this case following the
        pattern of the OSN (Observatorio de Sierra Nevada).
        
        Args:
            full_file_name: The name of the file.
            file_header: Header of the file.
        
        """
        
        star_name = file_header[self._header_fields.object].strip()
        
        # If the name if the header is the default one, extract it from
        # the name of the file.
        if star_name == fitsheader.DEFAULT_OBJECT_NAME:
            
            # Split file name from the path.
            path, file = os.path.split(full_file_name)
            
            # Get the star name from the filename, the name is at 
            # the beginning and separated by a special character.
            star_name = file.split(DATANAME_CHAR_SEP)[0]
            
        return star_name    
            
    def update_star_name(self, file_name, star_name):
        """Determines if the file specifies the name of the star in the header,
        if not, the header is updated with this name.
        
        Args:
            file_name: The name of the file to update.
            star_name: The name of the star to set.
        """
        
        try:
            # Open FIT file.
            hdulist = pyfits.open(file_name, mode='update')
            
            # Get header of first hdu, only the first hdu is processed.
            header = hdulist[0].header
            
            # Update, in the header of first hdu, the field for the name of 
            # the object.
            hdulist[0].header[self._header_fields.object] = star_name
            
            # Changes are written back to the original file.
            hdulist.flush()
            
            hdulist.close()   
            
        except IOError as ioe:
            logging.error("Error updating fit file '%s'. Error is: %s." % 
                          (file_name, ioe))            
        
    def update_image_type(self, file_name, file_header):
        """ Try to fill the image type from the name of the file using the
        convention used in OSN (Observatorio de Sierra Nevada).
        
        Args:     
            path: Path where is the file.         
            filename: Name of the file to analyze.
            
        Returns:
            The header updated if possible, otherwise None.
        
        """
        
        # Take only the part that indicates the type.
        type_part = file_name[:file_name.find(DATANAME_CHAR_SEP)].upper()
         
        if type_part == self._header_fields.bias_value:
            
            file_header[self._header_fields.image_type] = \
                self._header_fields.bias_value
                
        elif type_part == self._header_fields.flat_value:   
             
            file_header[self._header_fields.image_type] = \
                self._header_fields.flat_value
                            
        elif type_part in self._stars.star_names:
            
            file_header[self._header_fields.image_type] = \
                self._header_fields.light_value
                
        else:
            file_header = None
            
        return file_header

    def analyze_and_copy_file(self, path, filename):
        """Establish the type of the file and copies it to the appropriate 
        directory. 
        
        This function determines the file type and moves the
        files to the proper directory created for that type of file.
        
        First it is to establish the type of each file looking at the file
        header.
        
        Args:     
            path: Path where is the file.         
            filename: Name of the file to analyze.  	
        """
        
        file_destination = None
        
        star_name = None
        
        # Some file names have suffixes delimited by dots that will be ignored 
        # to save the destiny file.    
        destiny_filename = remove_prefixes(filename)            
    
        full_file_name = os.path.join(path, filename)
    
        # Get the headers of the file.  
        file_header = get_fit_fields(full_file_name, 
                                     self._header_fields.header_fields_names)
        
        # Check if there is a value in the image type,
        # and update it if possible.
        if not self._header_fields.image_type in file_header:
            file_header = self.update_image_type(destiny_filename, file_header)
    
        if file_header is not None:
            
            images_dir = os.path.split(path)[-1]
            
            target_dir = os.path.join(self._progargs.target_dir, images_dir)
    
            # If the file is a bias.
            if file_header[self._header_fields.image_type].strip() == \
                    self._header_fields.bias_value:
                
                logging.debug("%s identified as bias." % (full_file_name))                
                
                bias_dir = os.path.join(target_dir,
                                        self._progargs.bias_directory)
                
                self.create_directory(bias_dir)
        
                file_destination = os.path.join(bias_dir, destiny_filename)
        
            # If the file is a flat.
            elif file_header[self._header_fields.image_type].strip() == \
                    self._header_fields.flat_value:
                
                logging.debug("%s identified as flat." % (full_file_name))
                
                filter_name = file_header[self._header_fields.filter]
                
                # Check that the filter of the image is one of the specified.
                if filter_name in self._filters:
                
                    flat_dir = os.path.join(target_dir,
                                            self._progargs.flat_directory,
                                            filter_name)
                                
                    self.create_directory(flat_dir)
            
                    file_destination = os.path.join(flat_dir, destiny_filename)
        
            # Otherwise the file is considered a light image.
            else:
                logging.debug("%s identified as data image." % (full_file_name))
                
                star_name = self.get_star_name(destiny_filename, file_header)
                
                if self._stars.has_star(star_name):
            
                    filter_name = file_header[self._header_fields.filter]
                    
                    # Check that the filter of the image is one of the specified.        
                    if filter_name in self._filters:
                        
                        data_dir = os.path.join(target_dir,
                                                self._progargs.light_directory,
                                                filter_name)
                            
                        self.create_directory(data_dir)
                
                        # Prefixes are removed from file name.
                        file_destination = os.path.join(data_dir, 
                                                        destiny_filename)
                else:
                    logging.warning("Star '%s' isn't in the list of stars." %
                                    (star_name))
        else:
            logging.debug("Image type undefined for file '%s', discarded."
                          % (full_file_name))
    
        # Determines if the file must be copied.
        if file_destination is not None:
            
            logging.debug("Copying '%s' to '%s'" % 
                          (full_file_name, file_destination))
    
            shutil.copy(os.path.abspath(full_file_name),
                        os.path.abspath(file_destination))
            
            # Update the name of the star in header of the file if necessary.
            if star_name is not None:
                self.update_star_name(file_destination, star_name)
            
    def ignore_current_directory(self, dir):
        """ Determines if current directory should be ignored.
        
        A directory whose name matches that of bias, flat or data directories or
        has a parent directory named as a flat or data directory is ignored, 
        as this directory could be a directory created in a previous run and a new
        bias/flat/data and redundant directory should be created for it.
        
        Args:
            dir: Directory to process. 
            
        Returns:
            True if directory must be ignored, False otherwise.
        
        """
        ignore  = False
        
        # Get the names of the current and parent directory.
        head, current_directory = os.path.split(dir)
        rest, parent_directrory = os.path.split(head)
        
        # Check if current directory corresponds to a directory already organized.
        if current_directory == self._progargs.bias_directory or \
            current_directory == self._progargs.flat_directory or \
            parent_directrory == self._progargs.flat_directory or \
            current_directory == self._progargs.light_directory or \
            parent_directrory == self._progargs.light_directory:
            ignore  = True
        
        return ignore  

    def get_binnings_of_images(self, data_path):
        """Returns the binnings used for the images in the path indicated.
        
        Args:    
            data_path: Directory with full path with images to analyze.
        
        Returns:
            The list of binning used for the data images in the directory indicated.
        
        """
        
        binnings = []
        
        # Walk from current directory.
        for path, dirs, files in os.walk(data_path):
    
            # Inspect only directories without subdirectories.
            if len(dirs) == 0:
                
                # Get the binning of each file in the directory.
                for f in files:
                    path_file = os.path.join(path,f)
                    
                    bin = fitfiles.get_file_binning(path_file)
        
                # If the binning has been read.
                if bin is not None:
                    # If this binning has not been found yet, add it.
                    if not bin in binnings:
                        binnings.extend([bin])
                        
        if len(binnings) > 1:
            logging.warning("Images with different %s binning in '%s'" %
                            (binnings, data_path))
                
        return binnings
    
    def remove_images_with_diff_binning(self, data_path, binnings):
        """Remove images with a binning not included in the binnings received.
        
        Args:    
            data_path: Path that contains the images to analyze.
            binnings: List of binnings to consider.
        
        """
        
        # Walk from current directory.
        for path, dirs, files in os.walk(data_path):
    
            # Inspect only directories without subdirectories.
            if len(dirs) == 0:
                
                # Get the binning of each file in the directory.
                for f in files:
                    path_file = os.path.join(path,f)
                    
                    bin = fitfiles.get_file_binning(path_file)
        
                    # If the binning has been read.
                    if bin is not None:
                        # If this binning has not been in the list of binnings,
                        # remove the image.
                        if not bin in binnings:
                            logging.debug("Removing file '%s' with binning %s not used" % 
                                          (path_file, bin))
                                                    
                            os.remove(path_file) 
                    else:
                        logging.warning("Binning not read for: %s" % (path_file))  
    
    def remove_dir_if_empty(self, source_path):
        """Check if the directory is empty and in that case is removed.
        
        Args:    
            source_path: Path to analyze.
            
        """
        
        # If current directory is empty, remove it.
        if os.listdir(source_path) == []:
            logging.debug("Removing empty directory: '%s'" % (source_path))
            
            try:
                os.rmdir(source_path)
                
            except OSError as oe:
                logging.error("Removing directory: '%s'" % (source_path))
                logging.error("Error is: %s" % (oe))
        else:        
            # Walk from current directory.
            for path, dirs, files in os.walk(source_path):
        
                # Iterate over the directories.
                for d in dirs:
                    self.remove_dir_if_empty(os.path.join(path,d))
    
    def remove_images_according_to_binning(self, path):
        """Remove bias and flat whose binning doesn't match that of the data 
        images.
        
        Analyzes the binning of the bias and flat images and remove those whose 
        binning does not match that of the data images.
        
        Args: 
            path: Path where the analysis of the images should be done.
            
        """
        
        data_path = os.path.join(path, self._progargs.light_directory)
        
        # If current path has data directory, process bias and flats
        if os.path.exists(data_path):
        
            logging.debug("Removing bias and flats with a binning not needed in: %s" % 
                          (path))
            
            # Get the binning of images in data directory.
            binnings = self.get_binnings_of_images(data_path)
            
            # Remove images in bias directory with different binning of that of 
            # images.
            bias_path = os.path.join(path, self._progargs.bias_directory)
            
            if os.path.exists(bias_path):
                self.remove_images_with_diff_binning(bias_path, binnings)
                
                # If now bias directory is empty is removed.
                self.remove_dir_if_empty(bias_path)
                    
            # Remove images in flat directory with different binning of that of 
            # images.
            flat_path = os.path.join(path, self._progargs.flat_directory)
            
            if os.path.exists(flat_path):
                self.remove_images_with_diff_binning(flat_path, binnings)   
                
                # If now flat directory is empty is removed.
                self.remove_dir_if_empty(flat_path)
            
    def process_directories(self):
        """This function walks the directories searching for image files,
        when a directory with image files is found the directory contents
        are analyzed and organized.
        
        """          
        
        # Walk from source directory.
        for path, dirs, files in os.walk(self._progargs.source_dir):
            
            # Inspect only directories without subdirectories.
            if len(dirs) == 0:       
                 
                # Check if current directory was created previously
                # to contain bias, flat or light, in that case the directory 
                # is ignored.        
                if self.ignore_current_directory(path):
                    logging.debug("Ignoring directory '%s', already organized."
                                  % (path))
                else:
                    # For each file move it to he proper directory.
                    for fn in files:
                        # The extension is the final string of the list 
                        # without the initial dot.
                        filext = os.path.splitext(fn)[-1][1:]
            
                        if filext == FIT_FILE_EXT:
                            
                            logging.debug("Analyzing: %s" %
                                          (os.path.join(path, fn)))
                            
                            self.analyze_and_copy_file(path, fn)
                        else:
                            logging.debug("Ignoring file: %s" % (fn))

            # Check the directory to remove bias and flat
            # with a different binning of data images.
            self.remove_images_according_to_binning(path)      

def organize_files(progargs, stars, header_fields, filters):
    """Get the data necessary to process files and initiates the search of 
    FIT files in directories to organize them.
        
    Args:    
        progargs: Program arguments.  
        stars: The list of stars.
        header_fields: Information about the headers.        
        filters: Filters to use.
        
    """
            
    org = OrganizeFIT(progargs, stars, header_fields, filters)
    
    org.process_directories()