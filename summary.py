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

"""This module get some summaries from a directory structure containing fit
images processed by ycas.

This module could be used as an independent program but also is used from ycas
to generate a final summary of the steps performed by the pipeline.
"""

import sys
import os
import logging
import argparse
from constants import *
from sumreport import *
import starsset

DEFAULT_DESTINY_FILE = "ycas_sum.txt"

def generate_summary(progargs, stars, stars_mag):
    """ Generates a summary for the tasks performed by the pipeline.
    
    Args:
        progargs: The program arguments.
        stars: List of stars.
        stars_mag: The magnitudes calculated.
        
    """    
    
    # Object that generates the summary.     
    sum_report = SummaryReport(DEFAULT_DESTINY_FILE, stars, stars_mag)     
    
    if progargs.all_steps_requested: 
        sum_report.enable_all_summary_task()

    else:    
        if progargs.organization_requested:
            sum_report.enable_organization_summary
    
        if progargs.reduction_requested:
            sum_report.enable_reduction_summary
            
        if progargs.astrometry_requested:
            sum_report.enable_astrometry_summary   
            
        if progargs.photometry_requested:
            sum_report.enable_photometry_summary
            
        if progargs.magnitudes_requested:
            sum_report.enable_magnitude_summary

    try:
        sum_report.generate_summary()
    except SummaryException as se:
        logging.error(se)   

        
        
class SummaryArguments(object):
    """ Encapsulates the definition and processing of program arguments for
        summaries as an independent program.
        
    """
    
    MIN_NUM_ARGVS = 1    
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
        
        self.__parser.add_argument("-a", dest="a", action="store_true", \
                                   help="Get summaries for astrometry.")   
        
        self.__parser.add_argument("-p", dest="p", action="store_true", \
                                   help="Get summaries for photometry.") 
        
        self.__parser.add_argument("-m", dest="m", action="store_true", \
                                   help="Get summaries for magnitudes.") 
        
        self.__parser.add_argument("-l", metavar="log file name", dest="l", \
                                   help="File to save the log messages")
          
        self.__parser.add_argument("-s", metavar="stars_file_name",
                                   dest="s",
                                   help="File of the stars to analyze.")               
         
    @property
    def destiny_file_name(self):
        return self.__args.d  
    
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
    def summary_file_name(self):
        return self.__args.d         
    
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
        return self.__args.a 
    
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
            self.__args.d = DEFAULT_DESTINY_FILE 
            
        if self.__args.l is None:
            self.__args.l = SummaryArguments.DEFAULT_LOG_FILE_NAME  
            
        if self.file_of_stars_provided:
            self.__stars_file_name = self.__args.s              
            
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
            
def main(progargs):
    """ Determines the summaries to generate and call to generate them.
    
    Args: 
        progargs - Program arguments.
        
    """
    
    ret_val = 0
    
    # Process program arguments.
    progargs.parse()           
        
    # Initializes logging.
    init_log(progargs)  
    
    # If summary for magnitudes has been requested, check if the file with
    # information about the stars has been provided.
    if ( progargs.summary_magnitude or progargs.summary_all ) and \
        not progargs.file_of_stars_provided:
        logging.error("A file for stars must be specified to generate a" +
                      "summary for magnitudes.")
        ret_val = 1
        
    else:           
        # Object that generates the summary.     
        sum_report = SummaryReport(progargs.summary_file_name,
                                   progargs.stars_file_name, 
                                   None)
        
        # Set the summaries to generate.
        if progargs.summary_all:
            sum_report.enable_all_summary_task()
    
        else:
            if progargs.summary_organization:
                sum_report.enable_organization_summary
                
            if progargs.summary_reduction:
                sum_report.enable_reduction_summary
                
            if progargs.summary_astrometry:
                sum_report.enable_astrometry_summary   
                
            if progargs.summary_photometry:
                sum_report.enable_photometry_summary
                
            if progargs.summary_magnitude:
                sum_report.enable_magnitude_summary
    
        sum_report.generate_summary()
            
        if not sum_report.is_any_summary_task_enabled:
            progargs.print_help()                
    
    return ret_val
        
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