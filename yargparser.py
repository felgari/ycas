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

"""
This module process the program arguments received by main function.
Define the arguments available, check for its correctness, and provides 
these arguments to other modules. 
"""

import argparse
import logging
from constants import *

class ProgramArguments(object):
    """ Encapsulates the definition and processing of program arguments.
        
    """
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ProgramArguments 
        with the definition of arguments to use.

        """   
        
        self.__bias_directory = BIAS_DIRECTORY
        self.__flat_directory = FLAT_DIRECTORY
        self.__data_directory = DATA_DIRECTORY      
        
        self.__astrometry_num_of_objects = ASTROMETRY_NUM_OBJS          

            
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-b", dest="b", metavar="bias", \
                                   help='Name for the destiny directory name where the bias images are stored')
        
        self.__parser.add_argument("-f", dest="f", metavar="flat", \
                                   help="Name for the destiny directory name where the flat images are stored")
        
        self.__parser.add_argument("-d", dest="d", metavar="data", \
                                   help="Name for the destiny directory name where the data images are stored")
        
        self.__parser.add_argument("-no", dest="no", metavar="number of objects", type=int, \
                                   help="Number of objects to take into account in images when doing astrometry")        
                
        self.__parser.add_argument("-l", metavar="log file name", dest="l", \
                                   help="File to save the log messages") 
        
        self.__parser.add_argument("-v", metavar="log level", dest="v", \
                                   help="Level of the log messages to generate")         
        
        self.__parser.add_argument("-o", dest="o", action="store_true", \
                                   help="Organize the images")                
        
        self.__parser.add_argument("-r", dest="r", action="store_true", \
                                   help="Reduce the images")       
        
        self.__parser.add_argument("-s", dest="s", action="store_true",  
                                   help="Calculate the astrometry")  
        
        self.__parser.add_argument("-a", dest="a", action="store_true", \
                                   help="Align the images")   
        
        self.__parser.add_argument("-p", dest="p", action="store_true", 
                                   help="Calculate the photometry of the images")       
        
        self.__parser.add_argument("-m", dest="m", action="store_true", 
                                   help="Calculate the magnitudes of the images")                 
        
        self.__args = None    
        
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
    def number_of_objects_for_astrometry(self):        
        return self.__astrometry_num_of_objects
    
    @property    
    def log_file_provided(self): 
        return self.__args.l <> None      
    
    @property
    def log_file_name(self):
        return self.__args.l 

    @property    
    def log_level_provided(self): 
        return self.__args.v <> None     
    
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
        return self.__args.s  
    
    @property
    def align_requested(self):
        return self.__args.a 
    
    @property
    def photometry_requested(self):
        return self.__args.p  
    
    @property
    def magnitudes_requested(self):
        return self.__args.m      
    
    def parse(self):
        """ Parse program arguments.
        
        Performs the parsing of program arguments using the
        'ArgumentParser' object created.
        
        """
        
        self.__args = self.__parser.parse_args()
            
        if self.__args.b <> None:
            self.__bias_directory = self.__args.b
            
        if self.__args.f <> None:
            self.__flat_directory = self.__args.f
            
        if self.__args.d <> None:
            self.__data_directory = self.__args.d
            
        if self.__args.no <> None:
            self.__astrometry_num_of_objects = self.__args.no
     