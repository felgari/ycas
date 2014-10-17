#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Felipe Gallego. All rights reserved.
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

import sys
import os
import glob
from pyraf import iraf
from pyraf.iraf import noao, digiphot, apphot

DATA_DIRECTORY = "data"
FIT_FILE_EXT = "fit"
CAT_FILE_EXT = "cat"
MAGNITUDE_FILE_EXT = "mag"
DATA_FINAL_SUFFIX = "_final"

def init_iraf():
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

def set_phot_pars():
    # Set photometry parameters.
    iraf.photpars.apertures = 14
    iraf.fitskypars.annulus = 25
    iraf.fitskypars.dannulus = 36
    iraf.fitskypars.salgorithm = "mode"
    iraf.centerpars.cbox = 0
    iraf.datapars.exposure = "EXPTIME"
    iraf.datapars.airmass = "AIRMASS"

def save_parameters():
    
    # Save parameters in files.
    iraf.centerpars.saveParList(filename='center.par')
    iraf.datapars.saveParList(filename='data.par')
    iraf.fitskypars.saveParList(filename='fitsky.par')
    iraf.photpars.saveParList(filename='phot.par')
    
def get_work_file_names(cat_file):  
    
    image_file_name = \
        cat_file.replace("." + CAT_FILE_EXT, DATA_FINAL_SUFFIX + "." + FIT_FILE_EXT)
    
    output_mag_file_name = \
        cat_file.replace("." + CAT_FILE_EXT, "." + MAGNITUDE_FILE_EXT)
    
    return image_file_name, output_mag_file_name  

def do_phot(image_file_name, catalog_file_name, output_mag_file_name):

    # If magnitude file exists, remove it to avoid error.
    if os.path.exists(output_mag_file_name):
        os.remove(output_mag_file_name)

    print "Calculating magnitudes for: " + image_file_name + \
        " in " + output_mag_file_name
        
    iraf.phot(image = image_file_name, 
                coords = catalog_file_name, 
                output = output_mag_file_name)

def do_photometry():    
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
                files = glob.glob(os.path.join(full_dir, "*." + CAT_FILE_EXT))
                print "Found " + str(len(files)) + " catalog files"
                
                for cat_file in files:
                    image_file_name, output_mag_file_name = \
                        get_work_file_names(cat_file)
                 
                    do_phot(image_file_name, cat_file, output_mag_file_name)           

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

    set_phot_pars()

    # Calculate the photometry.
    do_photometry()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())

