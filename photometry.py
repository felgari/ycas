#!/usr/bin/python
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
This module calculates the photometry of the objects detected previously
by means of astrometry in a set of data images.
The photometry values calculated are stored in a text file that contains
all the measures for the objects of an image.
"""

import sys
import os
import glob
from pyraf import iraf
from pyraf.iraf import noao, digiphot, apphot
from constants import *

FWHM = 5.5

def init_iraf():
    """
    
    This function initializes the pyraf environment.
    
    """
    
    # The display of graphics is not used, so skips Pyraf graphics 
    # initialization and run in terminal-only mode to avoid warning messages.
    os.environ['PYRAF_NO_DISPLAY'] = '1'

    # Set PyRAF process caching off to avoid errors if spawning multiple processes.
    iraf.prcacheOff()

    # Load iraf packages and does not show any output of the tasks.
    iraf.digiphot(_doprint = 0)
    iraf.apphot(_doprint = 0) 
    iraf.images(_doprint = 0)

    # Set the iraf.phot routine to scripting mode.
    iraf.phot.interactive = "no"
    iraf.phot.verify = "no"

def set_phot_pars(fwhm):
    """
    
    This function sets the pyraf parameters used to perform
    the photometry of images.
    
    """        
    
    # Set photometry parameters.
    iraf.photpars.apertures = APERTURE_MULT * fwhm
    iraf.fitskypars.annulus = ANNULUS_MULT * fwhm
    iraf.fitskypars.dannulus = DANNULUS_VALUE
    iraf.fitskypars.salgorithm = "mode"
    iraf.centerpars.cbox = 0
    iraf.centerpars.calgori = "centroid"
    
    # Name of the fields FITS that contains these values.
    iraf.datapars.exposure = "EXPOSURE"
    iraf.datapars.airmass = "AIRMASS"
    iraf.datapars.obstime = "MJD"
    iraf.datapars.readnoise = OSN_CCD_T150_READNOISE
    iraf.datapars.epadu = OSN_CCD_T150_GAIN
    iraf.datapars.datamax = OSN_CCD_T150_DATAMAX
    iraf.datapars.datamin = DATAMIN_VALUE

def save_parameters():
    """
    
    This function saves the parameters used to do the photometry.
    
    """    
    
    # Save parameters in files.
    iraf.centerpars.saveParList(filename='center.par')
    iraf.datapars.saveParList(filename='data.par')
    iraf.fitskypars.saveParList(filename='fitsky.par')
    iraf.photpars.saveParList(filename='phot.par') 

def do_phot(image_file_name, catalog_file_name, output_mag_file_name):
    """
    
    This function calculates the photometry of the images. 
    Receives the image to use, a catalog with the position of the objects
    contained in the image and the name of the output file.
    
    """
    
    # If magnitude file exists, remove it to avoid error.
    if os.path.exists(output_mag_file_name):
        os.remove(output_mag_file_name)

    print "Calculating magnitudes for: " + image_file_name + \
        " in " + output_mag_file_name
        
    try:
        iraf.phot(image = image_file_name, 
                    coords = catalog_file_name, 
                    output = output_mag_file_name)
    except iraf.IrafError as exc:
        print "Error executing phot on : " + image_file_name 
        print "Iraf error is: " + str(exc)

def do_photometry():   
    """
    
    This function walk the directories searching for catalog files
    that contains the x,y coordinates of the objects detected by the
    astrometry. 
    For each catalog the corresponding data image is located and passes
    along with the catalog to a function that calculates the photometry
    of the objects in the catalog file.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of catalog files.
                catalog_files = glob.glob(os.path.join(full_dir, "*." + CATALOG_FILE_EXT))
                print "Found " + str(len(catalog_files)) + " catalog files"
                
                # Each catalog indicates one or more images.
                for cat_file in catalog_files:
                    
                    # The images used are the aligned ones with a name that matches
                    # the name of the catalog, so the catalog references are valid
                    # for all these images.
                    object_name = cat_file[0:cat_file.find(DATANAME_CHAR_SEP)]
                     
                    image_file_pattern = object_name + "*" + DATA_FINAL_PATTERN
                    
                    images_of_catalog = glob.glob(image_file_pattern)
                        
                    print "Found " + str(len(images_of_catalog)) + " images for this catalog."
                        
                    # Calculate the magnitudes for each image related to the catalog.
                    for image in images_of_catalog:
                            
                        output_mag_file_name = \
                            image.replace(DATA_FINAL_PATTERN, 
                                                "." + MAGNITUDE_FILE_EXT)
                     
                        do_phot(image, cat_file, output_mag_file_name)    
                    
def txdump_photometry_info():
    """
    
    This function search files containing the results of photometry
    and using txdump extracts the coordinates and photometric measure
    to save it to a text file.
    
    """
    
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        
        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep) 
            
            # Check if current directory is for data images.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of magnitude files.
                mag_files = glob.glob(os.path.join(full_dir, "*." + MAGNITUDE_FILE_EXT))
                print "Found " + str(len(mag_files)) + " magnitude files"    
                
                # Reduce each data file one by one.
                for mfile in mag_files:                  
    
                    # Get the name of the file where the magnitude data will be saved.
                    mag_dest_file_name = \
                        mfile.replace("." + MAGNITUDE_FILE_EXT, \
                                      MAGNITUDE_FILE_EXT + "." + CSV_FILE_EXT)
                    
                    # Remove the destiny file if exists.
                    if os.path.exists(mag_dest_file_name):
                        os.remove(mag_dest_file_name)
                    
                    mag_dest_file = open(mag_dest_file_name, 'w' )
                    
                    try:
                        iraf.txdump(mfile, fields=TXDUMP_FIELDS, expr='yes', Stdout=mag_dest_file)
                    except iraf.IrafError as exc:
                        print "Error executing txdump to get: " + mag_dest_file_name
                        print "Iraf error is: " + str(exc)
                        
                    mag_dest_file.close()
                           
def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv

    # Init iraf package.
    init_iraf()

    # Set the parameters for photometry.
    set_phot_pars(FWHM)

    # Calculate the photometry.
    do_photometry()
    
    # Export photometry info to a text file with only the columns needed.
    txdump_photometry_info()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())

