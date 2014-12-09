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

"""Calculates the magnitude of a group of objects in a sequence of steps.

The processing assumes certain values in the header of the fits images,
even in the names of the files. Also a list of objects of interest, 
whose magnitudes are calculated, and a list of standard stars.
Some characteristics of the CCD camera are also needed to calculate
the photometric magnitude of the objects.
"""

import sys
import logging
import yargparser
import orgfits
import reduce
import align
import astrometry
import photometry
import magnitude
from constants import *

def convert_logging_level(level):
    """ Convert the log level received to one of the loogging module. "
    
    Keyword arguments:
    level -- Level to convert.
    
    """
    
    try:
        logging_level = LOG_LEVELS[level]
    except KeyError as ke:
        # If no valid log level is indicated use the default level.
        logging_level = LOG_LEVELS[DEFAULT_LOG_LEVEL_NAME]
        
        print "No valid log level has been indicated using default level: " + \
                DEFAULT_LOG_LEVEL_NAME
    
    return logging_level

def init_log(progargs):
    """ Initializes the file log and messages format. 
    
    Keyword arguments:
    progargs - ProgramArguments object, it contains the information of all 
        program arguments received.
    
    """    
    
    # If no log level is indicated use the default level.
    if progargs.log_level_provided:
        logging_level = LOG_LEVELS[progargs.log_level]
    else:
        logging_level = LOG_LEVELS[DEFAULT_LOG_LEVEL_NAME]
    
    # If a file name has been provided as program argument use it.
    if progargs.log_file_provided:
        log_file = progargs.log_file_name
    else:
        log_file = DEFAULT_LOG_FILE_NAME
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=log_file, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging_level)
    
    logging.debug("Logging initialized.")

def main(progargs):
    """ Main function.

    A main function allows the easy calling from other modules and also from 
    the command line.
    
    This function performs all the steps needed to process the images.
    Each step is a calling to a function that implements a concrete task.

    """    
    
    # To check if the arguments received corresponds to any task.
    something_done = False    
    
    # Process program arguments.
    progargs.parse()           
        
    # Initializes logging.
    init_log(progargs)
        
    # This step organizes the images in directories depending on the type of image:
    # bias, flat or data.
    if progargs.organization_requested:
        logging.info("* Step 1 * Organizing image files in directories.")
        orgfits.organize_files(progargs)
        something_done = True
    else:
        logging.info("* Step 1 * Skipping organizing image files in " + \
                     "directories. Not requested.")
    
    # This step reduces the data images applying the bias and flats.
    if progargs.reduction_requested:
        logging.info("* Step 2 * Reducing images.") 
        reduce.reduce_images()
        something_done = True        
    else:
        logging.info("* Step 2 * Skipping reducing images. Not requested.")
    
    # This step find objects in the images. The result is a list of x,y and 
    # AR,DEC coordinates.
    if progargs.astrometry_requested:
        logging.info("* Step 3 * Performing astrometry.")
        astrometry.do_astrometry(progargs)
        something_done = True        
    else:
        logging.info("* Step 3 * Skipping performing astrometry. " + \
                     "Not requested.")
    
    # This step aligns the data images of the same object. This step is 
    # optional as the rest of steps could be performed with images not aligned.
    if progargs.align_requested:
        logging.info("* Step 4 * Performing alignment.")    
        align.align_images()
        something_done = True        
    else:
        logging.info("* Step 4 * Skipping performing alignment. Not requested.")
        
    # This step calculates the photometry of the objects detected doing the 
    # astrometry.
    if progargs.photometry_requested:
        logging.info("* Step 5 * Performing photometry.")     
        photometry.calculate_photometry(progargs)
        something_done = True        
    else:
        logging.info("* Step 5 * Skipping performing photometry. " + \
                     "Not requested.")
        
    # This step calculates the differental photometry of the objects detected 
    # doing the astrometry.        
    if progargs.diff_photometry_requested:
        logging.info("* Step 6 * Performing differential photometry.")     
        photometry.differential_photometry(progargs)
        something_done = True        
    else:
        logging.info("* Step 6 * Skipping differential magnitudes of " + \
                     "each object. Not requested.")          
                
    # This step process the magnitudes calculated for each object and 
    # generates a file that associate to each object all its measures.
    if progargs.magnitudes_requested:
        logging.info("* Step 7 * Processing magnitudes of each object.")     
        magnitude.calculate_magnitudes(progargs)
        something_done = True        
    else:
        logging.info("* Step 7 * Skipping processing magnitudes of each " + \
                     "object. Not requested.")     
        
    if not something_done:
        progargs.print_help()   

# Where all begins ...
if __name__ == "__main__":

    # Create object to process program arguments.
    progargs = yargparser.ProgramArguments()    
    
    # If no arguments are provided, show help and exit.
    if len(sys.argv) <= yargparser.ProgramArguments.MIN_NUM_ARGVS:
        print "The number of program arguments are not enough."        
        progargs.print_help()
        sys.exit(1)
    else: 
        sys.exit(main(progargs))