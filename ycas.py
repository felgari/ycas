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

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv
        
    # Perform all the steps to get the photometry of fit images that
    # are found from the directory where this program is launched.
    print "* Step 1 * Organize image files in directories."
    orgfits.main()
    
    print "* Step 2 * Reduce images."    
    reduce.main()
    
    print "* Step 3 * Perform astrometry."    
    astrometry.main()
    
    print "* Step 4 * Perform alignment."    
    align.main()    
    
    print "* Step 5 * Perform photometry."     
    photometry.main()
    
    print "* Step 6 * Process magnitudes of each object."     
    objmag.main()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())