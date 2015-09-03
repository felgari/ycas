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
from constants import *
from textfiles import read_cfg_file

class ProgramArgumentsException(Exception):
    
    def __init__(self, msg):
        
        self._msg = msg
        
    def __str__(self):
        return self._msg

class ProgramArguments(object):
    """ Encapsulates the definition and processing of program arguments. """
    
    YES_VALUE = "YES"
    
    NO_VALUE = "NO"
    
    # Default values for some parameters.
    DEFAULT_LOG_FILE = "log.txt" 
    DEFAULT_LOG_LEVEL = "DEBUG"      
    
    # Default number of objects to look at when doing astrometry.
    DEFAULT_ASTROM_NUM_OBJS = 20
    
    # Default named of the directories containing different types of files.
    DEFAULT_BIAS_DIRECTORY = 'bias'
    DEFAULT_DARK_DIRECTORY = 'dark' 
    DEFAULT_FLAT_DIRECTORY = 'flat'
    DEFAULT_LIGHT_DIRECTORY = 'light'    
    
    # Names of the parameters in the configuration file.
    STARS_PAR_NAME = "STARS" 

    SYNONYMS_PAR_NAME = "SYNONYMS"

    PHOT_SETTINGS_PAR_NAME = "PHOT_SETTINGS"

    INSTRUMENT_SETTINGS_PAR_NAME = "INSTRUMENT_SETTINGS"

    FIT_HEADERS_PAR_NAME = "FIT_HEADERS"

    FILTERS_PAR_NAME = "FILTERS" 

    SOURCE_DIR_PAR_NAME = "SOURCE_DIR" 

    TARGET_DIR_PAR_NAME = "TARGET_DIR" 
    
    DARK_DIR_NAME_PAR_NAME = "DARK_DIR_NAME"    

    BIAS_DIR_NAME_PAR_NAME = "BIAS_DIR_NAME"

    FLAT_DIR_NAME_PAR_NAME = "FLAT_DIR_NAME"

    LIGHT_DIR_NAME_PAR_NAME = "LIGHT_DIR_NAME"

    NUM_OBJS_ASTROMETRY_PAR_NAME = "NUM_OBJS_ASTROMETRY"

    USE_SEXTRACTOR_PAR_NAME = "USE_SEXTRACTOR"

    SEXTRACTOR_PATH_PAR_NAME = "SEXTRACTOR_PATH"

    LOG_FILE_PAR_NAME = "LOG_FILE"

    LOG_LEVEL_PAR_NAME = "LOG_LEVEL"

    SUMMARY_PAR_NAME = "SUMMARY"
    
    # Error messages related to parameters coherence.
    NO_PIPELINE_STEPS_REQUESTED = "At least one pipeline step should be " + \
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

    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ProgramArguments 
        with the definition of arguments to use.

        """   
        
        # Initializes variables with default values.  
        self._stars_file = None
        self._stars_syn_file = None
        self._phot_settings_file = None
        self._inst_settings_file = None
        self._fit_headers_file = None
        self._filters_file = None
        self._source_dir = None
        self._target_dir = None              
        self._bias_directory = ProgramArguments.DEFAULT_BIAS_DIRECTORY
        self._dark_directory = ProgramArguments.DEFAULT_DARK_DIRECTORY
        self._flat_directory = ProgramArguments.DEFAULT_FLAT_DIRECTORY
        self._light_directory = ProgramArguments.DEFAULT_LIGHT_DIRECTORY 
        self._astrometry_num_of_objects = ProgramArguments.DEFAULT_ASTROM_NUM_OBJS
        self._use_sextractor = False
        self._sextractor_cfg_path = os.getcwd()
        self._log_file = ProgramArguments.DEFAULT_LOG_FILE
        self._log_level = ProgramArguments.DEFAULT_LOG_LEVEL
        self._generate_summary = False        
        
        self._min_number_of_args = 1             
                
        self._args = None   
        
        self._parser = None  
        
        self.init_parser()                                             
        
    @property
    def min_number_args(self):
        return self._min_number_of_args
        
    @property    
    def bias_directory(self):        
        return self._bias_directory
    
    @property     
    def dark_directory(self):        
        return self._dark_directory    
    
    @property     
    def flat_directory(self):        
        return self._flat_directory
    
    @property     
    def light_directory(self):        
        return self._light_directory
    
    @property     
    def sextractor_cfg_path(self):        
        return self._sextractor_cfg_path    
         
    @property          
    def number_of_objects_for_astrometry(self):        
        return self._astrometry_num_of_objects
    
    @property    
    def log_file_provided(self): 
        return self._log_file is not None 
    
    @property
    def log_file_name(self):
        return self._log_file
    
    @property    
    def file_of_stars_provided(self): 
        return self._stars_file is not None     
    
    @property
    def stars_file_name(self):
        return self._stars_file
    
    @property    
    def file_of_instrument_provided(self): 
        return self._inst_settings_file is not None      
    
    @property
    def intrument_file_name(self):
        return self._inst_settings_file 
    
    @property    
    def file_of_phot_params_provided(self): 
        return self._phot_settings_file is not None      
    
    @property
    def phot_params_file_name(self):
        return self._phot_settings_file 
    
    @property    
    def file_of_header_params_provided(self): 
        return self._fit_headers_file is not None      
    
    @property
    def header_params_file_name(self):
        return self._fit_headers_file      
    
    @property
    def file_of_filters_provided(self):
        return self._filters_file is not None   
    
    @property
    def filters_file_name(self):
        return self._filters_file     
    
    @property
    def sextractor_cfg_file_provided(self):
        return self._sextractor_cfg_path is not None

    @property
    def log_level_provided(self): 
        return self._log_level is not None     
    
    @property
    def log_level(self):
        return self._log_level     
        
    @property
    def file_of_synonym_provided(self):
        return self._stars_syn_file is not None   
    
    @property
    def synonym_file_name(self):
        return self._stars_syn_file    

    @property
    def source_dir_provided(self): 
        return self._source_dir is not None     
    
    @property
    def source_dir(self):
        return self._source_dir   
    
    @property
    def target_dir_provided(self): 
        return self._target_dir is not None     
    
    @property
    def target_dir(self):
        return self._target_dir
        
    @property
    def use_sextractor_for_astrometry(self):
        return self._use_sextractor      
    
    @property
    def organization_requested(self):
        return self._args.o         
    
    @property
    def reduction_requested(self):
        return self._args.r  
    
    @property
    def astrometry_requested(self):
        return self._args.a    
    
    @property
    def photometry_requested(self):
        return self._args.p     
    
    @property
    def magnitudes_requested(self):
        return self._args.m
    
    @property
    def light_curves_requested(self):
        return self._args.g           
    
    @property
    def summary_requested(self):
        return self._generate_summary
    
    @property
    def all_steps_requested(self):
        return self._args.all   
    
    def init_parser(self):
        """Initializes the ArgumentParser object."""
        
        self._parser = argparse.ArgumentParser()
        
        # Initialize arguments of the parser.        
        self._parser.add_argument("-cf", dest="cf", metavar="cfg_file", 
                                  help="Configuration file with the program options.")
        self._parser.add_argument("-all", dest="all", action="store_true", 
                                  help="Perform sequentially all the steps.")
        self._parser.add_argument("-o", dest="o", action="store_true", 
                                  help="Organize the images.")
        self._parser.add_argument("-r", dest="r", action="store_true", 
                                  help="Reduce the images.")
        self._parser.add_argument("-a", dest="a", action="store_true", 
                                  help="Calculate the astrometry.")
        self._parser.add_argument("-p", dest="p", action="store_true", 
                                  help="Calculate the photometry.")
        self._parser.add_argument("-m", dest="m", action="store_true", 
                                  help="Calculate the magnitudes of stars.")
        self._parser.add_argument("-g", dest="g", action="store_true", 
                                  help="Graphics of light curves.")
        self._parser.add_argument("-sum", dest="sum", action="store_true", 
                                  help="Generates a summary of the results.")
        self._parser.add_argument("-stars", metavar="stars_file", dest="stars", 
                                  help="File of the stars to analyze.")
        self._parser.add_argument("-syn", metavar="synonym_file", dest="syn", 
                                  help="File with the synomyms for the names of the stars.")
        self._parser.add_argument("-ins", metavar="instrument_file", dest="ins", 
                                  help="File with features of the instrument.")
        self._parser.add_argument("-pp", metavar="phot_param_file", dest="pp", 
                                  help="File with parameters for phot.")
        self._parser.add_argument("-filters", metavar="filters_file", 
                                  dest="filters", 
                                  help="Name of the file with the filters " + 
                                  "to take into account.")
        self._parser.add_argument("-fh", metavar="fit_headers_file", dest="fh", 
                                  help="File with parameters for FIT headers.")
        self._parser.add_argument("-bias", dest="bias", metavar="bias_dir_name", 
                                  help="Name of the directory for bias.")
        self._parser.add_argument("-flat", dest="flat", metavar="flat_dir_name", 
                                  help="Name of the directory for flat.")
        self._parser.add_argument("-dark", dest="dark", metavar="dark_dir_name", 
                                  help="Name of the directory for dark.")
        self._parser.add_argument("-light", dest="light", metavar="light_dir_name", 
                                  help="Name of the directory for light images.")
        self._parser.add_argument("-sd", metavar="source_dir", dest="sd", 
                                  help="Source directory of the files.")
        self._parser.add_argument("-td", metavar="target_dir", dest="td", 
                                  help="Target directory of the files.")
        self._parser.add_argument("-l", metavar="log_file", dest="l", 
                                  help="File to save the log messages.")
        self._parser.add_argument("-v", metavar="log_level", dest="v", 
                                  help="Level of the log to generate.")
        self._parser.add_argument("-x", dest="x", metavar="sex_cfg_path", 
                                  help="Configuration directory of sextractor.")
        self._parser.add_argument("-no", dest="no", metavar="number_of_objects", 
                                  type=int, help="Number of objects to use when " + 
                                  "doing astrometry.")
        self._parser.add_argument("-us", dest="us", action="store_true", 
                                  help="Use sextractor for astrometry.")    
    
    def load_configuration_parameters(self):
        """Load the values indicated in the configuration file."""
        
        params = read_cfg_file(self._args.cf)
        
        try:
            self._stars_file = params[ProgramArguments.STARS_PAR_NAME]
        except:
            print "Stars_file not supplied in configuration file." 

        try:
            self._stars_syn_file = params[ProgramArguments.SYNONYMS_PAR_NAME]
        except:
            print "synonyms file not supplied in configuration file." 
            
        try:
            self._phot_settings_file = params[ProgramArguments.PHOT_SETTINGS_PAR_NAME]
        except:
            print "phot parameters file not supplied in configuration file." 
            
        try:
            self._inst_settings_file = params[ProgramArguments.INSTRUMENT_SETTINGS_PAR_NAME]
        except:
            print "instrument settings file not supplied in configuration file." 
            
        try:
            self._fit_headers_file = params[ProgramArguments.FIT_HEADERS_PAR_NAME]
        except:
            print "fit headers file not supplied in configuration file." 
            
        try:
            self._filters_file = params[ProgramArguments.FILTERS_PAR_NAME]
        except:
            print "Filters file not supplied in configuration file." 
            
        try:
            self._source_dir = params[ProgramArguments.SOURCE_DIR_PAR_NAME]
        except:
            print "Source directory not supplied in configuration file." 
            
        try:
            self._target_dir = params[ProgramArguments.TARGET_DIR_PAR_NAME]
        except:
            print "Target directory not supplied in configuration file." 
            
        try:
            self._dark_directory = params[ProgramArguments.DARK_DIR_NAME_PAR_NAME]
        except:
            print "Dark directory name not supplied in configuration file."                                                                                      
                        
        try:
            self._bias_directory = params[ProgramArguments.BIAS_DIR_NAME_PAR_NAME]
        except:
            print "Bias directory name not supplied in configuration file."   

        try:
            self._flat_directory = params[ProgramArguments.FLAT_DIR_NAME_PAR_NAME]
        except:
            print "Flat directory name not supplied in configuration file."       

        try:
            self._light_directory = params[ProgramArguments.LIGHT_DIR_NAME_PAR_NAME]
        except:
            print "Light directory name not supplied in configuration file."       

        try:
            self._astrometry_num_of_objects = params[ProgramArguments.NUM_OBJS_ASTROMETRY_PAR_NAME]
        except:
            print "Number of objects for astrometry not supplied in configuration file."      

        try:
            val = params[ProgramArguments.USE_SEXTRACTOR_PAR_NAME]
            
            if val == ProgramArguments.YES_VALUE:                
                self._use_sextractor = True
            elif val == ProgramArguments.NO_VALUE:                
                self._use_sextractor = False
            else:
                print "Value for parameter %s is not valid: %s" % \
                    (ProgramArguments.USE_SEXTRACTOR_PAR_NAME, val)
        except:
            print "Use of sextractor not indicated in configuration file."      

        try:
            self._sextractor_cfg_path = params[ProgramArguments.SEXTRACTOR_PATH_PAR_NAME]
        except:
            print "Sextractor directory not supplied in configuration file."      

        try:
            self._log_file = params[ProgramArguments.LOG_FILE_PAR_NAME]
        except:
            print "Log file name not supplied in configuration file."     

        try:
            self._log_level = params[ProgramArguments.LOG_LEVEL_PAR_NAME]
        except:
            print "Debug level not supplied in configuration file."     

        try:
            val = params[ProgramArguments.SUMMARY_PAR_NAME]
            
            if val == ProgramArguments.YES_VALUE:                
                self._generate_summary = True
            elif val == ProgramArguments.NO_VALUE:                
                self._generate_summary = False
            else:
                print "Value for parameter %s is not valid: %s" % \
                    (ProgramArguments.SUMMARY_PAR_NAME, val)            
        except:
            print "Generation of summary not supplied in configuration file."     

    def parse_and_update(self):
        """Parse the program arguments and update attributes."""

        try:
            # Parse program arguments.        
            self._args = self._parser.parse_args()
            
            if self._args.cf is not None:
                print "Loading arguments from file: %s" % self._args.cf
                
                self.load_configuration_parameters()

            # Update variables if a program argument has been received
            # for their value. These values overwrite those supplied in the
            # configuration file, if any.
            if self._args.stars is not None:
                self._stars_file = self._args.stars              
            
            if self._args.syn is not None:
                self._stars_syn_file = self._args.syn
                
            if self._args.ins is not None:
                self._inst_settings_file = self._args.ins
            
            if self._args.pp is not None:
                self._phot_settings_file = self._args.pp
                
            if self._args.fh is not None:
                self._fit_headers_file = self._args.fh
                
            if self._args.filters is not None:
                self._filters_file = self._args.filters
                
            if self._args.sd is not None:
                self._source_dir = self._args.sd
                
            if self._args.td is not None:
                self._target_dir = self._args.td                
                
            if self._args.dark is not None:
                self._dark_directory = self._args.dark  
                
            if self._args.bias is not None:
                self._bias_directory = self._args.bias  
                
            if self._args.flat is not None:
                self._flat_directory = self._args.flat  
                
            if self._args.light is not None:
                self._light_directory = self._args.light                                                                  
            
            if self._args.no is not None:
                self._astrometry_num_of_objects = self._args.no  

            if self._args.us:
                self._use_sextractor = True
                
            if self._args.x is not None:
                self._sextractor_cfg_path = self._args.x 
                
            if self._args.l is not None:
                self._log_file = self._args.l 
                
            if self._args.v is not None:
                self._log_level = self._args.v 
                
            if self._args.sum:
                self._generate_summary = True          
            
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
                print "Creating target directory: %s" % self.target_dir
                os.makedirs(self.target_dir)
                
            except OSError:
                print "Target directory cannot be created: %s" % self.target_dir
                
                raise ProgramArgumentsException(ProgramArguments.ERROR_CREATING_TARGET_DIR)
                
    def process_program_arguments(self):
        """Parse and check coherence of program arguments."""     

        self.parse_and_update()

        self.check_arguments_coherence()
 
    def print_usage(self):
        """Print arguments options """
                
        self._parser.print_usage()     
        
    def print_help(self):
        """Print help for arguments options """
                
        self._parser.print_help()     