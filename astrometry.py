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
import pyfits
import subprocess32 as subprocess
import constants

def write_xy_catalog(table_file_name, catalogue_file_name):

    # Check if the file containing x,y coordinates exists.
    if os.path.exists(table_file_name):

        print "X,Y coordinates file exists"
        print "Table file name: " + table_file_name
        print "Catalog file name: " + catalogue_file_name

        # Open the FITS file received.
        f = pyfits.open(table_file_name) 

        # Assume the first extension is a table.
        tbdata = f[ASTROMETRY_WCS_TABLE_INDEX].data  

        # Write x,y coordinates to a text file.
        text_file = open(catalogue_file_name, "w")

        for i in range(len(tbdata)):
            text_file.write(str(tbdata[i][0]) + " " + str(tbdata[i][1]) + "\n")

        text_file.close()

    else:
        print "X,Y coordinates file does not exists so no catalog file is created."
        
def do_astrometry():
    print "Doing astrometry ..."

    number_of_images = 0
    number_of_successfull_images = 0

    # Walk from current directory.
    for path,dirs,files in os.walk('.'):

        # Inspect only directories without subdirectories.
        if len(dirs) == 0:
            split_path = path.split(os.sep)

            # Check if current directory is for data.
            if split_path[-2] == DATA_DIRECTORY:
                # Get the full path of the directory.                
                full_dir = path
                print "Found a directory for data: " + full_dir

                # Get the list of files ignoring hidden files.
                files_full_path = \
                    [fn for fn in glob.glob(os.path.join(full_dir, "*" + DATA_FINAL_PATTERN)) \
                    if not os.path.basename(fn).startswith('.')]
                print "Found " + str(len(files)) + " data files"

                # Get the list of unique data names.
                data_names = [ os.path.basename(f[0:f.find(DATANAME_CHAR_SEP)]) \
                                for f in files_full_path ]

                # Remove duplicates.
                unique_data_names = list(set(data_names))

                # The name of the directory that contains the imagen matches
                # the name of the filter.
                filter_name = split_path[-1]

                # Complete the name of all files.
                files_to_catalog = \
                    [ os.path.join(full_dir, udn + DATANAME_CHAR_SEP + FIRST_DATA_IMG + \
                        filter_name + DATA_FINAL_PATTERN) \
                        for udn in unique_data_names ]

                print "Files to catalog: " + str(files_to_catalog)

                # Get the astrometry for each file.
                for fl in files_to_catalog:

                    catalog_name = fl.replace(DATA_FINAL_PATTERN, "." + CATALOG_FILE_EXTENSION)

                    # Check if the catalog file already exists.
                    if os.path.exists(catalog_name) == False :

                        command = ASTROMETRY_COMMAND + " " + ASTROMETRY_PARAMS + " " + fl
                        print "Executing: " + command

                        # Executes astrometry.net to get the astrometry of the image.
                        return_code = subprocess.call(command, \
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        print "Execution return code: " + str(return_code)

                        number_of_images += 1

                        if return_code == 0:
                            number_of_successfull_images = number_of_successfull_images + 1

                            # From wcs file generates a text file with x,y values.
                            write_xy_catalog( \
                                fl.replace("." + FIT_FILE_EXT, INDEX_FILE_EXTENSION), \
                                catalog_name)
                    else:
                        print "Catalog file already exists: " + catalog_name

    print "Astrometry results:"
    print "- Number of images processed: " + str(number_of_images)
    print "- Images processed successfully: " + str(number_of_successfull_images)

def main(argv=None):
    """ main function.

    A main function allows the easy calling from other modules and also from the
    command line.

    Arguments:
    argv - List of arguments passed to the script.

    """

    if argv is None:
        argv = sys.argv

    # Calculate the x,y coordinates of each object in the data images.
    do_astrometry()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())

