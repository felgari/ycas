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

"""Calculates the magnitudes of stars from images in FIT format.

It is a pipeline, a process that performs a set of tasks in a given order. 
Each step of the sequence uses the results of the previous step to perform
its task.

This is the main module, read program arguments and executes the steps of the
pipeline. 

In a given execution is not necessary to perform all the steps of the pipeline
but the results of the previous steps must exists, this is, these results
have been calculated in a previous execution.

"""

import sys
import logging
import logutil
import yargparser
import starsset
import orgfits
import reduction
import astrometry
import photometry
import magnitude
import curves
import summary
from constants import * 

def pipeline(progargs):
    """ Performs sequentially those steps of the pipeline that have been 
    requested.
    
    Check each step to determine if it has been requested and if it is so, 
    the step is executed.
    
    Args:
        progargs: Program arguments.
        
    """
    
    # The list of stars.
    stars = None
    
    # Magnitudes calculated.
    mag = None
    
    # Read the data of the stars if a file for them has been provided.
    if progargs.file_of_stars_provided:        
        # Read the data of the stars of interest.
        stars = starsset.StarsSet(progargs.stars_file_name)        
    
    # This step organizes the images in directories depending on the type of
    # image: bias, flat or data.
    if progargs.organization_requested or progargs.all_steps_requested:
        logging.info("* Step 1 * Organizing image files in directories.")
        orgfits.organize_files(progargs)
        anything_done = True
    else:
        logging.info("* Step 1 * Skipping the organization of image files " + 
                     "in directories. Not requested.")
    
    # This step reduces the data images applying the bias and flats.
    if progargs.reduction_requested or progargs.all_steps_requested:
        logging.info("* Step 2 * Reducing images.")
        reduction.reduce_images(progargs)
        anything_done = True
    else:
        logging.info("* Step 2 * Skipping the reduction of images. " + 
                     "Not requested.")
        
    # This step find objects in the images. The result is a list of x,y and
    # AR,DEC coordinates.
    if progargs.astrometry_requested or progargs.all_steps_requested:
        logging.info("* Step 3 * Performing astrometry of the images.")
        astrometry.do_astrometry(progargs, stars)
        anything_done = True
    else:
        logging.info("* Step 3 * Skipping astrometry. Not requested.")

    # This step calculates the photometry of the objects detected doing the
    # astrometry.
    if progargs.photometry_requested or progargs.all_steps_requested:
        logging.info("* Step 4 * Performing photometry of the stars.")
        photometry.calculate_photometry(progargs)
        anything_done = True
    else:
        logging.info("* Step 4 * Skipping photometry. Not requested.")
        
    # This step process the magnitudes calculated for each object and
    # generates a file that associate to each object all its measures.
    if progargs.magnitudes_requested or progargs.all_steps_requested:
        logging.info("* Step 5 * Calculating magnitudes of stars.")
        mag = magnitude.process_magnitudes(stars, progargs.data_directory)
        anything_done = True
    else:
        logging.info("* Step 5 * Skipping the calculation of magnitudes of stars. Not requested.")
        
    # This step process the magnitudes calculated for each object and
    # generates light curves.
    if progargs.light_curves_requested or progargs.all_steps_requested:
        logging.info("* Step 6 * Generating light curves.")
        curves.generate_curves(stars, mag)
        anything_done = True
    else:
        logging.info("* Step 6 * Skipping the generation of light curves. Not requested.")        
        
    # Generates a summary with the results of the steps performed.
    if anything_done and progargs.summary_requested:
        summary.generate_summary(progargs, stars, mag)

def main(progargs):
    """A main function allows the easy calling from other modules and also from 
    the command line.
    
    This function process program arguments, initializes log and executes
    the pipeline.
    
    Args:
        progargs: Program arguments.

    """    
    
    try:
        # Process program arguments and check that programs arguments are used
        # coherently.
        progargs.process_program_arguments()           
        
        # Initializes logging.
        logutil.init_log(progargs)
        
        # Perform the steps of the pipeline.
        pipeline(progargs)
        
    except yargparser.ProgramArgumentsException as pae:
        # To stdout, since logging has not been initialized.
        print pae
    except Exception as e:
        # To catch any other Exception.
        print e.__doc__
        print e.message       
  

# Where all begins ...
if __name__ == "__main__":

    # Create object to process the program arguments.
    progargs = yargparser.ProgramArguments()    
    
    # Check the number of arguments received.
    if len(sys.argv) <= progargs.min_number_args:
        
        # If no arguments are provided show help and exit.
        print "The number of program arguments are not enough."   
             
        progargs.print_help()
        
        sys.exit(1)
        
    else: 
        # Number of arguments is fine, execute main function.
        sys.exit(main(progargs))