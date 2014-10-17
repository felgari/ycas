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
import shutil

FILENAME_EXT = 'fit'
FILENAME_SEP = '-'
BIAS_STRING = 'bias'
FLAT_STRING = 'flat'
FILTERS = [ 'V', 'B', 'R', 'CN', 'Cont4430', 'Cont6840' ]

BIAS_DIRECTORY = 'bias'
FLAT_DIRECTORY = 'flat'
DATA_DIRECTORY = 'data'

def get_image_filter(filename):
    """ Returns the filter indicated in the filename if any. """

    filtername = ''

    filename_no_ext = filename[:-len('.' + FILENAME_EXT)]    

    for f in FILTERS:
        index = filename_no_ext.rfind(f)

        if index > 0:
            filtername = f
    
    return filtername    

def create_directory(path, dirname):
    """ Create a directory with the given name. """

    complete_dirname = os.path.join(path,dirname)

    # Check if the directory exists.
    if not os.path.exists(complete_dirname):
        try: 
            print "Creating directory: " + complete_dirname
            os.makedirs(complete_dirname)
        except OSError:
            if not os.path.isdir(complete_dirname):
                raise

def analyze_name(filename, path):
    """ The file name has the the form type-orderfilter.fit'.
        Where 'type' could be 'flat', 'bias' or a proper name.
        A '-' character separates the 'orderfilter' part that
        indicates the ordinal number of the image and optionally
        a filter, only bias has no filter. """

    file_source = os.path.join(path, filename)

    # If the file is a bias.
    if filename.startswith(BIAS_STRING):
        create_directory(path, BIAS_DIRECTORY)

        file_destination = os.path.join(path, BIAS_DIRECTORY, filename)

    # If the file is a flat.
    elif filename.startswith(FLAT_STRING):
        create_directory(path, FLAT_DIRECTORY)

        filtername = get_image_filter(filename)

        if len(filtername) > 0:
            create_directory(path, os.path.join(FLAT_DIRECTORY, filtername))

        file_destination = os.path.join(path, FLAT_DIRECTORY, filtername, filename)

    # Else the file is a data image.
    else:
        create_directory(path, DATA_DIRECTORY)

        filtername = get_image_filter(filename)

        if len(filtername) > 0:
            create_directory(path, os.path.join(DATA_DIRECTORY, filtername))

        file_destination = os.path.join(path, DATA_DIRECTORY, filtername, filename)

    print "Moving '" + file_source + "' to '" + file_destination + "'"

    shutil.move(os.path.abspath(file_source),
                os.path.abspath(file_destination))

def organize_files():
    # Walk from current directory.
    for path,dirs,files in os.walk('.'):
        # For each file move it to he proper directory.
        for fn in files:
            # The extension is the final string of the list 
            # without the initial dot.
            filext = os.path.splitext(fn)[-1][1:]

            if filext == FILENAME_EXT:
                # Analyze name.
                print "Analyzing: " + os.path.join(path, fn)
                analyze_name(fn, path)
            else:
                print "Ignoring file: " + fn

def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv

    organize_files()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())

