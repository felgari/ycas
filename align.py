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
from constants import *

def align_images():
    print "Aligning images ..."

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

                # Get the list of catalog files ignoring hidden files.
                files_full_path = \
                    [f for f in glob.glob(os.path.join(full_dir, "*." + CATALOG_FILE_EXTENSION)) \
                    if not os.path.basename(f).startswith('.')]
                print "Found " + str(len(files_full_path)) + " catalog files"
                
                # Get the list of unique catalog names.
                catalog_names = [ os.path.basename(f[0:f.find(DATANAME_CHAR_SEP)]) \
                                    for f in files_full_path ]

                print "Catalogos: " + str(catalog_names)

                # Align the images corresponding to each catalog.
                for cn in catalog_names:
                    data_images = \
                        [f for f in glob.glob(os.path.join(full_dir, \
                        cn + "*" + DATA_FINAL_PATTERN)) \
                        if not os.path.basename(f).startswith('.')]

                    if len(data_images) > 1:

                        # Sort the images by name.
                        data_images.sort()

                        reference_image = data_images[0]

                        align_images = \
                            [s.replace(DATA_FINAL_PATTERN, DATA_ALIGN_PATTERN) for s in data_images ]

                        catalog = reference_image.replace(DATA_FINAL_PATTERN, "." + CATALOG_FILE_EXTENSION)

                        print "- Catalog: " + catalog
                        print "- Data images: " + str(data_images)
                        print "- Reference image: " + reference_image
                        print "- Align files: " + str(align_images)

                        #pyraf.imalin(data_images, reference_image, catalog, align_images)
                    else:
                        print "Only 1 data image, alignment is not necessary."

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
    align_images()

# Where all begins ...
if __name__ == "__main__":

    sys.exit(main())

