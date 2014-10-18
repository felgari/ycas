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

# Directories.
BIAS_DIRECTORY = 'bias'
FLAT_DIRECTORY = 'flat'
DATA_DIRECTORY = 'data'

# File extensions.
DATA_FINAL_PATTERN = "_final.fit"
DATA_ALIGN_PATTERN = "_align.fit"
FILENAME_EXT = 'fit'
CATALOG_FILE_EXTENSION = 'cat'
INDEX_FILE_EXTENSION = '-indx.xyls'
FIT_FILE_EXT = "fit"
CAT_FILE_EXT = "cat"
MAGNITUDE_FILE_EXT = "mag"

# Directory paths.
PATH_FROM_FLAT_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_FLAT = os.path.join("..", "..", FLAT_DIRECTORY)

# Special characters in file names.
BIAS_STRING = 'bias'
FLAT_STRING = 'flat'
DATANAME_CHAR_SEP = "-"
FIRST_DATA_IMG = "001"
FILTERS = [ 'V', 'B', 'R', 'CN', 'Cont4430', 'Cont6840' ]

MASTERBIAS_FILENAME = "bias_avg.fit"
MASTERFLAT_FILENAME = "flat_avg.fit"
WORK_FILE_SUFFIX = "_work"
DATA_FINAL_SUFFIX = "_final"

# External commands
ASTROMETRY_COMMAND = "solve-field"

# Overwrite previous files and limit the number of objects to look at"
ASTROMETRY_PARAMS = "--overwrite -d 20"

ASTROMETRY_WCS_TABLE_INDEX = 1