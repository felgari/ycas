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

"""Process the program arguments received by main function.

Define the arguments available, check for its correctness and coherence, 
and provides these arguments to other modules. 
"""

import os
import argparse
import logging
from constants import *

class ProgramArgumentsException(Exception):
    
    def __init__(self, msg):
        
        self._msg = msg
        
    def __str__(self):
        return self._msg

class ProgramArguments(object):
    """ Encapsulates the definition and processing of program arguments. """
    
    # Default number of objects to look at when doing astrometry.
    ASTROMETRY_NUM_OBJS = 20
    
    # Default named of the directories containing different types of files.
    BIAS_DIRECTORY = 'bias'
    DARK_DIRECTORY = 'dark' 
    FLAT_DIRECTORY = 'flat'
    LIGHT_DIRECTORY = 'light'    
    
    # Error messages related to parameters coherence.
    NO_PIPELINE_STEPS_INDICATED = "At least one pipeline step should be " + \
        "indicated."           
        
    SEXTRACTOR_PATH_REQUIRED = "The path for sextractor must be supplied."
        
    FILTERS_PARAM_REQUIRED = "A configuration file specifying the filters " + \
        "must be supplied."
        
    HEADER_PARAM_REQUIRED = "A configuration file for FIT headers must be " + \
        "supplied."
        
    STARS_FILE_REQUIRED = "A file with the information of the stars " + \
        "must be supplied."
        
    PHOT_REQUIRES_PHOT_PARAMETERS = "Photometry requires the specification " + \
        "of a file containing the parameters for phot." 
        
    PHOT_REQUIRES_INST_CHARACTERISTICS = "Photometry requires the " + \
        "specification of a file containing characteristics of the instrument."  
        
    SOURCE_DIR_REQUIRED = "The source directory with the files must be supplied."   
    
    SOURCE_DIR_MUST_EXISTS = "The source directory supplied does not exist."     
    
    TARGET_DIR_REQUIRED = "The target directory of the files must be supplied."
    
    ERROR_CREATING_TARGET_DIR = "The target directory cannot be created."               
        
    # Name of the file that contains information about the stars of interest.
    STARS_FILE_NAME = "stars.csv"        
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ProgramArguments 
        with the definition of arguments to use.

        """   
        
        self.__min_number_of_args = 1
        
        # Initializes variables with default values.        
        self.__bias_directory = ProgramArguments.BIAS_DIRECTORY
        self.__dark_directory = ProgramArguments.DARK_DIRECTORY
        self.__flat_directory = ProgramArguments.FLAT_DIRECTORY
        self.__light_directory = ProgramArguments.LIGHT_DIRECTORY      
        
        self.__sextractor_cfg_path = os.getcwd()
        
        self.__astrometry_num_of_objects = ProgramArguments.ASTROMETRY_NUM_OBJS
        
        self.__stars_file_name = self.STARS_FILE_NAME       
            
        # Initialize arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-all", dest="all", action="store_true",
                                   help="Perform sequentially all the steps.")           
        
        self.__parser.add_argument("-o", dest="o", action="store_true",
                                   help="Organize the images.")                
        
        self.__parser.add_argument("-r", dest="r", action="store_true",
                                   help="Reduce the images.")       
        
        self.__parser.add_argument("-a", dest="a", action="store_true",  
                                   help="Calculate the astrometry.")         
        
        self.__parser.add_argument("-p", dest="p", action="store_true", 
                                   help="Calculate the photometry.")   
        
        self.__parser.add_argument("-m", dest="m", action="store_true", 
                                   help="Calculate the magnitudes of stars.")
        
        self.__parser.add_argument("-g", dest="g", action="store_true", 
                                   help="Graphics of light curves.")        
        
        self.__parser.add_argument("-sum", dest="sum", action="store_true", 
                                   help="Generates a summary of the results.")
        
        self.__parser.add_argument("-stars", metavar="stars_file",
                                   dest="stars",
                                   help="File of the stars to analyze.")    
        
        self.__parser.add_argument("-syn", metavar="synonym_file", dest="syn",
                                   help="File with the synomyms for the names of the stars.")          
        
        self.__parser.add_argument("-ins", metavar="instrument_file",
                                   dest="ins",
                                   help="File with features of the instrument.")
        
        self.__parser.add_argument("-pp", metavar="phot_param_file",
                                   dest="pp",
                                   help="File with parameters for phot.")   
        
        self.__parser.add_argument("-filters", metavar="filters_file",
                                   dest="filters",
                                   help="Name of the file with the filters " + 
                                   "to take into account.")           
        
        self.__parser.add_argument("-fh", metavar="fit_headers_file",
                                   dest="fh",
                                   help="File with parameters for FIT headers.")                                
        
        self.__parser.add_argument("-bias", dest="bias", metavar="bias_dir_name",
                                   help="Name of the directory for bias.")
        
        self.__parser.add_argument("-flat", dest="flat", metavar="flat_dir_name",
                                   help="Name of the directory for flat.")
        
        self.__parser.add_argument("-dark", dest="dark", metavar="dark_dir_name",
                                   help="Name of the directory for dark.")          
        
        self.__parser.add_argument("-light", dest="light", 
                                   metavar="light_dir_name",
                                   help="Name of the directory for light images.")        
        
        self.__parser.add_argument("-sd", metavar="source_dir",
                                   dest="sd",
                                   help="Source directory of the files.")  
        
        self.__parser.add_argument("-td", metavar="target_dir",
                                   dest="td",
                                   help="Target directory of the files.")                  
                
        self.__parser.add_argument("-l", metavar="log_file", dest="l",
                                   help="File to save the log messages.") 
        
        self.__parser.add_argument("-v", metavar="log_level", dest="v",
                                   help="Level of the log to generate.")                  
        
        self.__parser.add_argument("-x", dest="x", metavar="sex_cfg_path",
                                   help="Configuration directory of sextractor.")        
        
        self.__parser.add_argument("-no", dest="no",
                                   metavar="number_of_objects", type=int,
                                   help="Number of objects to use when " +
                                   "doing astrometry.")   
        
        self.__parser.add_argument("-us", dest="us", action="store_true",  
                                   help="Use sextractor for astrometry.")                                              
        
        self.__args = None   
        
    @property
    def min_number_args(self):
        return self.__min_number_of_args
        
    @property    
    def bias_directory(self):        
        return self.__bias_directory
    
    @property     
    def dark_directory(self):        
        return self.__dark_directory    
    
    @property     
    def flat_directory(self):        
        return self.__flat_directory
    
    @property     
    def light_directory(self):        
        return self.__light_directory
    
    @property     
    def sextractor_cfg_path(self):        
        return self.__sextractor_cfg_path    
         
    @property          
    def number_of_objects_for_astrometry(self):        
        return self.__astrometry_num_of_objects
    
    @property    
    def log_file_provided(self): 
        return self.__args.l is not None      
    
    @property
    def log_file_name(self):
        return self.__args.l 
    
    @property    
    def file_of_stars_provided(self): 
        return self.__args.stars is not None      
    
    @property
    def stars_file_name(self):
        return self.__stars_file_name  
    
    @property    
    def file_of_instrument_provided(self): 
        return self.__args.ins is not None      
    
    @property
    def intrument_file_name(self):
        return self.__args.ins   
    
    @property    
    def file_of_phot_params_provided(self): 
        return self.__args.pp is not None      
    
    @property
    def phot_params_file_name(self):
        return self.__args.pp  
    
    @property    
    def file_of_header_params_provided(self): 
        return self.__args.fh is not None      
    
    @property
    def header_params_file_name(self):
        return self.__args.fh      
    
    @property
    def file_of_filters_provided(self):
        return self.__args.filters is not None   
    
    @property
    def filters_file_name(self):
        return self.__args.filters      
    
    @property
    def sextractor_cfg_file_provided(self):
        return self.__args.x is not None

    @property
    def log_level_provided(self): 
        return self.__args.v is not None     
    
    @property
    def log_level(self):
        return self.__args.v     
        
    @property
    def file_of_synonym_provided(self):
        return self.__args.syn is not None   
    
    @property
    def synonym_file_name(self):
        return self.__args.syn    

    @property
    def source_dir_provided(self): 
        return self.__args.sd is not None     
    
    @property
    def source_dir(self):
        return self.__args.sd   
    
    @property
    def target_dir_provided(self): 
        return self.__args.td is not None     
    
    @property
    def target_dir(self):
        return self.__args.td
        
    @property
    def use_sextractor_for_astrometry(self):
        return self.__args.us      
    
    @property
    def organization_requested(self):
        return self.__args.o         
    
    @property
    def reduction_requested(self):
        return self.__args.r  
    
    @property
    def astrometry_requested(self):
        return self.__args.a    
    
    @property
    def photometry_requested(self):
        return self.__args.p     
    
    @property
    def magnitudes_requested(self):
        return self.__args.m
    
    @property
    def light_curves_requested(self):
        return self.__args.g           
    
    @property
    def summary_requested(self):
        return self.__args.sum 
    
    @property
    def all_steps_requested(self):
        return self.__args.all   
    
    def parse_and_update(self):
        """Parse the program arguments and update attributes."""

        try:
            # Parse program arguments.        
            self.__args = self.__parser.parse_args()        

            # Update variables if a program argument has been received
            # for their value.
            if self.__args.bias is not None:
                self.__bias_directory = self.__args.bias

            if self.__args.dark is not None:
                self.__bias_directory = self.__args.dark                   
                
            if self.__args.flat is not None:
                self.__flat_directory = self.__args.flat
                
            if self.__args.light is not None:
                self.__light_directory = self.__args.light
                
            if self.sextractor_cfg_file_provided:
                self.__sextractor_cfg_path = self.__args.x
                
            if self.file_of_stars_provided:
                self.__stars_file_name = self.__args.stars  
                
            if self.__args.no is not None:
                self.__astrometry_num_of_objects = self.__args.no 
            
        except argparse.ArgumentError as ae:
            print ae.message
            raise ProgramArgumentsException(ae.message)                         
            
    def check_arguments_coherence(self):
        """Check the coherence of program arguments received."""
        
        # Check that at least a pipeline step has been requested.
        if not self.organization_requested and \
            not self.reduction_requested and \
            not self.astrometry_requested and \
            not self.photometry_requested and \
            not self.magnitudes_requested and \
            not self.all_steps_requested and \
            not self.summary_requested:
            raise ProgramArgumentsException(ProgramArguments.NO_PIPELINE_STEPS_REQUESTED)        
        
        # Check all the conditions required for the program arguments.        
        if self.use_sextractor_for_astrometry and \
            not self.sextractor_cfg_file_provided:
            raise ProgramArgumentsException(ProgramArguments.SEXTRACTOR_PATH_REQUIRED)
            
        # Check the specification of the all the parameters needed for the
        # photometry.
        if self.photometry_requested or self.all_steps_requested:
            if not self.file_of_stars_provided:
                raise ProgramArgumentsException(ProgramArguments.STARS_FILE_REQUIRED)
            
            if not self.file_of_phot_params_provided:
                raise ProgramArgumentsException(ProgramArguments.PHOT_REQUIRES_PHOT_PARAMETERS)
            
            if not self.file_of_instrument_provided:
                raise ProgramArgumentsException(ProgramArguments.PHOT_REQUIRES_INST_CHARACTERISTICS)
            
            if not self.sextractor_cfg_file_provided:
                raise ProgramArgumentsException(ProgramArguments.SEXTRACTOR_PATH_REQUIRED)        

        # Check coherence for other steps.
        
        if self.organization_requested or self.all_steps_requested:
            if not self.file_of_stars_provided:
                raise ProgramArgumentsException(ProgramArguments.STARS_FILE_REQUIRED)
                                                            
            if not self.file_of_filters_provided:
                raise ProgramArgumentsException(ProgramArguments.FILTERS_PARAM_REQUIRED) 
        
            if not self.file_of_header_params_provided:
                raise ProgramArgumentsException(ProgramArguments.HEADER_PARAM_REQUIRED) 
            
            if not self.source_dir_provided:
                raise ProgramArgumentsException(ProgramArguments.SOURCE_DIR_REQUIRED)
            elif not os.path.exists(self.source_dir):
                raise ProgramArgumentsException(ProgramArguments.SOURCE_DIR_MUST_EXISTS)                  
        
        if self.astrometry_requested or self.all_steps_requested:
            if not self.file_of_stars_provided:
                raise ProgramArgumentsException(ProgramArguments.STARS_FILE_REQUIRED)            
        
        if self.magnitudes_requested or self.all_steps_requested:
            if not self.file_of_stars_provided:
                raise ProgramArgumentsException(ProgramArguments.STARS_FILE_REQUIRED)
        
        if self.light_curves_requested or self.all_steps_requested:
            if not self.stars_file_name:
                raise ProgramArgumentsException(ProgramArguments.STARS_FILE_REQUIRED)
        
        if not self.target_dir_provided:
            raise ProgramArgumentsException(ProgramArguments.TARGET_DIR_REQUIRED)
        elif not os.path.exists(self.target_dir):     
            try: 
                logging.debug("Creating target directory: %s" % 
                              (self.target_dir))
                os.makedirs(self.target_dir)
                
            except OSError:            
                logging.error("Target directory cannot be created: %s" %
                              (self.target_dir))
                
                raise ProgramArgumentsException(ProgramArguments.ERROR_CREATING_TARGET_DIR)
                
    def process_program_arguments(self):
        """Parse and check coherence of program arguments."""      

        self.parse_and_update()

        self.check_arguments_coherence()
 
    def print_usage(self):
        """Print arguments options """
                
        self.__parser.print_usage()     
        
    def print_help(self):
        """Print help for arguments options """
                
        self.__parser.print_help()     