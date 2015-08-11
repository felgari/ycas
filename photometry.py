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

"""This module calculates the photometry.

This module calculates the photometry of the objects detected previously
by the astrometry in the data images.
The photometry values calculated are stored in a text file that contains
all the measures for the objects of an image.
"""

import sys
import os
import glob
import astromatics
from pyraf import iraf
from pyraf.iraf import noao, digiphot, apphot
from constants import *
from textfiles import *
from fitfiles import *
from images import *
from photpars import *

phot_progargs = None

TXDUMP_FIELDS = "id,xc,yc,otime,mag,xairmass,merr"
    
def init_iraf():
    """Initializes the pyraf environment. """
    
    # The display of graphics is not used, so skips Pyraf graphics 
    # initialization and run in terminal-only mode to avoid warning messages.
    os.environ['PYRAF_NO_DISPLAY'] = '1'

    # Set PyRAF process caching off to avoid errors if spawning multiple 
    # processes.
    iraf.prcacheOff()

    # Load iraf packages and does not show any output of the tasks.
    iraf.digiphot(_doprint = 0)
    iraf.apphot(_doprint = 0) 
    iraf.images(_doprint = 0)

    # Set the iraf.phot routine to scripting mode.
    iraf.phot.interactive = "no"
    iraf.phot.verify = "no"
    
def set_common_phot_pars(phot_params):
    """Sets the pyraf parameters used to in photometry common to all the images.
    
    Args:
        phot_params: Parameters for phot.
            
    """        
    
    # Set photometry parameters.
    iraf.fitskypars.dannulus = phot_params.dannulus
    iraf.fitskypars.skyvalue = phot_params.sky
    iraf.fitskypars.salgorithm = phot_params.salgorithm
    iraf.centerpars.cbox = phot_params.cbox
    iraf.centerpars.calgori = phot_params.calgori
    
    # Name of the fields FITS that contains these values.
    iraf.datapars.exposure = "EXPOSURE"
    iraf.datapars.airmass = "AIRMASS"
    iraf.datapars.obstime = "MJD"

    
    iraf.datapars.readnoise = phot_params.readnoise
    iraf.datapars.epadu = phot_params.epadu
    iraf.datapars.datamax = phot_params.datamax 

def set_image_specific_phot_pars(fwhm, phot_params):
    """Sets the pyraf parameters in photometry that changes for each image.
    
    Args: 
        fwhm: FWHM value.
        phot_params: Parameters for phot.
    
    """       
    
    # Set photometry parameters.
    iraf.datapars.fwhmpsf = fwhm
    iraf.photpars.apertures = fwhm * phot_params.aperture
    iraf.fitskypars.annulus = fwhm * phot_params.annulus_mult
    
    # Name of the fields FITS that contains these values.
    iraf.datapars.datamin = phot_params.datamin

def save_parameters():
    """Saves the parameters used to do the photometry. """    
    
    # Save parameters in files.
    iraf.centerpars.saveParList(filename='center.par')
    iraf.datapars.saveParList(filename='data.par')
    iraf.fitskypars.saveParList(filename='fitsky.par')
    iraf.photpars.saveParList(filename='phot.par') 


def calculate_datamin(image_file_name, phot_params):
    """ Calculate a datamin value for the image received using imstat. 
    
    Args: 
        image_file_name: Name of the file with the image.
        phot_params: Parameters for phot.
    
    """
    
    # Set a default value for datamin.
    datamin = phot_params.datamin
    
    try:
        imstat_output = iraf.imstat(image_file_name, fields='mean,stddev', \
                                    Stdout=1)
        imstat_values = imstat_output[IMSTAT_FIRST_VALUE]
        values = imstat_values.split()
        
        # Set a calculated value for datamin.
        datamin = float(values[0]) - phot_params.datamin_mult * float(values[1])
        
    except iraf.IrafError as exc:
        logging.error("Error executing imstat: Stats for data image: %s" %
                      (image_file_name))
        logging.error("Iraf error is: %s" % (exc))
        
    except ValueError as ve:
        logging.error("Value Error calculating datamin for image: %s" %
                      (image_file_name))
        logging.error("mean is: %s stddev is: %s" % (values[0], values[1]))
        logging.error("Value Error is: %s" % (ve))
        
    if datamin < phot_params.datamin:
        datamin = phot_params.datamin
        
    return datamin

def do_phot(image_file_name, catalog_file_name, output_mag_file_name, 
            sextractor_cfg_path, phot_params):
    """Calculates the photometry of the images.
    
    Receives the image to use, a catalog with the position of the objects
    contained in the image and the name of the output file.
    
    Args:     
        image_file_name: Name of the file with the image. 
        catalog_file_name: File with the X, Y coordinates to do phot.
        output_mag_file_name: Name of the output file with the magnitudes.
        sextractor_cfg_path: Path to the sextractor configuration files.
        phot_params: Parameters for phot.
    
    """
    
    # If magnitude file exists, remove it to avoid error.
    if os.path.exists(output_mag_file_name):
        os.remove(output_mag_file_name)

    logging.debug("Calculating magnitudes for: %s in %s" %
                  (image_file_name, output_mag_file_name))
    
    # Calculate datamin for this image.   
    datamin = calculate_datamin(image_file_name, phot_params)                         
           
    # Calculate FWHM for this image.
    fwhm = astromatics.get_fwhm(sextractor_cfg_path, image_file_name)
           
    # Set the parameters for the photometry that depends on the image.
    set_image_specific_phot_pars(fwhm, phot_params)                
                
    try:           
        iraf.phot(image = image_file_name, 
                    coords = catalog_file_name, 
                    output = output_mag_file_name)
    except iraf.IrafError as exc:
        logging.error("Error executing phot on : %s" % (image_file_name)) 
        logging.error( "Iraf error is: %s" % (exc))

