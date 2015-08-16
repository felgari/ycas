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
import fitsheader
import textfiles
from constants import *

def get_pipeline_parameters(progargs):
    """Read the configuration parameters required by the pipeline.
    
    Args:
        progargs: Program arguments.
    
    """
    
    stars = None
    
    if progargs.file_of_stars_provided:        
        # Read the data of the stars of interest.
        stars = starsset.StarsSet(progargs.stars_file_name,
                                  progargs.synonym_file_name)  
    
    filters = orgfits.Filters(progargs.filters_file_name)
    
    # Read the names of the header fields used.
    cfg_header_fields = textfiles.read_cfg_file(progargs.header_params_file_name)
    
    header_fields = fitsheader.HeaderFields(cfg_header_fields)    
    
    return stars, filters, header_fields

def pipeline(progargs):
    """ Performs sequentially the steps of the pipeline that have been 
    requested.
    
    Args:
        progargs: Program arguments.    
        
    """
    
    # Magnitudes calculated.
    mag = None     
    
    stars, filters, header_fields = get_pipeline_parameters(progargs)
    
    # This step organizes the images in directories depending on the type of
    # image: bias, flat or data.
    if progargs.organization_requested or progargs.all_steps_requested:
        logging.info("* Step 1 * Organizing image files in directories.")
        orgfits.organize_files(progargs, stars, header_fields, filters)
        anything_done = True
    else:
        logging.info("* Step 1 * Skipping the organization of image files in directories. Not requested.")
    
    # This step reduces the data images applying the bias and flats.
    if progargs.reduction_requested or progargs.all_steps_requested:
        logging.info("* Step 2 * Reducing images.")
        reduction.reduce_images(progargs)
        anything_done = True
    else:
        logging.info("* Step 2 * Skipping the reduction of images. Not requested.")
        
    # This step find objects in the images. The result is a list of x,y and
    # AR,DEC coordinates.
    if progargs.astrometry_requested or progargs.all_steps_requested:
        logging.info("* Step 3 * Performing astrometry of the images.")
        astrometry.do_astrometry(progargs, stars, header_fields)
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
        mag = magnitude.process_magnitudes(stars, progargs.target_dir,
                                           progargs.light_directory)
        anything_done = True
    else:
        logging.info("* Step 5 * Skipping the calculation of magnitudes of stars. Not requested.")
        
    # This step process the magnitudes calculated for each object and
    # generates a light curves.
    if progargs.light_curves_requested or progargs.all_steps_requested:
        logging.info("* Step 6 * Generating light curves.")
        curves.generate_curves(stars, mag)
        anything_done = True
    else:
        logging.info("* Step 6 * Skipping the generation of light curves. Not requested.")        
        
    # Generates a summary if requested and some task has been indicated.
    if anything_done and progargs.summary_requested:
        summary.generate_summary(progargs, stars, mag)

def main(progargs):
    """ Main function.

    A main function allows the easy calling from other modules and also from 
    the command line.
    
    This function performs all the steps needed to process the images.
    Each step is a calling to a function that implements a concrete task.

    """        
    
    try:
        # Process program arguments checking that programs arguments used are
        # coherent.
        progargs.process_program_arguments()           
        
        # Initializes logging.
        logutil.init_log(progargs)
        
        # Perform the steps requested.
        pipeline(progargs)
        
    except yargparser.ProgramArgumentsException as pae:
        # To stdout, since logging has not been initialized.
        print pae
        
    except fitsheader.HeaderFieldsException as hfe:
        logging.error("Invalid header fields in file: %s" % 
                      progargs.header_params_file_name)        
  
    logging.info("Program finished.")

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