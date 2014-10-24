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
This module calculates the magnitude of a group of objects performing
a sequence of steps.

The processing assumes certain values in the header of the fits images,
even in the names of the files. Also a list of objects of interest, 
whose magnitudes are calculated, and a list of standard stars.
Some characteristics of the CCD camera are also needed to calculate
the photometric magnitude of the objects.
"""

import sys
import orgfits
import reduce
import align
import astrometry
import photometry
import objmag

def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.
    
    This function performs all the steps needed to process the images.
    Each step is a calling to a function that implements a concrete task.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv
        
    # This step organizes the images in directories depending on the type of image:
    # bias, flat or data.
    print "* Step 1 * Organize image files in directories."
    orgfits.main()
    
    # This step reduces the data images applying the bias and flats.
    print "* Step 2 * Reduce images."    
    reduce.main()
    
    # This step find objects in the images. The result is a list of x,y and AR,DEC
    # coordinates.
    print "* Step 3 * Perform astrometry."    
    astrometry.main()
    
    # This step aligns the data images of the same object. This step is optional as
    # the rest of steps could be performed with images not aligned.
    print "* Step 4 * Perform alignment."    
    align.main()    
    
    # This step calculates the photometry of the objects detected doing the astrometry.
    print "* Step 5 * Perform photometry."     
    photometry.main()
    
    # This step process the magnitudes calculated for each object and generates a file
    # that associate to each object all its measures.
    print "* Step 6 * Process magnitudes of each object."     
    objmag.main()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())