def do_photometry(progargs, phot_params):   
    """Walk the directories searching for image to calculate its photometry.
    
    This function walk the directories searching for catalog files
    that contains the x,y coordinates of the objects detected by the
    astrometry. 
    For each catalog the corresponding data image is located and passes
    along with the catalog to a function that calculates the photometry
    of the objects in the catalog file.
    
    Args:     
        progargs: Program arguments. 
        phot_params: Photometry parameters.  
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk(progargs.target_dir):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == progargs.data_directory:
                logging.debug("Found a directory for data: %s" % (path))

                # Get the list of catalog files.
                catalog_files = glob.glob(os.path.join(path, "*.%s" %
                                                       (CATALOG_FILE_EXT)))
                
                logging.debug("Found %d catalog files" % (len(catalog_files)))
                
                # Each catalog corresponds to an image.
                for cat_file in catalog_files:
                    
                    image_file_name = cat_file.replace("." + CATALOG_FILE_EXT, 
                                                       DATA_FINAL_PATTERN)
                        
                    logging.debug("Found image %s for catalog %s" %
                                  (image_file_name, cat_file))
                        
                    # Calculate the magnitudes for the image related to the 
                    # catalog.        
                                        
                    # Get the name of the file for the magnitudes from 
                    # the FITS file.
                    output_mag_file_name = \
                        image_file_name.replace(FIT_FILE_EXT, \
                                                MAGNITUDE_FILE_EXT)
                 
                    # If magnitude file exists, skip.
                    if not os.path.exists(output_mag_file_name):
                        do_phot(image_file_name, cat_file,
                                output_mag_file_name,
                                progargs.sextractor_cfg_path,
                                phot_params)  
                    else:
                        logging.debug("Skipping phot for: %s, already done." %
                                      (output_mag_file_name))
                    
def txdump_photometry_info(target_dir, data_dir_name):
    """Extract the results of photometry from files to save them to a text file.
    
    This function search files containing the results of photometry
    and using txdump extracts the coordinates and photometric measure
    to save it to a text file. 
    
    Args:    
        target_dir: Directory that contains the files to process.
        data_dir_name: Name for the directories with data.    
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk(target_dir):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == data_dir_name:
                logging.debug("Found a directory for data: %s" % (path))

                # Get the list of magnitude files.
                mag_files = glob.glob(os.path.join(path, "*.%s" %
                                                   MAGNITUDE_FILE_EXT))
                
                logging.debug("Found %d magnitude files" % (len(mag_files)))    
                
                # Reduce each data file one by one.
                for mfile in mag_files:                  
    
                    # Get the name of the file where the magnitude data will 
                    # be saved.
                    mag_dest_file_name = \
                        mfile.replace(".%s" %(MAGNITUDE_FILE_EXT), 
                                      "%s%s.%s" %
                                      (FILE_NAME_PARTS_DELIM,
                                      MAGNITUDE_FILE_EXT, CSV_FILE_EXT))
                    
                    # Remove the destiny file if exists.
                    if os.path.exists(mag_dest_file_name):
                        os.remove(mag_dest_file_name)
                        
                    try:                                            
                        mag_dest_file = open(mag_dest_file_name, 'w' )
                    
                        iraf.txdump(mfile, fields=TXDUMP_FIELDS, expr='yes', \
                                    Stdout=mag_dest_file)
                        
                        mag_dest_file.close()
                        
                    except iraf.IrafError as exc:
                        logging.error("Error executing txdump to get: %s" %
                                      (mag_dest_file_name))
                        logging.error("Iraf error is: %s" % (exc)) 
                        
                    except IOError as ioe:
                        logging.error("Reading file: %s" % (mag_dest_file_name))                                           
                           
def calculate_photometry(progargs):
    """Calculates the photometry for all the data images found.
    
    Args:    
       progargs: Program arguments.
       
    """

    # Init iraf package.
    init_iraf()
    
    # Get the paramters for the protometry.
    try:
        phot_params = PhotParameters(progargs.phot_params_file_name,
                                     progargs.intrument_file_name)
        
        # Set photometry parameters that do not depend on each image.
        set_common_phot_pars(phot_params)
    
        # Calculate the photometry.
        do_photometry(progargs, phot_params)
        
        # Export photometry info to a text file with only the columns needed.
        txdump_photometry_info(progargs.target_dir, progargs.data_directory)        
    except PhotParamNotFound as ppnf:
        logging.error(ppnf)
        
    except PhotParamFileError as ppfe:
        logging.error(ppfe)