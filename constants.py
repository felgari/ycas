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

import os
import logging

# Log levels.
LOG_LEVELS = { "CRITICAL" : logging.CRITICAL,
              "ERROR": logging.ERROR,
              "WARNING": logging.WARNING,
              "INFO": logging.INFO,
              "DEBUG": logging.DEBUG }

DEFAULT_LOG_LEVEL_NAME = "WARNING"

DEFAULT_LOG_FILE_NAME = "ycas_log.txt"

# Directories.
BIAS_DIRECTORY = 'bias'
FLAT_DIRECTORY = 'flat'
DATA_DIRECTORY = 'data'

# File extensions.
FIT_FILE_EXT = "fit"
CATALOG_FILE_EXT = 'cat'
MAGNITUDE_FILE_EXT = "mag"
CSV_FILE_EXT = "csv"
TSV_FILE_EXT = "tsv"
RDLS_FILE_EXT = "rdls"
INDEX_FILE_PATTERN = '-indx.xyls'
DATA_FINAL_PATTERN = "_final.fit"
DATA_ALIGN_PATTERN = "_align.fit"

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
NORM_FILE_SUFFIX = "_norm"
DATA_FINAL_SUFFIX = "_final"

# External commands
ASTROMETRY_COMMAND = "solve-field"

# Default number of objects to look at when doing astrometry.
ASTROMETRY_NUM_OBJS = 20
# Overwrite previous files and limit the number of objects to look at"
ASTROMETRY_PARAMS = "--overwrite -d "

ASTROMETRY_WCS_TABLE_INDEX = 1

# Photometry paramters

# Multipliers to calculate some photometry parameters as multipliers 
# of the seeing value.
APERTURE_MULT = 2
ANNULUS_MULT = 4

DANNULUS_VALUE = 5
DATAMIN_VALUE = -0.001
DATAMAX_VALUE = 65536

TXDUMP_FIELDS = "id,xc,yc,otime,mag,merr"

# Parameters for the T150 CCD of the OSN.
# http://www.osn.iaa.es/content/CCDT150-Camera
OSN_CCD_T150_READNOISE = 8.23
OSN_CCD_T150_GAIN = 1.5
OSN_CCD_T150_DATAMAX = 65536