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

Define the arguments available, check for its correctness, and provides 
these arguments to other modules. 
"""

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
    
    PHOT_REQUIRES_SEX_PATH = "Photometry requires the specification of " + \
        "a path for sextractor configuration files."
        
    PHOT_REQUIRES_STARS_FILE = "Photometry requires the specification " + \
        "of a file containing the data of the stars." 

    PHOT_REQUIRES_SEX_PATH_AND_STARS_FILE = "Photometry requires the " + \
        "specification of a path for sextractor configuration files and " + \
        "also the file containing the data of the stars." 
    
    USE_SEX_REQUIRES_SEX_PATH = "The use of sextractor requires the " + \
        "specification of a path for sextractor configuration files."
        
    ASTRO_REQUIRES_STARS_FILE = "Astrometry requires the specification " + \
        "of a file containing the data of the stars."    
        
    MAG_REQUIRES_STARS_FILE = "Calculation of magnitudes  requires the " + \
        "specification of a file containing the data of the stars."  
        
    NO_PIPELINE_STEPS_INDICATED = "At least one pipeline step should be " + \
        "indicated."
        
    # Name of the file that contains information about the stars of interest.
    STARS_FILE_NAME = "stars.csv"        
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ProgramArguments 
        with the definition of arguments to use.

        """   
        
        self.__min_number_of_args = 1
        
        # Initializes variables with default values.        
        self.__bias_directory = BIAS_DIRECTORY
        self.__flat_directory = FLAT_DIRECTORY
        self.__data_directory = DATA_DIRECTORY      
        
        self.__sextractor_cfg_path = os.getcwd()
        
        self.__astrometry_num_of_objects = ASTROMETRY_NUM_OBJS
        
        self.__stars_file_name = STARS_FILE_NAME  
            
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-all", dest="all", action="store_true", \
                                   help="Perform sequentially all the " + \
                                   "steps of the pipeline.")           
        
        self.__parser.add_argument("-o", dest="o", action="store_true", \
                                   help="Organize the images.")                
        
        self.__parser.add_argument("-r", dest="r", action="store_true", \
                                   help="Reduce the images.")       
        
        self.__parser.add_argument("-a", dest="a", action="store_true",  
                                   help="Calculate the astrometry.")         
        
        self.__parser.add_argument("-p", dest="p", action="store_true", 
                                   help="Calculate the photometry of the " + \
                                   "images.")   
        
        self.__parser.add_argument("-dp", dest="dp", action="store_true", 
                                   help="Calculate diferential photometry " + \
                                   "of the images.")
        
        self.__parser.add_argument("-m", dest="m", action="store_true", 
                                   help="Calculate the magnitudes of " + \
                                   "the stars o interest.")  
        
        self.__parser.add_argument("-s", metavar="stars_file_name",
                                   dest="s", \
                                   help="File that contains the names and " + \
                                   "coordinates of the stars od interest.")                 
        
        self.__parser.add_argument("-b", dest="b", metavar="bias_dir_name", \
                                   help="Name for the directory where " + \
                                   "the bias images are stored.")
        
        self.__parser.add_argument("-f", dest="f", metavar="flat_dir_name", \
                                   help="Name for the directory where " + \
                                   "the flat images are stored.")
        
        self.__parser.add_argument("-d", dest="d", metavar="data_dir_name", \
                                   help="Name for the directory where " + \
                                   "the data images are stored.")
        
        self.__parser.add_argument("-l", metavar="log_file_name", dest="l", \
                                   help="File to save the log messages.") 
        
        self.__parser.add_argument("-v", metavar="log_level", dest="v", \
                                   help="Level of the log to generate.")                  
        
        self.__parser.add_argument("-x", dest="x", metavar="sex_cfg_path", \
                                   help="Name for directory where the " + \
                                   "configuration files for sextractor are.")        
        
        self.__parser.add_argument("-no", dest="no", \
                                   metavar="number_of_objects", type=int, \
                                   help="Number of objects to take into " + \
                                   "account in images when doing astrometry.")   
        
        self.__parser.add_argument("-us", dest="us", action="store_true",  
                                   help="Use sextractor to calculate the " + \
                                   "astrometry.")                   
        
        self.__parser.add_argument("-t", dest="t", action="store_true", 
                                   help="Use header information to get " + \
                                   "the type of the image.")                     
        
        self.__args = None   
        
    @property
    def min_number_args(self):
        return self.__min_number_of_args
        
    @property    
    def bias_directory(self):        
        return self.__bias_directory
    
    @property     
    def flat_directory(self):        
        return self.__flat_directory
    
    @property     
    def data_directory(self):        
        return self.__data_directory
    
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
        return self.__args.s is not None      
    
    @property
    def stars_file_name(self):
        return self.__stars_file_name  
    
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
    def organization_requested(self):
        return self.__args.o         
    
    @property
    def reduction_requested(self):
        return self.__args.r  
    
    @property
    def astrometry_requested(self):
        return self.__args.a  
        
    @property
    def use_sextractor_for_astrometry(self):
        return self.__args.us      
    
    @property
    def photometry_requested(self):
        return self.__args.p  
    
    @property
    def diff_photometry_requested(self):
        return self.__args.dp      
    
    @property
    def magnitudes_requested(self):
        return self.__args.m    
    
    @property    
    def use_headers_to_get_image_type(self):
        return self.__args.t    
    
    @property
    def all_steps_requested(self):
        return self.__args.all   
    
    def parse_and_update(self):
        """ Parse the program arguments and update attributes.
        
        """
        
        # Parse program arguments.
        self.__args = self.__parser.parse_args()          
            
        # Update variables if a program argument has been received
        # for their value.
        if self.__args.b is not None:
            self.__bias_directory = self.__args.b
            
        if self.__args.f is not None:
            self.__flat_directory = self.__args.f
            
        if self.__args.d is not None:
            self.__data_directory = self.__args.d
            
        if self.sextractor_cfg_file_provided:
            self.__sextractor_cfg_path = self.__args.x
            
        if self.file_of_stars_provided:
            self.__stars_file_name = self.__args.s   
            
        if self.__args.no is not None:
            self.__astrometry_num_of_objects = self.__args.no            
            
    def check_arguments_coherence(self):
        """ Check the coherence of program arguments received.
        
        """
        
        # Check at least a pipeline step has been requested.
        if not self.organization_requested and \
            not self.reduction_requested and \
            not self.astrometry_requested and \
            not self.photometry_requested and \
            not self.magnitudes_requested and \
            not self.all_steps_requested:
            raise ProgramArgumentsException(NO_PIPELINE_STEPS_REQUESTED)
        
        # Check all the conditions required for the program arguments.
        
        if self.use_sextractor_for_astrometry and \
            not self.sextractor_cfg_file_provided:
            raise ProgramArgumentsException(self.USE_SEX_REQUIRES_SEX_PATH)
            
        # Check the specification of the file with the stars of interest.
        if self.photometry_requested:
            if not self.sextractor_cfg_file_provided:
                if not self.file_of_stars_provideds:
                    raise ProgramArgumentsException(PHOT_REQUIRES_SEX_PATH_AND_STARS_FILE)
                else:
                    raise ProgramArgumentsException(self.PHOT_REQUIRES_SEX_PATH)
            elif not self.file_of_stars_provided:
                raise ProgramArgumentsException(PHOT_REQUIRES_STARS_FILE)
            
        if self.astrometry_requested and not self.file_of_stars_provided:
            raise ProgramArgumentsException(ASTRO_REQUIRES_STARS_FILE)
        
        if self.magnitudes_requested and not self.file_of_stars_provided:
            raise ProgramArgumentsException(MAG_REQUIRES_STARS_FILE)
            
    def process_program_arguments(self):
        """ Parse and check coherence of program arguments.
        
        Parse the program arguments using the 'ArgumentParser' object created.
        
        """      
        
        self.parse_and_update()
      
        self.check_arguments_coherence()
            
    def print_usage(self):
        """ Print arguments options """
                
        self.__parser.print_usage()     
        
    def print_help(self):
        """ Print help for arguments options """
                
        self.__parser.print_help()           
     