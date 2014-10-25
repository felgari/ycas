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
This module performs operations with the headers of FIT files.
"""

import sys
import os
import logging
import glob
import pyfits
from constants import *

NO_VALUE = "NO VALUE"

FIELD_SEP = ", "

FIT_HEADER_FIELDS = ["DATE-OBS", "OBJCTRA", "OBJCTDEC", "IMAGETYP", "FILTER", "AIRMASS"]

def summarize_fit_headers():
    """
    
    This function searches FIT files that correspond to data images and
    prints the values stored for a set of headers fields.
    
    """
    
    line = "FILENAME" + FIELD_SEP
    
    for i in range(len(FIT_HEADER_FIELDS)):
        line += FIT_HEADER_FIELDS[i]
        line += FIELD_SEP

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                logging.info("Found a directory for data: " + full_dir)

                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*" + DATA_FINAL_PATTERN))
                logging.info("Found " + str(len(files)) + " data files")
                
                for fl in files:

                    # Open FIT file.
                    hdulist = pyfits.open(fl)
                    
                    # Get header of first hdu, only one hdu is used.
                    header = hdulist[0].header
                    
                    line = fl + FIELD_SEP
                    
                    for i in range(len(FIT_HEADER_FIELDS)):
                        
                        try:
                            line += str(header[FIT_HEADER_FIELDS[i]])
                        except KeyError:
                            line += NO_VALUE
                            
                        line += FIELD_SEP
                    
                    hdulist.close()
                    
def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """
    
    # Print the values of a set of field headers for the data images found.
    summarize_fit_headers()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())