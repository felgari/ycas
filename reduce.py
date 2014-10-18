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
from constants import *

LIST_OF_FILES_MAX_LENGTH = 20

def do_masterbias():
    print "Doing masterbias ..."

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Check if current directory is for bias fits.
        for dr in dirs:

            if dr == BIAS_DIRECTORY:

                # Get the full path of the directory.                
                full_dir = os.path.join(path, dr)
                print "Found a directory for 'bias': " + full_dir

                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*." + FILENAME_EXT))
                print "Found " + str(len(files)) + " bias files"

                # Put the files list in a string.
                list_of_files = str(files).translate(None, "[]\'")

                masterbias_name = os.path.join(full_dir, MASTERBIAS_FILENAME) 

                # Getting statistics for bias files.
                means = iraf.imstat(list_of_files, fields='mean', Stdout=1)
                means = means[1:]
                mean_strings = [str(m).translate(None, ",\ ") for m in means]
                mean_values = [float(m) for m in mean_strings]                

                print "Bias images - Max. mean: " + str(max(mean_values)) + " Min. mean: " + str(min(mean_values))

                print "Creating bias file: " + masterbias_name

                # Combine all the bias files.
                iraf.imcombine(list_of_files, masterbias_name, Stdout=1)

def do_masterflat():
    print "Doing masterflat ..."

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Process only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == FLAT_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for 'flat': " + full_dir

                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*." + FILENAME_EXT))
                print "Found " + str(len(files)) + " flat files"

                # Put the files list in a string.
                list_of_flat_files = str(files).translate(None, "[]\'")

                # Create list of names of the work flat files.
                work_files = \
                    [s.replace("." + FILENAME_EXT, WORK_FILE_SUFFIX + "." + FILENAME_EXT) for s in files ]

                list_of_work_flat_files = str(work_files).translate(None, "[]\'")

                masterbias_name = os.path.join(full_dir, PATH_FROM_FLAT_TO_BIAS, MASTERBIAS_FILENAME)

                # Create the work files substracting bias from flat.
                iraf.imarith(list_of_flat_files, '-', masterbias_name, list_of_work_flat_files)

                # Combine all the flat files.
                masterflat_name = os.path.join(full_dir, MASTERFLAT_FILENAME) 

                iraf.imcombine(list_of_work_flat_files, masterflat_name, Stdout=1)

def reduce_data():
    print "Reducing data ..."

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for flats.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of files.
                files = glob.glob(os.path.join(full_dir, "*." + FILENAME_EXT))
                print "Found " + str(len(files)) + " data files"

                # If the list is too long the operation fails, so process only a limited
                # number of files.
                i = 0
                while i < len(files):
                    j = i + LIST_OF_FILES_MAX_LENGTH

                    files_subset = files[i:j]

                    print "Processing files from " + str(i) + " to " + str(min(j - 1, len(files)))

                    # Increment count.
                    i = j

                    # Put the files list in a string.
                    list_of_data_files = str(files_subset).translate(None, "[]\'")

                    # Create list of names of the work flat files.
                    work_files = \
                        [s.replace("." + FILENAME_EXT, WORK_FILE_SUFFIX + "." + FILENAME_EXT) for s in files_subset ]

                    list_of_work_data_files = str(work_files).translate(None, "[]\'")

                    # The masterbias file name.
                    masterbias_name = os.path.join(full_dir, PATH_FROM_DATA_TO_BIAS, MASTERBIAS_FILENAME)

                    # Create the work files substracting bias from flat.
                    iraf.imarith(list_of_data_files, '-', masterbias_name, list_of_work_data_files)

                    # Create list of names of the final flat files.
                    final_files = \
                        [s.replace("." + FILENAME_EXT, DATA_FINAL_SUFFIX + "." + FILENAME_EXT) for s in files_subset ]

                    list_of_final_data_files = str(final_files).translate(None, "[]\'")

                    # Get the path+name of the flat file.
                    path,dir_name=os.path.split(full_dir)
                    masterflat_name = os.path.join(full_dir, PATH_FROM_DATA_TO_FLAT, dir_name, MASTERFLAT_FILENAME)

                    # Create the final data dividing by master flat.
                    iraf.imarith(list_of_work_data_files, '/', masterflat_name, list_of_final_data_files)

def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv

    # Load the images package and does not show any output of the tasks.
    iraf.images(_doprint=0)

    do_masterbias()

    do_masterflat()

    reduce_data()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())
